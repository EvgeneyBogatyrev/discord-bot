import os
import json

def add_ach_progress(player, achievement, set_to=-1):
    try:
        if achievement == "unique":
            with open("logs/classes.json", 'r') as f:
                classes = json.load(f)
            
            if player not in classes.keys():
                return


            
            return
        else:
            pass
    except:
        pass

    with open("ach.json", "r") as f:
        ach = json.load(f)

    if player not in ach.keys():
        ach[player] = {}
    if achievement not in ach[player].keys():
        ach[player][achievement] = 0
    if set_to == -1:
        ach[player][achievement] += 1
    else:
        ach[player][achievement] = set_to

    with open("ach.json", "w") as f:
        json.dump(ach, f)


with open("logs/games_data.json", 'r') as f:
    games_data = json.load(f)


with open('logs/classes.json', 'r') as f:
    classes_data = json.load(f)

for player in games_data:
    add_ach_progress(player, "register_1st")
    len_games = len(games_data[player])
    add_ach_progress(player, "20_games", len_games)

    if [3, 0] in games_data[player]:
        add_ach_progress(player, "3-0")
    if [3, 2] in games_data[player] or [2, 3] in games_data[player]:
        add_ach_progress(player, "long_game")

    dh = ['Ragewolf', 'Naughtyfins', 'Sonarchy', 'Ravenous', 'Buzzcrave', 'Slogturtle', 'Covet-hiss']

    if player in classes_data:
        all_classes =  classes_data[player]
        all_c = []
        for elem in all_classes:
            all_c.extend(elem)

        dh_count = 0
        for elem in all_c:
            if elem in dh:
                dh_count += 1

        if dh_count > 0:
            add_ach_progress(player, "dark_hero_first", 1)

        add_ach_progress(player, "dark_hero_total", dh_count)


first_place_men = [
   "<@749632385179582538>",
   "<@265561687078338562>",
   "<@765174393323126815>",
   "<@637010153983705089>",
]


nick = [
    "<@701803834003030047>",
    "<@265561687078338562>",
    "<@749632385179582538>",
    "<@749354891977162792>",
    "<@930929234657030206>",
    "<@429571599839133706>",
        ]

for man in first_place_men:
    add_ach_progress(man, "1st_place", 1)


for man in nick:
    add_ach_progress(man, "nickname", 1)


gigachads = [
"<@749354891977162792>",
"<@701803834003030047>",
"<@765174393323126815>",
"<@429571599839133706>",
"<@265561687078338562>",
"<@749632385179582538>",
"<@878917541324525588>",


        ]


for man in gigachads:
    add_ach_progress(man, 'kuwagattan', 10)
    add_ach_progress(man, 'eye', 20)
    add_ach_progress(man, 'pon_video', 1)

