import json
import math
from random import randint
import discord
import asyncio

from functions import *


async def confirm_game(ctx, player, opponent, your_score, opponent_score, bot=None):  

    try:
        update_log_game(player, opponent, your_score, opponent_score)
    except:
        print("Can't store game data")

    with open("data/pairs.json", "r") as f:
        unresolved = json.load(f)

    for pair in unresolved:
        if player in pair and opponent in pair:
            unresolved.remove(pair)

    with open("data/pairs.json", "w") as f:
        json.dump(unresolved, f)     

    with open("data/points.json", "r") as f:
        points_data = json.load(f)

    try:
        if (your_score == 3 and opponent_score == 2) or (your_score == 2 and opponent_score == 3):
            add_ach_progress(player, 'long_game')
            add_ach_progress(opponent, 'long_game')
    except:
        print("ERROR in long game")


    if your_score > opponent_score:
        for i in range(len(points_data["participants"])):
            if points_data["participants"][i] == player:
                points_data["points"][i] += 10 + your_score - opponent_score
                try:
                    if points_data['points'][i] == 39:
                        add_ach_progress(player, "3-0_total")
                except:
                    print("ERROR in INVINCIBLE")
            elif points_data["participants"][i] == opponent:
                points_data["points"][i] += opponent_score
        try:
            if your_score == 3 and opponent_score == 0:
                add_ach_progress(player, "3-0")
        except:
            print("ERROR in 3-0")
    elif opponent_score > your_score:
        for i in range(len(points_data["participants"])):
            if points_data["participants"][i] == opponent:
                points_data["points"][i] += 10 + opponent_score - your_score
                try:
                    if points_data['points'][i] == 39:
                        add_ach_progress(opponent, "3-0_total")
                except:
                    print("ERROR in INVINCIBLE")
            elif points_data["participants"][i] == player:
                points_data["points"][i] += your_score
        try:
            if your_score == 0 and opponent_score == 3:
                add_ach_progress(opponent, "3-0")
        except:
            print("ERROR in 3-0")

    try:
        add_ach_progress(player, "20_games")
        add_ach_progress(opponent, "20_games")

        dark_heroes = ['Ragewolf', 'Naughtyfins', 'Sonarchy', 'Ravenous', 'Buzzcrave', 'Slogturtle', 'Covet-hiss']
        with open("data/current_tournament.json", 'r') as f:
            cur = json.load(f)
        classes_player = cur['classes'][player]
        classes_opponent = cur['classes'][opponent]

        for cl in classes_player:
            if cl in dark_heroes:
                add_ach_progress(player, "dark_hero_total")
                break
        for cl in classes_opponent:
            if cl in dark_heroes:
                add_ach_progress(opponent, "dark_hero_total")
                break


    except:
        print("ERROR in VETERAN!!!")

    with open("data/points.json", "w") as f:
        json.dump(points_data, f)

    diff1, diff2 = adjust_rating(player, opponent, your_score > opponent_score)

    try:
        if diff1 >= 10:
            add_ach_progress(player, "10_points")
        elif diff2 >= 10:
            add_ach_progress(opponent, "10_points")
    except:
        print("ERROR in diff")


    if diff1 >= 0:
        diff1 = "+" + str(diff1)
    else:
        diff1 = str(diff1)
    
    if diff2 >= 0:
        diff2 = "+" + str(diff2)
    else:
        diff2 = str(diff2)

    mode = read_mode()
    if mode == "1vs1":
        await ctx.send(f"{player} VS {opponent}\nResult: {your_score}:{opponent_score}\n\
    \nRating changes:\n{player} : {get_rating(player, mention=True)} ({diff1})\n{opponent} : {get_rating(opponent, mention=True)} ({diff2})")
    else:
        line = f"{player} VS {opponent}\nResult: {your_score}:{opponent_score}\nRating changes:\n"
        words1 = list(player.split(" "))
        for word in words1:
            if "<" not in word:
                continue
            line += f"{word} : {get_rating(word, mention=True)} ({diff1})\n"
        words2 = list(opponent.split(" "))
        for word in words2:
            if "<" not in word:
                continue
            line += f"{word} : {get_rating(word, mention=True)} ({diff2})\n"
        await ctx.send(line)
        
    if len(unresolved) == 0:
        await start_next_round(ctx, bot=bot)


async def end_current_tournament(ctx, bot=None):
    with open("data/status.txt", "r") as f:
        tmp_status = f.read()
    if tmp_status == "NONE":
        #await ctx.send("The tournament is already over.\n")
        return


    line = "The tournament has ended.\nThe results are the following:\n\n"
    
    with open("data/points.json", "r") as f:
        part_points = json.load(f)

    part_points["participants"] = [x for _, x in sorted(zip(part_points["points"], part_points["participants"]), reverse=True)]
    part_points["points"] = [x for x, _ in sorted(zip(part_points["points"], part_points["participants"]), reverse=True)]

    for i in range(len(part_points["participants"])):
        line += f"{i + 1}) " + part_points["participants"][i]
        line += " - "
        line += str(part_points["points"][i]) + "\n"

        if i == 0:
            player_id = part_points["participants"][i]
            player_id = int(player_id[2:-1])
            print(player_id)
            try:
                add_ach_progress("<@" + player_id + ">", '1st_place')
            except:
                print("ERROR IN 1st PLACE")
            await assign_role(player_id, bot)
    status = "NONE"
    with open("data/status.txt", "w") as f:
        f.write(status)

    await ctx.send(line)


