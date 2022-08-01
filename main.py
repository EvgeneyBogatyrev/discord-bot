import discord
from discord.ext import commands
import os
import json
import codecs
import math
import asyncio
from random import randint

from constants import Constants

bot = commands.Bot(command_prefix='/')


STATUS = "NONE"
EDITING_PAIRS = False

def adjust_rating(user1, user2, win):
    rating1 = get_rating(user1, ment=True)
    rating2 = get_rating(user2, ment=True)

    win_chance1 = 1 / (1 + 10 ** ((rating2 - rating1) / Constants.ELO_DIFF))
    win_chance2 = 1 / (1 + 10 ** ((rating1 - rating2) / Constants.ELO_DIFF))

    diff1 = int((int(win) - win_chance1) * Constants.ELO_STEP)
    diff2 = int((int(not win) - win_chance2) * Constants.ELO_STEP)

    if win and diff1 == 0:
        diff1 = 1
    if win and diff2 == 0:
        diff2 = -1
    if not win and diff1 == 0:
        diff1 = -1
    if not win and diff2 == 0:
        diff2 = 1

    update_rating(user1, rating1 + diff1, ment=True)
    update_rating(user2, rating2 + diff2, ment=True)

    return diff1, diff2


def format_to_allowed(line):
    new_line = ""
    for c in line:
        if c in Constants.letters_match.keys():
            new_line += Constants.letters_match[c]
            continue
        if c not in Constants.allowed_letters:
            continue
        new_line += c
    return new_line


def read_status():
    global STATUS
    if not os.path.exists("data/status.txt"):
        STATUS = "NONE"
        return
    with open("data/status.txt", "r") as f:
        STATUS = f.readline()


def check_class(class_name):
    class_name = class_name.strip().lower()
    with open("data/patapons.txt", "r") as f:
        lines = list(f.readlines())
    for i in range(len(lines)):
        lines[i] = lines[i].strip().lower()
    if class_name not in lines:
        return False
    return True


def get_rating(name, ment=False):
    if not ment:
        with codecs.open("data/rating.csv", "r", 'utf-8') as f:
            lines = f.readlines()
        for line in lines:
            words = list(line.split(","))
            if words[0] == name.mention:
                return int(words[2])
        return -1
    else:
        with codecs.open("data/rating.csv", "r", 'utf-8') as f:
            lines = f.readlines()
        for line in lines:
            words = list(line.split(","))
            if words[0] == name:
                return int(words[2])
        return -1


def update_rating(name, rating, ment=False):
    if not ment:
        with codecs.open("data/rating.csv", "r", 'utf-8') as f:
            lines = f.readlines()
        data = {}
        for line in lines:
            words = list(line.split(","))
            data[(words[0], words[1])] = int(words[2][:-1])
            if words[0] == name.mention:
                data[(words[0], words[1])] = rating
        else:
            data[(name.mention, format_to_allowed(name.name))] = rating
    else:
        with codecs.open("data/rating.csv", "r", 'utf-8') as f:
            lines = f.readlines()
        data = {}
        for line in lines:
            words = list(line.split(","))
            data[(words[0], words[1])] = int(words[2][:-1])
            if words[0] == name:
                data[(words[0], words[1])] = rating

    new_lines = ""
    for key in data:
        new_lines += key[0] + "," + key[1] + "," + str(data[key]) + "\n"

    with open("data/rating.csv", "w") as f:
        f.write(new_lines)


@commands.has_permissions(administrator=True)
@bot.command()
async def lose(ctx, message):
    with open("data/points.json", "r") as f:
        data = json.load(f)
    for i in range(len(data["participants"])):
        if data["participants"][i] == message:
            data["points"][i] -= Constants.POINTS_FOR_WIN
            break
    with open("data/points.json", "w") as f:
        json.dump(data, f)

@commands.has_permissions(administrator=True)
@bot.command()
async def win(ctx, message):
    with open("data/points.json", "r") as f:
        data = json.load(f)
    for i in range(len(data["participants"])):
        if data["participants"][i] == message:
            data["points"][i] += Constants.POINTS_FOR_WIN
            break
    with open("data/points.json", "w") as f:
        json.dump(data, f)


