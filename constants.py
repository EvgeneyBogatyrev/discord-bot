class Constants:
    START_RATING = 100
    ELO_STEP = 16
    ELO_DIFF = 50
    POINTS_FOR_WIN = 10
    CONFIRM_SLEEP = 120

    ALLOWED_LETTERS = " ()abcdefghijklmnopqrstuvwxyz1234567890ABCDEFJHIJKLMNOPQRSTUVWXYZ!#$%&?,."
    LETTERS_MATCH = {
        "с" : "s",
        "к" : "k",
        "в" : "v",
        "и" : "i",
        "д" : "d",
        "а" : "a",
        "б" : "b",
        "г" : "g",
        "е" : "e",
        "ё" : "e",
        "ж" : "j",
        "з" : "z",
        "й" : "i",
        "л" : "l",
        "м" : "m",
        "н" : "n",
        "о" : "o",
        "п" : "p",
        "р" : "r",
        "т" : "t",
        "у" : "u",
        "ф" : "f",
        "х" : "h",
        "ц" : "c",
        "ч" : "ch",
        "ш" : "sh",
        "щ" : "sch",
        "ы" : "y",
        "э" : "e",
        "ю" : "yu",
        "я" : "ya",
        "С" : "S",
        "К" : "K",
        "В" : "V",
        "И" : "I",
        "Д" : "D",
        "А" : "A",
        "Б" : "B",
        "Г" : "G",
        "Е" : "E",
        "Ё" : "E",
        "Ж" : "J",
        "З" : "Z",
        "Й" : "I",
        "Л" : "L",
        "М" : "M",
        "Н" : "N",
        "О" : "O",
        "П" : "P",
        "Р" : "R",
        "Т" : "T",
        "У" : "U",
        "Ф" : "F",
        "Х" : "H",
        "Ц" : "C",
        "Ч" : "Ch",
        "Ш" : "Sh",
        "Щ" : "Sch",
        "Ы" : "Y",
        "Э" : "E",
        "Ю" : "Yu",
        "Я" : "Ya"
    }

    HELP = "```/help_me -- show this message\n\
/reg -- register for the tournament\n\
/result -- write the result of your match (ex. '/result 3-2' -- you win 3 and lose 2 games)\n\
/confirm -- confirm the results of the game your opponent sent\n\
/refute -- refute the results of the game your opponent sent\n\
/drop -- drop from the tournament\n\
/leaderboard -- show the leaderboard\n\
/metagame -- show classes popularity (not available during registration)\n\
/start_reg (admin only) -- start registration for the new tournament\n\
/end_reg (admin only) -- end registration for current tournament\n\
/start (admin only) -- begin the tournament\n\
/show_status (admin only) -- show all the participants of the tournament\n\
/end_round (admin only) -- end round by force\n\
/end_tournament (admin only) -- end tournament by force\n\
/restart_round (admin only) -- restart tournament by force\n\
/drop_player (admin only) -- kick player from the tournament\n\
```"