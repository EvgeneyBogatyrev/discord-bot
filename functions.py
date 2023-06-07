import os
import json
import random
import codecs
import datetime

from constants import Constants


def adjust_rating(user1, user2, win):
    """
    Adjust both player's ratings after their game.

    user1 : tag of the first player
    user2 : tag of the second player
    win : True if first user won, otherwise False
    """

    rating1 = get_rating(user1, mention=True)
    rating2 = get_rating(user2, mention=True)

    win_chance1 = 1 / (1 + 10 ** ((rating2 - rating1) / Constants.ELO_DIFF))
    win_chance2 = 1 / (1 + 10 ** ((rating1 - rating2) / Constants.ELO_DIFF))

    diff1 = int((int(win) - win_chance1) * Constants.ELO_STEP)
    diff2 = int((int(not win) - win_chance2) * Constants.ELO_STEP)

    # If absolute difference is smaller than 1, make it 1.
    if win and diff1 == 0:
        diff1 = 1
    if win and diff2 == 0:
        diff2 = -1
    if not win and diff1 == 0:
        diff1 = -1
    if not win and diff2 == 0:
        diff2 = 1

    mode = read_mode()
    if mode == "1vs1":
        update_rating(user1, rating1 + diff1, mention=True)
        update_rating(user2, rating2 + diff2, mention=True)
    else:
        words = list(user1.split(" "))
        for word in words:
            if not "<" in word:
                continue
            update_rating(word, get_rating(word, mention=True) + diff1, mention=True)

        words = list(user2.split(" "))
        for word in words:
            if not "<" in word:
                continue
            update_rating(word, get_rating(word, mention=True) + diff2, mention=True)

    return diff1, diff2



def check_class(class_name):
    """
    Check if class_name is an existing Patapon 3 class.

    class_name -- name from user input.

    Returns: True or False
    """

    class_name = class_name.strip().lower()
    with open("data/patapons.txt", "r") as f:
        lines = list(f.readlines())
    for i in range(len(lines)):
        lines[i] = lines[i].strip().lower()
    if class_name not in lines:
        return False
    return True


def find_closest_class(class_name):
    """
    Find closest class name.

    class_name -- name from user input.

    Returns: Closest class name or None.
    """

    class_name = class_name.strip().lower()
    with open("data/patapons.txt", "r") as f:
        lines = list(f.readlines())

    base = {}
    for i in range(len(lines)):
        lines[i] = lines[i].strip().lower()
        
        error_index = 0
        for true_sym, fake_sym in zip(lines[i], class_name):
            if true_sym != fake_sym:
                error_index += 1
        error_index += abs(len(class_name) - len(lines[i]))

        base[lines[i]] = error_index

    min_error = -1
    best_class = None
    alert = False

    for cl in base:
        err = base[cl]
        if min_error == err:
            alert = True
        if min_error == -1 or min_error > err:
            alert = False
            min_error = err
            best_class = cl

    if alert:
        return None
    if len(best_class) / min_error < 2:
        return None

    return best_class



def create_missing_data():
    """
    Create all files in data folder.
    """

    if not os.path.exists("data/metagame.json"):
        meta_data = {}
        with open("data/patapons.txt", "r") as f:
            lines = f.readlines()
        for line in lines:
            meta_data[line[:-1]] = 0
        with open("data/metagame.json", "w") as f:
            json.dump(meta_data, f)

    if not os.path.exists("data/metagame2vs2.json"):
        meta_data = {}
        with open("data/patapons.txt", "r") as f:
            lines = f.readlines()
        for line in lines:
            meta_data[line[:-1]] = 0
        with open("data/metagame2vs2.json", "w") as f:
            json.dump(meta_data, f)

    if not os.path.exists("data/await_confirmation.json"):
        with open("data/await_confirmation.json", "w") as f:
            json.dump([], f)

    if not os.path.exists("data/patapon_names.json"):
        with open("data/patapon_names.json", "w") as f:
            json.dump({}, f)

    if not os.path.exists("data/played_pairs.json"):
        with open("data/played_pairs.json", "w") as f:
            json.dump([], f)

    if not os.path.exists("plan.json"):
        with open("plan.json", "w") as f:
            json.dump({}, f)


def format_to_allowed(line):
    """
    Replace all gibberish letters from line with english letters.

    line -- user name
    """

    updated_line = ""
    for symbol in line:
        if symbol in Constants.LETTERS_MATCH.keys():
            updated_line += Constants.LETTERS_MATCH[symbol]
            continue
        if symbol not in Constants.ALLOWED_LETTERS:
            continue
        updated_line += symbol
    return updated_line


def get_rating(name, mention=False, rec=False):
    """
    Get rating of the player.

    name -- player object or player tag
    mention -- True, if first argument is player tag, otherwise False

    Returns: True or False 
    """
    mode = read_mode()
    if mention and mode != "1vs1" and not rec:
        words = list(name.split(" "))
        summ = 0
        count = 0
        for word in words:
            if "<" not in word:
                continue
            summ += get_rating(word, mention=True, rec=True)
            count += 1
        assert count > 0, "Count is zero!"
        return round(summ / count)

    if not mention:
        with codecs.open("data/rating.csv", "r", 'utf-8') as f:
            lines = f.readlines()
        for line in lines:
            creds = list(line.split(","))
            if creds[0] == name.mention:
                return int(creds[2])
        return -1
    else:
        with codecs.open("data/rating.csv", "r", 'utf-8') as f:
            lines = f.readlines()
        for line in lines:
            creds = list(line.split(","))
            if creds[0] == name:
                return int(creds[2])
        return -1


