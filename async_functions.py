import json
import math
from random import randint

from functions import *


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
        await start_next_round(ctx)


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
    n = int(n)

    with open("data/max_rounds.txt", "r") as f:
        max_num = f.readline()

    with open("data/points.json", "r") as f:
        part_points = json.load(f)
    
    number_of_participants = len(part_points["participants"])
    max_num = int(math.log2(number_of_participants))
    if 2 ** max_num != number_of_participants:
        max_num += 1

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
        for i in range(len(part_points["participants"])):
            if part_points["participants"][i] == participants[-1]:
                part_points["points"][i] += Constants.POINTS_FOR_WIN

    with open("data/points.json", "w") as f:
        json.dump(part_points, f)

    await ctx.send(line)

    with open("data/pairs.json", "w") as f:
        json.dump(unresolved, f)