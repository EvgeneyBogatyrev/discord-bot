class Constants:
    START_RATING = 100
    ELO_STEP = 16
    ELO_DIFF = 50
    POINTS_FOR_WIN = 10
    CONFIRM_SLEEP = 120

    MAX_MESSAGES = 10

    BOT_COMMANDS_ID_LOCAL = 1001104114522005534
    BOT_COMMANDS_ID = 1009215461176647751
    MEMES_ID = 1001220727892082748
    MEMES_ID_LOCAL = 1009201950174224524
    TOURN_STATUS = 1001220951939231744

    NIKI100 = 765174393323126815
    RULES_MSG_ID = 1009220223519432725


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

    HELP = "```If you want to see the description of a particular command, type /help command.\n\n\
/help                           Show this message\n\
/reg                            Register for the tournament\n\
/result                         Send the result of your match\n\
/confirm                        Confirm the results of the game your opponent sent\n\
/reject                         Reject the results of the game your opponent sent\n\
/drop                           Drop from the tournament\n\
/leaderboard                    Show the leaderboard\n\
/metagame                       Show classes popularity\n\
/nickname                       Set your Patapon 3 nickname\n\
/banlist                        Show classes that are banned for this tournament\n\
/start_reg (admin only)         Start registration for the new tournament\n\
/end_reg (admin only)           End registration for current tournament\n\
/start (admin only)             Begin the tournament\n\
/end_round (admin only)         End round by force\n\
/restart_round (admin only)     Restart tournament by force\n\
/drop_player (admin only)       Kick player from the tournament\n\
/ban_ (admin only)               Ban classes from tournament\n\
/ban_meta (admins only)         Ban top N meta classes from the tournament\n\
/unban (admin only)             Unban classes\n\
```"

    HELP_MEME = "```If you want to see the description of a particular command, type /help command.\n\n\
/help                           Show this message\n\
/pon                            Generate random Patapon\n\
/kuwagattan_says                Generate Kuwagattan quote\n\
```"

    HELP_COMMAND = {
        "reg" : "no translation needed",
        "drop" : "no translation needed",
        "help" : "Show all bot commands.",
        "reg1vs1" : "Register for the tournament.\n\
Type: ```/reg class-name1 class-name2 class-name3``` where \
class-name1, class-name2, and class-name3 are classes you want to play.",
        "reg2vs2" : "Register for the tournament.\n\
Type: ```/reg @friend-tag class-name1 class-name2 ...``` where \
class-name1, class-name2, ... are classes you want to play.",
        "result" : "Send the result of your game.\n\
Type: ```/result your-wins:opponent's-wins```",
        "confirm" : "Confirm the results that your last opponent sent.",
        "reject" : "Reject the results that your last opponent sent.",
        "drop-reg" : "Cancel your registration for the tournament.\n\
You will still be able to come back.",
        "drop-tour" : "Drop from the tournament.\n\
You won't be able to come back.",
        "leaderboard" : "Show the leaderboard.",
        "metagame" : "Show the metagame.",
        "start_reg" : "Start the registration for the tournament.\n\
Only for admins.\n\
Type: ```/start_reg mode``` where mode is either 1vs1 or 2vs2.",
        "end_reg" : "End the registration for the tournament.\n\
Only for admins.",
        "start" :  "Start the tournament.\n\
Only for admins.",
        "end_round" :  "End current round by force. The leaderboard is not affected.\n\
Only for admins.",
        "restart_round" :  "Restart current round. The leaderboard is not affected.\n\
Only for admins.",
        "drop_player" :  "Use: ```/drop_player player_tag``` to drop the player from the tournament.\n\
Only for admins.",
        "ban_" : "Use ```/ban_ class1 class2 ...``` to ban specific classes from the tournament.\n\
Only for admins.",
        "ban_meta" : "Use ```/ban_meta N``` to ban top N meta classes from the tournament. See `/metagame` command.\n\
Only for admins.",
        "unban" : "Use ```/unban class1 class2 ...``` to unban specific classes.\n\
Only for admins.",
        "nickname" : "Use: ```/nickname your-nickname``` to set your Patapon3 nickname.",
        "banlist" : "Show classes that are banned for the tournament.",
        "pon" : f"`/pon` - generate random Patapon 3 class.\n`/pon X` - generate X random Patapon 3 classes.",
        "kuwagattan_says" : f"Write `/kuwagattan_says any-text`."
    }