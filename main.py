import discord
from discord.ext import commands
import os
import json
import datetime
import codecs
import math

from requests import get


bot = commands.Bot(command_prefix='/')

allowed_letters = "abcdefghijklmnopqrstuvwxyz1234567890ABCDEFJHIJKLMNOPQRSTUVWXYZ!#$%&?"

STATUS = "NONE"
START_RATING = 100


def format_to_allowed(line):
    new_line = ""
    for c in line:
        if c not in allowed_letters:
            continue
        new_line += c
    return new_line

def read_status():
    global STATUS
    if not os.path.exists("data\\status.txt"):
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


def fix_ratings(participants):
    
    ratings = []
    for p in participants:
        ratings.append(get_rating(p, ment=True))
    
    avg = sum(ratings) / len(ratings)

    for i in range(len(participants) // 2):
        if ratings[i] >= avg:
            ratings[i] += 10
        else:
            ratings[i] += max(10, int(0.5 * (avg - ratings[i])))
    for i in range(len(participants) // 2 + (len(participants) % 2), len(participants)):
        if ratings[i] <= avg:
            ratings[i] -= 10
        else:
            ratings[i] -= max(10, int(0.5 * (ratings[i] - avg)))
    
    for i in range(len(participants)):
        update_rating(participants[i], ratings[i], ment=True)


            


@commands.has_permissions(administrator=True)
@bot.command()
async def lose(ctx, message):
    with open("data/points.json", "r") as f:
        data = json.load(f)
    for i in range(len(data["participants"])):
        if data["participants"][i] == message:
            data["points"][i] -= 3
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
            data["points"][i] += 3
            break
    with open("data/points.json", "w") as f:
        json.dump(data, f)


@commands.has_permissions(administrator=True)
@bot.command() 
async def restart_round(ctx):
    global STATUS
    with open("data/round_n.txt", "r") as f:
        n = f.readline()

    with open("data/points.json", "r") as f:
        part_points = json.load(f)
    
    part_points["participants"] = [x for _, x in sorted(zip(part_points["points"], part_points["participants"]), reverse=True)]
    part_points["points"] = [x for x, _ in sorted(zip(part_points["points"], part_points["participants"]), reverse=True)]
    
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

        line += f"{participants[2 * i]}\n1) {part_data['classes'][participants[2 * i]][0]}\n2) {part_data['classes'][participants[2 * i]][1]}\n3) {part_data['classes'][participants[2 * i]][2]}\n"
        line += "\nVS\n\n"
        line += f"{participants[2 * i + 1]}\n1) {part_data['classes'][participants[2 * i + 1]][0]}\n2) {part_data['classes'][participants[2 * i + 1]][1]}\n3) {part_data['classes'][participants[2 * i + 1]][2]}\n"
        line += "\n\n\n"

    if len(participants) % 2 == 1:
        line += f"{participants[-1]}, you skip this round (autowin)\n"
        for i in range(len(part_points["participants"])):
            if part_points["participants"][i] == participants[-1]:
                part_points["points"][i] += 3

    with open("data/points.json", "w") as f:
        json.dump(part_points, f)

    await ctx.reply(line)

    with open("data/pairs.json", "w") as f:
        json.dump(unresolved, f)


@bot.command()
async def help_me(ctx):
    line = "```/help_me -- show this message\n\
/reg -- register for the tournament\n\
/result -- write the result of your match (ex. '/result 3-2' -- you win 3 and lose 2 games)\n\
/leaderboard -- show the leaderboard\n\
/start_registration (admin only) -- start registration for the new tournament\n\
/end_registration (admin only) -- end registration for current tournament\n\
/start_tournament (admin only) -- begin the tournament\n\
/show_status (admin only) -- show all the participants of the tournament\n\
/end_round (admin only) -- end round by force\n\
/end_tournament (admin only) -- end tournament by force\n\
/restart_round (admin only) -- restart tournament by force\n\
/win @player (admin only) -- give 3 point to the player\n\
/lose @player (admin only) -- take 3 points to the player```"
    await ctx.reply(line)


@bot.command()
async def reg(ctx, *message):
    global STATUS

    if STATUS != "REGISTR":
        await ctx.reply("The registration has not started yet.\nAsk admins to start the registration.")
        return

    with open("data/current_tournament.json", 'r') as f:
        tour_data = json.load(f)
    if ctx.author.mention in tour_data["participants"]:
        await ctx.reply(f'{ctx.author.mention}, you have already registred for this tournament.\nAsk admins if you want to change classes.')
        return

    classes = list(message)
    if len(classes) != 3:
        await ctx.reply(f'{ctx.author.mention}, format your input the following way:\n/reg Taterazay Yarida Yumiyacha')
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
        await ctx.reply(line)
        return
    
    for i in range(len(classes)):
        classes[i] = classes[i].strip().lower().capitalize()

    classes = list(set(classes))
    if len(classes) < 3:
        line = f'{ctx.author.mention}, please, select 3 different classes'
        await ctx.reply(line)
        return

    rating = get_rating(ctx.author)
    if rating == -1:
        rating = START_RATING
        update_rating(ctx.author, rating)

    reply = f"Success!\n{ctx.author.mention}\nRating: {rating}\n1) {classes[0]}\n2) {classes[1]}\n3) {classes[2]}"   

    tour_data["participants"].append(ctx.author.mention)
    tour_data["classes"][ctx.author.mention] = classes

    with open("data/current_tournament.json", "w") as f:
        json.dump(tour_data, f)

    await ctx.reply(reply)


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
async def start_registration(ctx):
    global STATUS
    STATUS = "REGISTR"
    with open("data/status.txt", "w") as f:
        f.write("REGISTR")
    with open(f"data/current_tournament.json", "w") as f:
        data = {"participants" : [], "classes" : {}}
        json.dump(data, f)


@commands.has_permissions(administrator=True)
@bot.command() 
async def start_tournament(ctx):
    global STATUS
    STATUS = "TOURN"
    with open("data/status.txt", "w") as f:
        f.write("TOURN")
    with open("data/current_tournament.json", "r") as f:
        part_data = json.load(f)
    participants = sorted(part_data["participants"], key=lambda x: get_rating(x, ment=True), reverse=True)
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

    unresolved = []

    line = "ROUND 1:\n\n\n"

    for i in range(len(participants) // 2):
        pair = (participants[2 * i], participants[2 * i + 1])
        unresolved.append(pair)

        line += f"{participants[2 * i]}\n1) {part_data['classes'][participants[2 * i]][0]}\n2) {part_data['classes'][participants[2 * i]][1]}\n3) {part_data['classes'][participants[2 * i]][2]}\n"
        line += "\nVS\n\n"
        line += f"{participants[2 * i + 1]}\n1) {part_data['classes'][participants[2 * i + 1]][0]}\n2) {part_data['classes'][participants[2 * i + 1]][1]}\n3) {part_data['classes'][participants[2 * i + 1]][2]}\n"
        line += "\n\n\n"

    if len(participants) % 2 == 1:
        line += f"{participants[-1]}, you skip this round (autowin)\n"
        for i in range(len(part_points["participants"])):
            if part_points["participants"][i] == participants[-1]:
                part_points["points"][i] += 3

    with open("data/points.json", "w") as f:
        json.dump(part_points, f)

    await ctx.reply(line)

    with open("data/pairs.json", "w") as f:
        json.dump(unresolved, f)

    with open("data/round_n.txt", "w") as f:
        f.write("1")


@bot.command() 
async def result(ctx, message):
    global STATUS
    if STATUS != "TOURN":
        await ctx.reply("The tournament has not started yet.")
        return
        
    with open("data/pairs.json", "r") as f:
        unresolved = json.load(f)

    for pair in unresolved:
        if ctx.author.mention in pair:
            break
    else:
        await ctx.reply(f"{ctx.author.mention}, you have no active games.")
        return
    
    if '-' not in message:
        await ctx.reply(f"{ctx.author.mention}, correct format is <your wins>-<opponent's wins>.")
        return
    
    res = list(message.split("-"))
    if len(res) != 2 or res[0] not in "0123" or res[1] not in "0123" or int(res[0]) == int(res[1]):
        await ctx.reply(f"{ctx.author.mention}, correct format is <your wins>-<opponent's wins>.\nEach number has to be in range 0-3. One has to be higher than other.")
        return

    your_score = int(res[0])
    opponent_score = int(res[1])
    
    for pair in unresolved:
        if ctx.author.mention in pair:
            opponent = pair[0]
            if opponent == ctx.author.mention:
                opponent = pair[1]
            unresolved.remove(pair)
            break

    with open("data/pairs.json", "w") as f:
        json.dump(unresolved, f)     

    with open("data/points.json", "r") as f:
        points_data = json.load(f)

    if your_score > opponent_score:
        for i in range(len(points_data["participants"])):
            if points_data["participants"][i] == ctx.author.mention:
                points_data["points"][i] += 3
        #fix_ratings(ctx.author.mention, opponent, True, your_score - opponent_score)
    elif opponent_score > your_score:
        for i in range(len(points_data["participants"])):
            if points_data["participants"][i] == opponent:
                points_data["points"][i] += 3
        #fix_ratings(ctx.author.mention, opponent, False, opponent_score - your_score)



    with open("data/points.json", "w") as f:
        json.dump(points_data, f)

    await ctx.reply(f"{ctx.author.mention}, your result has been saved.")


    if len(unresolved) == 0:

        with open("data/round_n.txt", "r") as f:
            n = f.readline()

        with open("data/max_rounds.txt", "r") as f:
            max_num = f.readline()

        with open("data/points.json", "r") as f:
            part_points = json.load(f)
        
        part_points["participants"] = [x for _, x in sorted(zip(part_points["points"], part_points["participants"]), reverse=True)]
        part_points["points"] = [x for x, _ in sorted(zip(part_points["points"], part_points["participants"]), reverse=True)]


        if max_num == n:
            line = "@everyone\nThe tournament has ended.\nThe results are the following:\n\n"

            for i in range(len(part_points["participants"])):
                line += f"{i + 1}) " + part_points["participants"][i] + " " * (20 - len(part_points["participants"][i])) + str(part_points["points"][i]) + "\n"

            status = "NONE"
            with open("data/status.txt", "w") as f:
                f.write(status)

            await ctx.reply(line)
            fix_ratings(part_points["participants"])
            return

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

            line += f"{participants[2 * i]}\n1) {part_data['classes'][participants[2 * i]][0]}\n2) {part_data['classes'][participants[2 * i]][1]}\n3) {part_data['classes'][participants[2 * i]][2]}\n"
            line += "\nVS\n\n"
            line += f"{participants[2 * i + 1]}\n1) {part_data['classes'][participants[2 * i + 1]][0]}\n2) {part_data['classes'][participants[2 * i + 1]][1]}\n3) {part_data['classes'][participants[2 * i + 1]][2]}\n"
            line += "\n\n\n"

        if len(participants) % 2 == 1:
            line += f"{participants[-1]}, you skip this round round (autowin)\n"
            for i in range(len(part_points["participants"])):
                if part_points["participants"][i] == participants[-1]:
                    part_points["points"][i] += 3

        with open("data/points.json", "w") as f:
            json.dump(part_points, f)

        await ctx.reply(line)

        with open("data/pairs.json", "w") as f:
            json.dump(unresolved, f)
        

@commands.has_permissions(administrator=True)
@bot.command() 
async def end_round(ctx):
    global STATUS
    with open("data/round_n.txt", "r") as f:
        n = f.readline()

    with open("data/max_rounds.txt", "r") as f:
        max_num = f.readline()

    with open("data/points.json", "r") as f:
        part_points = json.load(f)
    
    part_points["participants"] = [x for _, x in sorted(zip(part_points["points"], part_points["participants"]), reverse=True)]
    part_points["points"] = [x for x, _ in sorted(zip(part_points["points"], part_points["participants"]), reverse=True)]


    if max_num == n:
        line = "@everyone\nThe tournament has ended.\nThe results are the following:\n\n"

        for i in range(len(part_points["participants"])):
            line += f"{i + 1}) " + part_points["participants"][i] + " " * (20 - len(part_points["participants"][i])) + str(part_points["points"][i]) + "\n"

        status = "NONE"
        with open("data/status.txt", "w") as f:
            f.write(status)

        await ctx.reply(line)
        fix_ratings(part_points["participants"])
        return

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

        line += f"{participants[2 * i]}\n1) {part_data['classes'][participants[2 * i]][0]}\n2) {part_data['classes'][participants[2 * i]][1]}\n3) {part_data['classes'][participants[2 * i]][2]}\n"
        line += "\nVS\n\n"
        line += f"{participants[2 * i + 1]}\n1) {part_data['classes'][participants[2 * i + 1]][0]}\n2) {part_data['classes'][participants[2 * i + 1]][1]}\n3) {part_data['classes'][participants[2 * i + 1]][2]}\n"
        line += "\n\n\n"

    if len(participants) % 2 == 1:
        line += f"{participants[-1]}, you skip the first round (autowin)\n"
        for i in range(len(part_points["participants"])):
            if part_points["participants"][i] == participants[-1]:
                part_points["points"][i] += 3

    with open("data/points.json", "w") as f:
        json.dump(part_points, f)

    await ctx.reply(line)

    with open("data/pairs.json", "w") as f:
        json.dump(unresolved, f)


@commands.has_permissions(administrator=True)
@bot.command() 
async def end_tournament(ctx):
    global STATUS
    with open("data/points.json", "r") as f:
        part_points = json.load(f)
    
    part_points["participants"] = [x for _, x in sorted(zip(part_points["points"], part_points["participants"]), reverse=True)]
    part_points["points"] = [x for x, _ in sorted(zip(part_points["points"], part_points["participants"]), reverse=True)]

    line = "@everyone\nThe tournament has ended.\nThe results are the following:\n\n"
    for i in range(len(part_points["participants"])):
        line += f"{i + 1}) " + part_points["participants"][i] + " " * (20 - len(part_points["participants"][i])) + str(part_points["points"][i]) + "\n"

    status = "NONE"
    with open("data/status.txt", "w") as f:
        f.write(status)

    await ctx.reply(line)
    fix_ratings(part_points["participants"])
    return

@commands.has_permissions(administrator=True)
@bot.command() 
async def end_registration(ctx):
    global STATUS
    STATUS = "NONE"
    with open("data/status.txt", "w") as f:
        f.write("NONE")
    

@commands.has_permissions(administrator=True)
@bot.command() 
async def print_status(ctx):
    global STATUS
    print(STATUS)



read_status()   
bot.run("MTAwMTAyMDY4MDgxMDI3MDc4MA.GCXgkc.PZPPLPkocviVNXStDhvRwTnM1AjYQ5R7Tn-qmg")