async def start_next_round(ctx, increment=True, no_sort=False, bot=None, round_n=-1):
    #with open("data/last_round_started")

    with open("data/round_n.txt", "r") as f:
        n = f.readline()
    n = int(n)

    #await ctx.send(f"Cur round = {n}, skipping = {round_n}\n")

    if round_n != -1 and n > round_n:
        #await ctx.send(f"Round {round_n + 1} has already started\n")
        return

    with open("data/max_rounds.txt", "r") as f:
        max_num = f.readline()

    with open("data/points.json", "r") as f:
        part_points = json.load(f)
    
    number_of_participants = len(part_points["participants"])
    max_num = int(math.log2(number_of_participants))
    if 2 ** max_num != number_of_participants:
        max_num += 1

    max_num = 3

    if not no_sort:
        part_points["participants"] = [x for _, x in sorted(zip(part_points["points"], part_points["participants"]), reverse=True)]
        part_points["points"] = [x for x, _ in sorted(zip(part_points["points"], part_points["participants"]), reverse=True)]
    else:
        odd = part_points["participants"][::2]
        even = part_points["participants"][1::2]
        even = even[::-1]


        new_list = []
        for i in range(len(part_points["participants"])):
            if i % 2 == 0:
                new_list.append(odd[i // 2])
            else:
                new_list.append(even[i // 2])
        part_points["participants"] = new_list

        try:
            if len(part_points["participants"]) % 2 == 1:
                first_player = part_points["participants"][0]
                last_player = part_points["participants"][-1]
                part_points["participants"][0] = last_player
                part_points["participants"][-1] = first_player
        except:
            pass


    if len(part_points["participants"]) % 2 == 1:
        with open("data/outsiders.json", "r") as f:
            outsiders = json.load(f)

        i = len(part_points["participants"]) - 1
        while part_points["participants"][i] in outsiders:
            i -= 1
            if i < 0:
                i = len(part_points["participants"]) - 1
                break
        outsider = part_points["participants"].pop(i)
        score_of_man = part_points["points"].pop(i)
        part_points["participants"].append(outsider)
        part_points["points"].append(score_of_man)

        outsiders.append(outsider)

        with open("data/outsiders.json", "w") as f:
            json.dump(outsiders, f)

    def check_repeat_games(array):
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
            number = check_repeat_games(part_points["participants"][:-1])
        else:
            number = check_repeat_games(part_points["participants"])
        if number == -1:
            break

        outsider = part_points["participants"].pop(number)
        outsiders_points = part_points["points"].pop(number)

        random_place = randint(0, len(part_points["participants"]) - 1)
        part_points["participants"].insert(random_place, outsider)
        part_points["points"].insert(random_place, outsiders_points)

        print("Rematching...")


    if int(max_num) <= int(n):
        await end_current_tournament(ctx, bot)
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

        line += f"{participants[2 * i]}\n"
        for j in range(len(part_data['classes'][participants[2 * i]])):
            line += f"{j + 1}) {part_data['classes'][participants[2 * i]][j]}\n"
        line += "\nVS\n\n"
        line += f"{participants[2 * i + 1]}\n"
        for j in range(len(part_data['classes'][participants[2 * i + 1]])):
            line += f"{j + 1}) {part_data['classes'][participants[2 * i + 1]][j]}\n"
        line += "\n\n\n"

    if len(participants) % 2 == 1:
        line += f"{participants[-1]}, you skip this round (auto win)\n"
        line += "\n\n\n"
    line += "To send the results of your game, go to <#1009215461176647751> and type !result <your-wins>:<opponent-wins>\nExample: !result 3-1\n\n\n"
    
    if bot is not None and n != 1:
        _partic = [x for _, x in sorted(zip(part_points["points"], part_points["participants"]), reverse=True)]
        _points = [x for x, _ in sorted(zip(part_points["points"], part_points["participants"]), reverse=True)]

        with open("data/patapon_names.json", "r") as f:
            nicknames = json.load(f)
        
        em = discord.Embed(
            title = 'Current points:'
        )
        if read_mode() == "1vs1":
            for index, tag in enumerate(_partic):
                user = await bot.fetch_user(int(tag[2:-1]))
                name = user.name
                name = name.replace("_", "\_") 
                if tag in nicknames.keys():
                    name += f" _({nicknames[tag]})_"
                em.add_field(name = f'{index + 1}: {name}', value = f'{_points[index]}', inline=False)
        else:
            for index, tag in enumerate(_partic):
                words = list(tag.split(" "))
                players = []
                for word in words:
                    if "<" not in word:
                        continue
                    user = await bot.fetch_user(int(word[2:-1]))
                    name = user.name
                    name = name.replace("_", "\_") 
                    if word in nicknames.keys():
                        name += f" _({nicknames[word]})_"
                    players.append(name)
                names = players[0]
                for i in range(1, len(players)):
                    names += " and " + players[i]
                em.add_field(name = f'{index + 1}: {names}', value = f'{_points[index]}', inline=False)
        await ctx.send(line, embed = em)
    else:
        await ctx.send(line)

    if len(participants) % 2 == 1:
        for i in range(len(part_points["participants"])):
            if part_points["participants"][i] == participants[-1]:
                part_points["points"][i] += Constants.POINTS_FOR_WIN

    with open("data/points.json", "w") as f:
        json.dump(part_points, f)

    with open("data/pairs.json", "w") as f:
        json.dump(unresolved, f)


async def assign_role(member_id, bot):

    members = bot.get_all_members()
    member = discord.utils.get(members, id=member_id)
    role = discord.utils.get(member.guild.roles, name="Tournament Winner")

    await member.add_roles(role)