async def end_current_tournament(ctx):
    line = "The tournament has ended.\nThe results are the following:\n\n"
    
    with open("data/points.json", "r") as f:
        part_points = json.load(f)

    part_points["participants"] = [x for _, x in sorted(zip(part_points["points"], part_points["participants"]), reverse=True)]
    part_points["points"] = [x for x, _ in sorted(zip(part_points["points"], part_points["participants"]), reverse=True)]

    for i in range(len(part_points["participants"])):
        line += f"{i + 1}) " + part_points["participants"][i]
        line += " - "
        line += str(part_points["points"][i]) + "\n"

    status = "NONE"
    with open("data/status.txt", "w") as f:
        f.write(status)

    await ctx.reply(line)


async def start_next_round(ctx, increment=True, no_sort=False):
    with open("data/round_n.txt", "r") as f:
        n = f.readline()

    with open("data/max_rounds.txt", "r") as f:
        max_num = f.readline()

    with open("data/points.json", "r") as f:
        part_points = json.load(f)
    
    if not no_sort:
        part_points["participants"] = [x for _, x in sorted(zip(part_points["points"], part_points["participants"]), reverse=True)]
        part_points["points"] = [x for x, _ in sorted(zip(part_points["points"], part_points["participants"]), reverse=True)]

    if len(part_points["participants"]) % 2 == 1:
        with open("data/outsiders.json", "r") as f:
            outsiders = json.load(f)

        i = len(part_points["participants"]) - 1
        while part_points["participants"][i] in outsiders:
            i -= 1
            if i < 0:
                i = len(part_points["participants"]) - 1
                break
        man = part_points["participants"].pop(i)
        score_of_man = part_points["points"].pop(i)
        part_points["participants"].append(man)
        part_points["points"].append(score_of_man)

        outsiders.append(man)

        with open("data/outsiders.json", "w") as f:
            json.dump(outsiders, f)

    def check_cringe(array):
        with open("data/played_pairs.json", "r") as f:
            played_pairs = json.load(f)
        for i in range(len(array) // 2):
            cur = [array[2 * i], array[2 * i + 1]]
            if cur in played_pairs or [cur[1], cur[0]] in played_pairs:
                return 2 * i
        return -1

    counter = 0
    while True:
        counter += 1
        if counter > 1000:
            with open("data/played_pairs.json", "w") as f:
                json.dump([], f)

        if len(part_points["participants"]) % 2 == 1:
            number = check_cringe(part_points["participants"][:-1])
        else:
            number = check_cringe(part_points["participants"])
        if number == -1:
            break

        man = part_points["participants"].pop(number)
        his_points = part_points["points"].pop(number)

        random_place = randint(0, len(part_points["participants"]) - 1)
        part_points["participants"].insert(random_place, man)
        part_points["points"].insert(random_place, his_points)

        print("cringe iteration")


    if max_num == n:
        await end_current_tournament(ctx)
        return

    if increment: 
        n = int(n) + 1
    with open("data/round_n.txt", "w") as f:
        f.write(str(n))

    participants = part_points["participants"]

    with open("data/points.json", "w") as f:
        json.dump(part_points, f)

    with open("data/current_tournament.json", "r") as f:
        part_data = json.load(f)

    unresolved = []

    line = f"ROUND {n}:\n\n\n"


    for i in range(len(participants) // 2):
        pair = (participants[2 * i], participants[2 * i + 1])
        unresolved.append(pair)
        
        with open("data/played_pairs.json", "r") as f:
            played_pairs = json.load(f)
        played_pairs.append(pair)
        with open("data/played_pairs.json", "w") as f:
            json.dump(played_pairs, f)

        line += f"{participants[2 * i]}\n1) {part_data['classes'][participants[2 * i]][0]}\n2) {part_data['classes'][participants[2 * i]][1]}\n3) {part_data['classes'][participants[2 * i]][2]}\n"
        line += "\nVS\n\n"
        line += f"{participants[2 * i + 1]}\n1) {part_data['classes'][participants[2 * i + 1]][0]}\n2) {part_data['classes'][participants[2 * i + 1]][1]}\n3) {part_data['classes'][participants[2 * i + 1]][2]}\n"
        line += "\n\n\n"

        

    if len(participants) % 2 == 1:
        line += f"{participants[-1]}, you skip this round (auto win)\n"
        for i in range(len(part_points["participants"])):
            if part_points["participants"][i] == participants[-1]:
                part_points["points"][i] += Constants.POINTS_FOR_WIN

    with open("data/points.json", "w") as f:
        json.dump(part_points, f)

    await ctx.send(line)

    with open("data/pairs.json", "w") as f:
        json.dump(unresolved, f)


@commands.has_permissions(administrator=True)
@bot.command() 
async def restart_round(ctx):
    await start_next_round(ctx, increment=False)


@bot.command()
async def drop(ctx):
    global STATUS

    with open("data/status.txt", "r") as f:
        STATUS = f.readline()

    if STATUS == "NONE":
        await ctx.reply("There is no tournament right now.")
        return

    elif STATUS == "REGISTR":
        with open("data/current_tournament.json", "r") as f:
            data = json.load(f)
        data["participants"].remove(ctx.author.mention)
        classes = data["classes"][ctx.author.mention]
        del data["classes"][ctx.author.mention]

        with open("data/current_tournament.json", "w") as f:
            json.dump(data, f)

        with open("data/metagame.json", "r") as f:
            meta_data = json.load(f)
        for cl in classes:
            meta_data[cl] -= 1
        with open("data/metagame.json", "w") as f:
            json.dump(meta_data, f)

        await ctx.reply(f"{ctx.author.mention} canceled their registration.")
        return

    else:
        with open("data/current_tournament.json", "r") as f:
            data = json.load(f)
        data["participants"].remove(ctx.author.mention)
        del data["classes"][ctx.author.mention]

        with open("data/current_tournament.json", "w") as f:
            json.dump(data, f)

        with open("data/points.json", "r") as f:
            points_data = json.load(f)

        for i in range(len(points_data["participants"])):
            if points_data["participants"][i] == ctx.author.mention:
                del points_data["points"][i]
                del points_data["participants"][i]
                break

        with open("data/pairs.json", "r") as f:
            data = json.load(f)

        opponent = None
        for pair in data:
            if ctx.author.mention in pair:
                opponent = pair[0]
                if opponent == ctx.author.mention:
                    opponent = pair[1]
                data.remove(pair)
                break

        with open("data/pairs.json", "w") as f:
            json.dump(data, f)
                        
        with open("data/points.json", "w") as f:
            json.dump(points_data, f)

        await ctx.send(f"{ctx.author.mention} dropped from the tournament. See you next time!")
        if opponent is not None:
            await confirm_game(ctx, ctx.author.mention, opponent, 0, 1)
            

@commands.has_permissions(administrator=True)
@bot.command()
async def drop_player(ctx, message):
    with open("data/current_tournament.json", "r") as f:
        data = json.load(f)
    data["participants"].remove(message)
    del data["classes"][message]

    with open("data/current_tournament.json", "w") as f:
        json.dump(data, f)

    with open("data/points.json", "r") as f:
        points_data = json.load(f)

    for i in range(len(points_data["participants"])):
        if points_data["participants"][i] == message:
            del points_data["points"][i]
            del points_data["participants"][i]
            break

    with open("data/pairs.json", "r") as f:
        data = json.load(f)

    opponent = None
    for pair in data:
        if message in pair:
            opponent = pair[0]
            if opponent == message:
                opponent = pair[1]
            data.remove(pair)
            break

    with open("data/pairs.json", "w") as f:
        json.dump(data, f)
                    
    with open("data/points.json", "w") as f:
        json.dump(points_data, f)

    await ctx.send(f"{message} was kicked from the tournament. See you next time!")
    if opponent is not None:
        await confirm_game(ctx, message, opponent, 0, 1)



@bot.command()
async def help_me(ctx):
    await ctx.reply(Constants.HELP)


@bot.command()
async def reg(ctx, *message):
    global STATUS

    if STATUS != "REGISTR":
        await ctx.reply("The registration has not started yet.\nAsk admins to start the registration.")
        return

    with open("data/current_tournament.json", 'r') as f:
        tour_data = json.load(f)
    if ctx.author.mention in tour_data["participants"]:
        await ctx.reply(f'You have already registred for this tournament.\nDrop and register again if you want to change classes.')
        return

    classes = list(message)
    if len(classes) != 3:
        await ctx.send(f'{ctx.author.mention}, format your input the following way:\n/reg Taterazay Yarida Yumiyacha')
        await ctx.message.delete(delay=5)
        return
    
    for i in range(len(classes)):
        classes[i] = classes[i].strip()

    bad_classes = []
    for patapon in classes:
        if not check_class(patapon):
            bad_classes.append(patapon)
    if len(bad_classes) != 0:
        line = f'{ctx.author.mention}, unknown classes: '
        for patapon in bad_classes:
            line += patapon + " "
        await ctx.send(line)
        await ctx.message.delete(delay=5)
        return
    
    for i in range(len(classes)):
        classes[i] = classes[i].strip().lower().capitalize()

    classes = list(set(classes))
    if len(classes) < 3:
        line = f'{ctx.author.mention}, please, select 3 different classes'
        await ctx.send(line)
        await ctx.message.delete(delay=5)
        return

    rating = get_rating(ctx.author)
    if rating == -1:
        rating = Constants.START_RATING
        update_rating(ctx.author, rating)

    reply = f"Success!\n{ctx.author.mention}\nRating: {rating}\n1) {classes[0]}\n2) {classes[1]}\n3) {classes[2]}"   

    tour_data["participants"].append(ctx.author.mention)
    tour_data["classes"][ctx.author.mention] = classes

    with open("data/current_tournament.json", "w") as f:
        json.dump(tour_data, f)

    #await ctx.reply(reply)
    #await ctx.channel.purge(limit=1)
    await ctx.message.delete(delay=5)
    await ctx.send(f"{ctx.author.mention} (Rating: {rating}) has successfully registred.")

    with open("data/metagame.json", "r") as f:
        meta_data = json.load(f)
    for cl in classes:
        meta_data[cl] += 1
    print(meta_data)
    with open("data/metagame.json", "w") as f:
        json.dump(meta_data, f)
    


@commands.has_permissions(administrator=True)
@bot.command() 
async def show_status(ctx):
    global STATUS
    if STATUS == "NONE":
        await ctx.reply("There is no tournament.")
        return
    with open("data/current_tournament.json", "r") as f:
        data = json.load(f)
    line = "TOURNAMENT:\n\n"
    for i, part in enumerate(data["classes"]):
        line += f"{i + 1}) {part}\n1. {data['classes'][part][0]}\n2. {data['classes'][part][1]}\n3. {data['classes'][part][2]}\n\n"
    await ctx.reply(line)

@bot.command()
async def leaderboard(ctx):
    with codecs.open("data/rating.csv", "r", 'utf-8') as f:
        lines = f.readlines()
    data = []
    longest_name = 4
    longest_rating = 6
    for line in lines:
        words = list(line[:-1].split(","))
        data.append((words[1], int(words[2])))
        if len(words[1]) > longest_name:
            longest_name = len(words[0])
        if len(words[2]) > longest_rating:
            longest_rating = len(words[1])
    
    def get_space(name, rating, base):
        return (base - len(rating)) * " "

    data = sorted(data, key=lambda x: x[1], reverse=True)
    line = "RATING" + get_space("NAME", "RATING", 20 + longest_rating) + "NAME\n"
    for elem in data:
        line += str(elem[1]) + get_space(elem[0], str(elem[1]), 20 + longest_rating) + elem[0] + "\n"
    await ctx.reply(line)


@commands.has_permissions(administrator=True)
@bot.command() 
async def start_reg(ctx):
    global STATUS
    STATUS = "REGISTR"
    with open("data/status.txt", "w") as f:
        f.write("REGISTR")
    with open(f"data/current_tournament.json", "w") as f:
        data = {"participants" : [], "classes" : {}}
        json.dump(data, f)
    await ctx.send("@everyone registration starts now.\nType /reg and write names of 3 classes you want to play.\n\
Example: /reg Taterazay Yarida Yumiyacha")

@commands.has_permissions(administrator=True)
@bot.command() 
async def start(ctx):
    global STATUS
    STATUS = "TOURN"
    with open("data/status.txt", "w") as f:
        f.write("TOURN")
    with open("data/outsiders.json", "w") as f:
        json.dump([], f)
    with open("data/played_pairs.json", "w") as f:
        json.dump([], f)
    with open("data/current_tournament.json", "r") as f:
        part_data = json.load(f)
    participants = sorted(part_data["participants"], key=lambda x: get_rating(x, ment=True), reverse=True)
    print(participants)
    part_points = {"participants" : participants, "points" : [0] * len(participants)}

    part_number_total = len(participants)
    log_num = int(math.log2(part_number_total))
    if 2 ** log_num != part_number_total:
        log_num += 1
    with open("data/max_rounds.txt", "w") as f:
        f.write(str(log_num))

    #await ctx.reply(" ".join(participants))

    with open("data/points.json", "w") as f:
        json.dump(part_points, f)

    with open("data/round_n.txt", "w") as f:
        f.write("0")

    await start_next_round(ctx, no_sort=True)


@bot.command() 
async def result(ctx, message):
    global EDITING_PAIRS
    if EDITING_PAIRS:
        await asyncio.sleep(5)
        await result(ctx, message)
        return

    global STATUS
    if STATUS != "TOURN":
        await ctx.reply("The tournament has not started yet.")
        return
        
    with open("data/await_confirmation.json", "r") as f:
        await_conf = json.load(f)

    for elem in await_conf:
        if ctx.author.mention in elem["players"]:
            await ctx.reply("!!! Your game's result has already been saved. Please, confirm or refute it. !!!")
            return

    with open("data/pairs.json", "r") as f:
        unresolved = json.load(f)

    for pair in unresolved:
        if ctx.author.mention in pair:
            break
    else:
        await ctx.reply(f"{ctx.author.mention}, you have no active games.")
        return
    
    if '-' not in message and ':' not in message:
        await ctx.reply(f"{ctx.author.mention}, correct format is <your wins>:<opponent's wins>.")
        return
    
    if '-' in message:
        res = list(message.split("-"))
    elif ":" in message:
        res = list(message.split(":"))
    if len(res) != 2 or res[0] not in "0123" or res[1] not in "0123" or int(res[0]) == int(res[1]):
        await ctx.reply(f"{ctx.author.mention}, correct format is <your wins>:<opponent's wins>.\nEach number has to be in range 0-3. One has to be higher than other.")
        return
    
    EDITING_PAIRS = True
    your_score = int(res[0])
    opponent_score = int(res[1])
    
    for pair in unresolved:
        if ctx.author.mention in pair:
            opponent = pair[0]
            if opponent == ctx.author.mention:
                opponent = pair[1]
            break

    await ctx.send(f"{opponent}, confirm that you won {opponent_score} and lost {your_score} games against \
{ctx.author.mention}.\nTo confirm type /confirm or just wait 2 minutes.\nTo refute type /refute.", delete_after=Constants.CONFIRM_SLEEP)

    with open("data/await_confirmation.json", "r") as f:
        await_conf = json.load(f)
    await_conf.append({"players" : [ctx.author.mention, opponent], 
        "score" : [your_score, opponent_score]})
    with open("data/await_confirmation.json", "w") as f:
        json.dump(await_conf, f)

    EDITING_PAIRS = False
    await asyncio.sleep(Constants.CONFIRM_SLEEP)
    await confirm(ctx, timeout=True)

@bot.command()
async def confirm(ctx, timeout=False):
    with open("data/await_confirmation.json", "r") as f:
        await_conf = json.load(f)
    
    if timeout:
        speciment = await_conf[0]
        if ctx.author.mention in speciment["players"]:
            score = speciment["score"]
            await_conf.remove(speciment)
            with open("data/await_confirmation.json", "w") as f:
                json.dump(await_conf, f)
            await confirm_game(ctx, speciment["players"][0], speciment["players"][1], score[0], score[1])
            return
    else:
        for speciment in await_conf:
            if ctx.author.mention in speciment["players"] and ctx.author.mention == speciment["players"][1]:
                score = speciment["score"]
                await_conf.remove(speciment)
                with open("data/await_confirmation.json", "w") as f:
                    json.dump(await_conf, f)
                await confirm_game(ctx, speciment["players"][0], speciment["players"][1], score[0], score[1])
                break
        else:
            await ctx.reply("You have no pending games.")

@bot.command()
async def refute(ctx):
    with open("data/await_confirmation.json", "r") as f:
        await_conf = json.load(f)
    for speciment in await_conf:
        if ctx.author.mention in speciment["players"]:
            await_conf.remove(speciment)
            with open("data/await_confirmation.json", "w") as f:
                json.dump(await_conf, f)
            players = speciment["players"]
            await ctx.send(f"{players[0]} VS {players[1]} - game results canceled.\nEnter correct results.")
            break
    else:
        await ctx.reply("You have no active games.")

async def confirm_game(ctx, player, opponent, your_score, opponent_score):  

    with open("data/pairs.json", "r") as f:
        unresolved = json.load(f)

    for pair in unresolved:
        if player in pair and opponent in pair:
            unresolved.remove(pair)

    with open("data/pairs.json", "w") as f:
        json.dump(unresolved, f)     

    with open("data/points.json", "r") as f:
        points_data = json.load(f)

    if your_score > opponent_score:
        for i in range(len(points_data["participants"])):
            if points_data["participants"][i] == player:
                points_data["points"][i] += 10 + your_score - opponent_score
            elif points_data["participants"][i] == opponent:
                points_data["points"][i] += opponent_score
    elif opponent_score > your_score:
        for i in range(len(points_data["participants"])):
            if points_data["participants"][i] == opponent:
                points_data["points"][i] += 10 + opponent_score - your_score
            elif points_data["participants"][i] == player:
                points_data["points"][i] += your_score

    with open("data/points.json", "w") as f:
        json.dump(points_data, f)

    diff1, diff2 = adjust_rating(player, opponent, your_score > opponent_score)

    if diff1 >= 0:
        diff1 = "+" + str(diff1)
    else:
        diff1 = str(diff1)
    
    if diff2 >= 0:
        diff2 = "+" + str(diff2)
    else:
        diff2 = str(diff2)

    await ctx.send(f"{player} VS {opponent}\nResult: {your_score}:{opponent_score}\n\
        \nRating changes:\n{player} : {get_rating(player, ment=True)} ({diff1})\n{opponent} : {get_rating(opponent, ment=True)} ({diff2})")

    if len(unresolved) == 0:
        await start_next_round(ctx)
        

@commands.has_permissions(administrator=True)
@bot.command() 
async def end_round(ctx):
    await start_next_round(ctx)


@commands.has_permissions(administrator=True)
@bot.command() 
async def end_tournament(ctx):
    await end_current_tournament(ctx)


@commands.has_permissions(administrator=True)
@bot.command() 
async def end_reg(ctx):
    global STATUS
    STATUS = "NONE"
    with open("data/status.txt", "w") as f:
        f.write("NONE")
    with open("data/current_tournament.json", "r") as f:
        data = json.load(f)
    line = "The registration has finished. Here are the participants:\n\n"
    for i, part in enumerate(data["classes"]):
        line += f"{i + 1}) {part}\n1. {data['classes'][part][0]}\n2. {data['classes'][part][1]}\n3. {data['classes'][part][2]}\n\n"
    await ctx.send(line)
    

@commands.has_permissions(administrator=True)
@bot.command() 
async def print_status(ctx):
    global STATUS
    print(STATUS)


@bot.command() 
async def metagame(ctx):
    with open("data/status.txt", "r") as f:
        STATUS = f.readline()
    if STATUS == "REGISTR":
        await ctx.reply("This command in blocked during the registration to prevent cheating.")
        return
    with open("data/metagame.json", "r") as f:
        meta_data = json.load(f)
    sort_data = {k: v for k, v in sorted(meta_data.items(), key=lambda item: item[1], reverse=True)}
    summ = 0
    for key in meta_data.keys():
        summ += meta_data[key]
    if summ == 0:
        await ctx.reply("Some error has occured. Ask admins to fix it.")
        return
    line = "Current metagame:\n"
    for elem in sort_data.keys():
        line += f"{elem} : {sort_data[elem]} ({round(100 * sort_data[elem] / summ, 2)}%)\n"
    await ctx.reply(line)


def create_missing_data():
    if not os.path.exists("data/metagame.json"):
        meta_data = {}
        with open("data/patapons.txt", "r") as f:
            lines = f.readlines()
        for line in lines:
            meta_data[line[:-1]] = 0
        with open("data/metagame.json", "w") as f:
            json.dump(meta_data, f)

    if not os.path.exists("data/await_confirmation.json"):
        with open("data/await_confirmation.json", "w") as f:
            json.dump([], f)

    if not os.path.exists("data/played_pairs.json"):
        with open("data/played_pairs.json", "w") as f:
            json.dump([], f)


read_status()
with open("data/token.txt", "r") as f:
    token = f.readline()

bot.run(token)