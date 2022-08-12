import os
import json
import codecs

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

    update_rating(user1, rating1 + diff1, mention=True)
    update_rating(user2, rating2 + diff2, mention=True)

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

    if not os.path.exists("data/await_confirmation.json"):
        with open("data/await_confirmation.json", "w") as f:
            json.dump([], f)

    if not os.path.exists("data/played_pairs.json"):
        with open("data/played_pairs.json", "w") as f:
            json.dump([], f)


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


def get_rating(name, mention=False):
    """
    Get rating of the player.

    name -- player object or player tag
    mention -- True, if first argument is player tag, otherwise False

    Returns: True or False 
    """

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