def read_status():
    """
    Return status of the tournament.
    """

    global STATUS
    if not os.path.exists("data/status.txt"):
        STATUS = "NONE"
        with open("data/status.txt", "w") as f:
            f.write(STATUS)
    else:
        with open("data/status.txt", "r") as f:
            STATUS = f.readline()
    return STATUS


def read_mode():
    """
    Return current mode.
    """

    if not os.path.exists("data/mode.txt"):
        return "1vs1"
    with open("data/mode.txt", "r") as f:
        mode = f.readline()
    return mode


def update_rating(name, rating, mention=False):
    """
    Update rating of the user.

    name -- player tag
    rating -- new rating
    mention -- True, if first argument is player tag, otherwise False
    """
    if not mention:
        with codecs.open("data/rating.csv", "r", 'utf-8') as f:
            lines = f.readlines()
        data = {}
        for line in lines:
            creds = list(line.split(","))
            data[(creds[0], creds[1])] = int(creds[2][:-1])
            if creds[0] == name.mention:
                data[(creds[0], creds[1])] = rating
        else:
            data[(name.mention, format_to_allowed(name.name))] = rating
    else:
        with codecs.open("data/rating.csv", "r", 'utf-8') as f:
            lines = f.readlines()
        data = {}
        for line in lines:
            creds = list(line.split(","))
            data[(creds[0], creds[1])] = int(creds[2][:-1])
            if creds[0] == name:
                data[(creds[0], creds[1])] = rating

    inner_csv = ""
    for key in data:
        inner_csv += key[0] + "," + key[1] + "," + str(data[key]) + "\n"

    with open("data/rating.csv", "w") as f:
        f.write(inner_csv)


def get_random_patapons(number):

    if number == 0:
        return []
    if number > 28:
        number = 28

    with open("data/patapons.txt", "r") as f:
        csv = f.readlines()

    patapons = list(csv)
    for i in range(len(patapons)):
        patapons[i] = patapons[i][:-1]

    random.shuffle(patapons)
    return patapons[:number]

def get_cur_date():
    weekday = datetime.datetime.today().weekday()
    now = datetime.datetime.now()

    current_time = now.strftime("%H:%M:%S")
    
    words = current_time.split(":")
    hours = int(words[0])
    minutes = int(words[1])
    seconds = int(words[2])

    return weekday, hours, minutes, seconds

def get_banned_classes():
    return []
    # Dark Heroes
    dh = ["Sonarchy", "Buzzcrave"]
    banned = []
    
    from random import randint

    random_number = randint(0, len(dh) - 1)
    banned.append(dh[random_number])

    dh.remove(banned[0])

    #random_number = randint(0, len(dh) - 1)
    #banned.append(dh[random_number])


    # Light Heroes
    with open("data/metagame.json", "r") as f:
        meta = json.load(f)

    classes = []
    amount = []

    for class_ in meta.keys():
        classes.append(class_)
        amount.append(meta[class_])

    combo = zip(classes, amount)
    combo = sorted(combo, key=lambda x: x[1], reverse=True)

    classes = [x[0] for x in combo]
    
    to_ban = classes[:3]

    #random_number = randint(0, len(to_ban) - 1)
    #banned.append(to_ban[random_number])

    #to_ban.remove(banned[1])

    #random_number = randint(0, len(to_ban) - 1)
    #banned.append(to_ban[random_number])

    #to_ban.remove(banned[2])

    #random_number = randint(0, len(to_ban) - 1)
    #banned.append(to_ban[random_number])

    banned.extend(to_ban)

    return banned

def get_intro_message(banned, eng=False):

    if not eng:
        with open("data/init_mes.txt", "r")as f:
            message = f.read()
    else:
        with open("data/init_mes_eng.txt", "r") as f:
            message = f.read()

    message = message.replace("role_id", "<@&956913343057264641>")
    #message = message.replace("role_id", "<@&1009497359908089886>")
    message = message.replace("channel_id", "<#1009215461176647751>")

    while len(banned) < 4:
        banned.append("...")

    message = message.replace("class1", banned[0])
    message = message.replace("class2", banned[1])
    message = message.replace("class3", banned[2])
    message = message.replace("class4", banned[3])

    return message

def get_rules(banned, eng=True):

    if not eng:
        with open("data/init_mes.txt", "r") as f:
            message = f.read()
    else:
        with open("data/init_mes_eng.txt", "r") as f:
            message = f.read()

    message = message.replace("role_id", "<@&956913343057264641>")
    #message = message.replace("role_id", "<@&1009497359908089886>")
    message = message.replace("channel_id", "<#1009215461176647751>")

    while len(banned) < 4:
        banned.append("...")

    message = message.replace("class1", banned[0])
    message = message.replace("class2", banned[1])
    message = message.replace("class3", banned[2])
    message = message.replace("class4", banned[3])

    return "\n".join(message.split("\n")[4:-4])


def update_log_classes():
    with open("data/current_tournament.json", "r") as f:
        data = json.load(f)
    classes = data["classes"]

    with open("logs/classes.json", "r") as f:
        cur_classes = json.load(f)


    for player in classes.keys():
        if player not in cur_classes.keys():
            cur_classes[player] = []
        cur_classes[player].append(classes[player])

    with open("logs/classes.json", "w") as f:
        json.dump(cur_classes, f)

def update_log_game(player1, player2, score1, score2):

    if "@" not in player1:
        player1 = "<@" + player1 + ">"
    if "@" not in player2:
        player2 = "<@" + player2 + ">"

    with open("logs/games_data.json", "r") as f:
        games = json.load(f)

    if player1 not in games.keys():
        games[player1] = []
    games[player1].append([score1, score2])

    if player2 not in games.keys():
        games[player2] = []
    games[player2].append([score2, score1])

    with open("logs/games_data.json", "w") as f:
        json.dump(games, f)


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

