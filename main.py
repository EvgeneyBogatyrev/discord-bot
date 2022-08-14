from discord.ext import commands
import discord
import json
import codecs
import math
import asyncio
from random import randint
import matplotlib.pyplot

COLOR = 'white'
matplotlib.pyplot.rcParams['text.color'] = COLOR
matplotlib.pyplot.rcParams['axes.labelcolor'] = COLOR
matplotlib.pyplot.rcParams['xtick.color'] = COLOR
matplotlib.pyplot.rcParams['ytick.color'] = COLOR

from constants import Constants
from functions import *
from async_functions import *

intents = discord.Intents.default()
intents.members = True

client = discord.Client(intents=intents)

bot = commands.Bot(command_prefix='/')      # bot react on messages that start with '/'
bot.remove_command("help")                  # inmplement custom /help command


STATUS = "NONE"                             # status of the tournament
                                            # NONE - no tournament
                                            # REGISTR - the registration is on
                                            # TOURN - the tournament is on

EDITING_PAIRS = False                       # mutex to prevent double reading/writing



@bot.command()
async def drop(ctx):
    global STATUS

    with open("data/status.txt", "r") as f:
        STATUS = f.readline()

    with open("data/current_tournament.json", "r") as f:
        data = json.load(f)

    if STATUS == "NONE":
        await ctx.reply("There is no tournament right now.")
        return

    elif STATUS == "REGISTR":

        player_id = None
        for i in range(len(data["participants"])):
            if ctx.author.mention in data["participants"][i]:
                player_id = data["participants"][i]
                break
        if player_id is None:
            await ctx.reply("You are not registred")
            return
        
        data["participants"].remove(player_id)
        classes = data["classes"][player_id]
        del data["classes"][player_id]

        with open("data/current_tournament.json", "w") as f:
            json.dump(data, f)

        meta_filename = "data/metagame.json"
        if read_mode() == "2vs2":
            meta_filename = "data/metagame2vs2.json"
        with open(meta_filename, "r") as f:
            meta_data = json.load(f)
        for cl in classes:
            meta_data[cl] -= 1
        with open(meta_filename, "w") as f:
            json.dump(meta_data, f)

        await ctx.reply(f"{player_id} canceled their registration.")
        return

    else:
        player_id = None
        for i in range(len(data["participants"])):
            if ctx.author.mention in data["participants"][i]:
                player_id = data["participants"][i]
                break
        if player_id is None:
            await ctx.reply("You are not registred")
            return

        with open("data/current_tournament.json", "r") as f:
            data = json.load(f)
        data["participants"].remove(player_id)
        del data["classes"][player_id]

        with open("data/current_tournament.json", "w") as f:
            json.dump(data, f)

        with open("data/points.json", "r") as f:
            points_data = json.load(f)

        for i in range(len(points_data["participants"])):
            if points_data["participants"][i] == player_id:
                del points_data["points"][i]
                del points_data["participants"][i]
                break

        with open("data/pairs.json", "r") as f:
            data = json.load(f)

        opponent = None
        for pair in data:
            if player_id in pair:
                opponent = pair[0]
                if opponent == player_id:
                    opponent = pair[1]
                data.remove(pair)
                break

        with open("data/pairs.json", "w") as f:
            json.dump(data, f)
                        
        with open("data/points.json", "w") as f:
            json.dump(points_data, f)

        await ctx.send(f"{player_id} dropped from the tournament. See you next time!")
        if opponent is not None:
            await confirm_game(ctx, player_id, opponent, 0, 1, bot)
            

@bot.command()
async def pon(ctx, message=None):
    
    links = {
        "Taterazay" : "https://static.wikia.nocookie.net/patapon/images/3/39/Taterazay.png",
        "Tondenga" : "https://static.wikia.nocookie.net/patapon/images/0/07/Tondenga.png",
        "Destrobo" : "https://static.wikia.nocookie.net/patapon/images/9/90/Destrobo.png",
        "Guardira" : "https://static.wikia.nocookie.net/patapon/images/3/3d/Guardira.png",
        "Myamsar" : "https://static.wikia.nocookie.net/patapon/images/3/3f/Myamsar.png",
        "Bowmunk" : "https://static.wikia.nocookie.net/patapon/images/4/43/Bowmunk.png",
        "Grenburr" : "https://static.wikia.nocookie.net/patapon/images/c/c8/Grenburr.png",
        "Yarida" : "https://static.wikia.nocookie.net/patapon/images/a/a7/Yarida.png",
        "Kibadda" : "https://static.wikia.nocookie.net/patapon/images/2/2f/Kibadda.png",
        "Piekron" : "https://static.wikia.nocookie.net/patapon/images/2/21/Piekron.png",
        "Cannassault" : "https://static.wikia.nocookie.net/patapon/images/8/83/Cannassault.png",
        "Pyokorider" : "https://static.wikia.nocookie.net/patapon/images/0/0b/Pyokorider.png",
        "Wooyari" : "https://static.wikia.nocookie.net/patapon/images/e/e3/Wooyari.png",
        "Charibasa" : "https://static.wikia.nocookie.net/patapon/images/9/9a/Charibasa.png",
        "Yumiyacha" : "https://static.wikia.nocookie.net/patapon/images/e/e0/Yumiyacha.png",
        "Wondabarappa" : "https://static.wikia.nocookie.net/patapon/images/4/4c/Wondabarappa.png",
        "Pingrek" : "https://static.wikia.nocookie.net/patapon/images/7/76/Pingrek.png",
        "Alosson" : "https://static.wikia.nocookie.net/patapon/images/f/ff/Alosson.png",
        "Oohoroc" : "https://static.wikia.nocookie.net/patapon/images/8/86/Oohoroc.png",
        "Jamsch" : "https://static.wikia.nocookie.net/patapon/images/c/c1/Jamsch.png",
        "Cannogabang" : "https://static.wikia.nocookie.net/patapon/images/e/e8/Cannogabang.png",
        "Ragewolf" : "https://static.wikia.nocookie.net/patapon/images/7/7e/Image_1652.png",
        "Naughtyfins" : "https://static.wikia.nocookie.net/patapon/images/6/6f/Image_1668.png",
        "Sonarchy" : "https://static.wikia.nocookie.net/patapon/images/a/a7/Image_1684.png",
        "Ravenous" : "https://static.wikia.nocookie.net/patapon/images/3/32/Image_1700.png",
        "Buzzcrave" : "https://static.wikia.nocookie.net/patapon/images/8/87/Image_1713.png",
        "Slogturtle" : "https://static.wikia.nocookie.net/patapon/images/0/0d/Image_1732.png",
        "Covet-hiss" : "https://static.wikia.nocookie.net/patapon/images/5/5e/Image_1748.png"

    }

    if message is None:
        number = 1
    else:
        try:
            number = int(message)
        except:
            number = 1
    
    if number < 1:
        number = 1
    if number > 28:
        number = 28

    if number == 1:

        chance = randint(1, 100)
        if chance <= 5:
            await ctx.reply(file=discord.File('./pon.mp4'))
            return
        elif chance <= 10:
            e = discord.Embed()
            e.set_image(url="https://raw.githubusercontent.com/WallSoGB/Patapon3Textures/master/ui/drums/pon.png")
            await ctx.reply(embed=e)
            return
        
        patapon = get_random_patapons(1)[0]
    
        e = discord.Embed()
        e.set_image(url=links[patapon])
        await ctx.reply(patapon, embed=e)
    else:
        patapons = get_random_patapons(number)
        line = patapons[0]
        for i in range(1, number):
            line += "\n" + patapons[i]

        await ctx.reply(line)


@bot.command()
async def help(ctx, *message):
    if len(message) == 0:
        await ctx.reply(Constants.HELP)
    else:
        message = list(set(message))
        bad_commands = []
        for elem in message:
            if elem == "drop":
                status = read_status()
                if status == "REGISTR":
                    await ctx.reply("```/drop:```\n" + Constants.HELP_COMMAND["drop-reg"])
                else:
                    await ctx.reply("```/drop:```\n" + Constants.HELP_COMMAND["drop-tour"])
            elif elem == "reg":
                mode = read_mode()
                if mode == "1vs1":
                    await ctx.reply("```/reg:```\n" + Constants.HELP_COMMAND["reg1vs1"])
                else:
                    await ctx.reply("```/reg:```\n" + Constants.HELP_COMMAND["reg2vs2"])
            elif elem in Constants.HELP_COMMAND:
                await ctx.reply("```/" + elem + ":```\n" + Constants.HELP_COMMAND[elem])
            else:
                bad_commands.append(elem)
        if len(bad_commands) > 0:
            line = "Unknown commands:"
            for elem in bad_commands:
                line += " " + elem
            await ctx.reply(line)



@bot.command()
async def reg(ctx, *message):

    global STATUS
    STATUS = read_status()

    if STATUS != "REGISTR":
        await ctx.reply("The registration has not started yet.\nAsk admins to start the registration.")
        return

    mode = read_mode()
    if mode == "1vs1":
        await reg1vs1(ctx, message)
    elif mode == "2vs2":
        await reg2vs2(ctx, message)
    else:
        await ctx.send(f"Wrong mode: {mode}")


async def reg1vs1(ctx, message):

    with open("data/current_tournament.json", 'r') as f:
        tour_data = json.load(f)
    if ctx.author.mention in tour_data["participants"]:
        await ctx.reply(f'You have already registred for this tournament.\nDrop and register again if you want to change classes.')
        return

    classes = list(message)
    if len(classes) != 3:
        await ctx.send(f'{ctx.author.mention}, format your input the following way:\n/reg class1 class2 class3')
        await ctx.message.delete(delay=5)
        return
    
    for i in range(len(classes)):
        classes[i] = classes[i].strip()

    bad_classes = []
    for i, patapon in enumerate(classes[:]):
        if not check_class(patapon):
            improved_class = find_closest_class(patapon)
            if improved_class is None:
                bad_classes.append(patapon)
            else:
                classes[i] = improved_class

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

    tour_data["participants"].append(ctx.author.mention)
    tour_data["classes"][ctx.author.mention] = classes

    with open("data/current_tournament.json", "w") as f:
        json.dump(tour_data, f)

    await ctx.message.delete(delay=5)
    await ctx.send(f"{ctx.author.mention} (Rating: {rating}) has registred successfully.")

    with open("data/metagame.json", "r") as f:
        meta_data = json.load(f)
    for cl in classes:
        meta_data[cl] += 1
    with open("data/metagame.json", "w") as f:
        json.dump(meta_data, f)


async def reg2vs2(ctx, message):

    with open("data/current_tournament.json", 'r') as f:
        tour_data = json.load(f)

    for participant in tour_data["participants"]:
        if ctx.author.mention in participant:
            await ctx.reply(f'You have already registred for this tournament.\nDrop and register again if you want to change classes.')
            await ctx.message.delete(delay=5)
            return

    with open("data/pull_size.txt", "r") as f:
        pull_size = int(f.readline())

    data = list(message)
    if len(data) != pull_size + 1:
        line = f'{ctx.author.mention}, format your input the following way:\n/reg friend-tag'
        for j in range(pull_size):
            line += f" class{j + 1}"
        line += "\n"
        await ctx.send(line)
        await ctx.message.delete(delay=5)
        return
    
    bad = False
    partner = data[0].strip()
    if partner.startswith("<@") and partner.endswith(">"):
        partner = partner[2:-1]
        if partner.isdigit():
            partner = int(partner)
            partner = await bot.fetch_user(partner)
            if partner is None:
                bad = True
            elif partner == ctx.author:
                await ctx.reply("You cannot play with youtself. Go find some friends.")
                await ctx.message.delete(delay=5)
                return
            elif partner.name in ["PataHell Head-On Bot", "Dyno", "ProBot"]:
                await ctx.reply("You cannot play with bot. Go find some human friends.")
                await ctx.message.delete(delay=5)
                return
            else:
                for participant in tour_data["participants"]:
                    if partner.mention in participant:
                        await ctx.reply(f'{partner.name} is already in the tournament with someone else.')
                        await ctx.message.delete(delay=5)
                        return
        else:
            bad = True
    else:
        bad = True

    if bad:
        await ctx.reply("First word should be the tag of your partner. They should be PataHell discord member.")
        await ctx.message.delete(delay=5)
        return

    classes = []
    for i in range(1, len(data)):
        classes.append(data[i].strip())

    bad_classes = []
    for i, patapon in enumerate(classes[:]):
        if not check_class(patapon):
            improved_class = find_closest_class(patapon)
            if improved_class is None:
                bad_classes.append(patapon)
            else:
                classes[i] = improved_class

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
    if len(classes) < pull_size:
        line = f'{ctx.author.mention}, please, select {pull_size} different classes'
        await ctx.send(line)
        await ctx.message.delete(delay=5)
        return

    rating = get_rating(ctx.author)
    if rating == -1:
        rating = Constants.START_RATING
        update_rating(ctx.author, rating)
    partner_rating = get_rating(partner)
    if partner_rating == -1:
        partner_rating = Constants.START_RATING
        update_rating(partner, partner_rating)

    tour_data["participants"].append(f"{ctx.author.mention} and {partner.mention}")
    tour_data["classes"][f"{ctx.author.mention} and {partner.mention}"] = classes

    with open("data/current_tournament.json", "w") as f:
        json.dump(tour_data, f)

    await ctx.message.delete(delay=5)
    await ctx.send(f"{ctx.author.mention} (Rating: {rating}) and {partner.mention} (Rating: {partner_rating}) has registred successfully.")

    with open("data/metagame2vs2.json", "r") as f:
        meta_data = json.load(f)
    for cl in classes:
        meta_data[cl] += 1
    with open("data/metagame2vs2.json", "w") as f:
        json.dump(meta_data, f)
    

@bot.command()
async def nickname(ctx, message):
    tag = ctx.author.mention
    with open("data/patapon_names.json", "r") as f:
        data = json.load(f)
    data[tag] = str(message)
    with open("data/patapon_names.json", "w") as f:
        json.dump(data, f)
    await ctx.reply("Your nickname has been updated!")


@bot.command()
async def leaderboard(ctx):
    with codecs.open("data/rating.csv", "r", 'utf-8') as f:
        lines = f.readlines()

    with open("data/patapon_names.json", "r") as f:
        nicknames = json.load(f)

    em = discord.Embed(
        title = f'{ctx.guild.name} Leaderboard'
    )
  
    data = []
    for line in lines:
        words = list(line[:-1].split(","))
        tag = words[0]
        name = words[1]
        rating = int(words[2])
        user = await bot.fetch_user(int(tag[2:-1]))
        
        data.append((user, rating))

    data = sorted(data, key=lambda x: x[1], reverse=True)

    index = 1
    for index, amt in enumerate(data):
        name = amt[0].name
        name = name.replace("_", "\_") 
        if amt[0].mention in nicknames.keys():
            name += f" _({nicknames[amt[0].mention]})_"
        em.add_field(name = f'{index + 1}: {name}', value = f'{amt[1]}', inline=False)
        index += 1
        
    await ctx.send(embed = em)


@commands.has_permissions(administrator=True)
@bot.command() 
async def restart_round(ctx):
    await start_next_round(ctx, increment=False)


@commands.has_permissions(administrator=True)
@bot.command()
async def drop_player(ctx, message):
    with open("data/current_tournament.json", "r") as f:
        data = json.load(f)

    player_id = None
    for i in range(len(data["participants"])):
        if message in data["participants"][i]:
            player_id = data["participants"][i]
            break
    if player_id is None:
        await ctx.reply("This player is not registred.")
        return

    data["participants"].remove(player_id)
    del data["classes"][player_id]

    with open("data/current_tournament.json", "w") as f:
        json.dump(data, f)

    with open("data/points.json", "r") as f:
        points_data = json.load(f)

    for i in range(len(points_data["participants"])):
        if points_data["participants"][i] == player_id:
            del points_data["points"][i]
            del points_data["participants"][i]
            break

    with open("data/pairs.json", "r") as f:
        data = json.load(f)

    opponent = None
    for pair in data:
        if player_id in pair:
            opponent = pair[0]
            if opponent == player_id:
                opponent = pair[1]
            data.remove(pair)
            break

    with open("data/pairs.json", "w") as f:
        json.dump(data, f)
                    
    with open("data/points.json", "w") as f:
        json.dump(points_data, f)

    prep = "was"
    if read_mode() != "1vs1":
        prep = "were"

    await ctx.send(f"{player_id} {prep} kicked from the tournament. See you next time!")
    if opponent is not None:
        await confirm_game(ctx, player_id, opponent, 0, 1, bot)


@bot.command() 
async def result(ctx, message):
    global EDITING_PAIRS
    if EDITING_PAIRS:
        await asyncio.sleep(5)
        await result(ctx, message)
        return

    global STATUS
    STATUS = read_status()
    if STATUS != "TOURN":
        await ctx.reply("The tournament has not started yet.")
        return

    with open("data/current_tournament.json", "r") as f:
        data = json.load(f)

    player_id = None
    for i in range(len(data["participants"])):
        if ctx.author.mention in data["participants"][i]:
            player_id = data["participants"][i]
            break
    if player_id is None:
        await ctx.reply("You are not registred")
        return
        
    with open("data/await_confirmation.json", "r") as f:
        await_conf = json.load(f)

    for elem in await_conf:
        if player_id in elem["players"]:
            await ctx.reply("!!! Your game's result has already been saved. Please, confirm or reject it. !!!")
            return

    with open("data/pairs.json", "r") as f:
        unresolved = json.load(f)

    for pair in unresolved:
        if player_id in pair:
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
        if player_id in pair:
            opponent = pair[0]
            if opponent == player_id:
                opponent = pair[1]
            break

    await ctx.send(f"{opponent}, confirm that you won {opponent_score} and lost {your_score} games against \
{player_id}.\nTo confirm type /confirm or just wait 2 minutes.\nTo reject type /reject.", delete_after=Constants.CONFIRM_SLEEP)

    with open("data/await_confirmation.json", "r") as f:
        await_conf = json.load(f)
    await_conf.append({"players" : [player_id, opponent], 
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

    with open("data/current_tournament.json", "r") as f:
        data = json.load(f)

    player_id = None
    for i in range(len(data["participants"])):
        if ctx.author.mention in data["participants"][i]:
            player_id = data["participants"][i]
            break
    if player_id is None:
        await ctx.reply("You are not registred")
        return
    
    if timeout:
        speciment = await_conf[0]
        if ctx.author.mention in speciment["players"][0] or ctx.author.mention in speciment["players"][1]:
            score = speciment["score"]
            await_conf.remove(speciment)
            with open("data/await_confirmation.json", "w") as f:
                json.dump(await_conf, f)
            await confirm_game(ctx, speciment["players"][0], speciment["players"][1], score[0], score[1], bot)
            return
    else:
        for speciment in await_conf:
            if player_id in speciment["players"] and player_id == speciment["players"][1]:
                score = speciment["score"]
                await_conf.remove(speciment)
                with open("data/await_confirmation.json", "w") as f:
                    json.dump(await_conf, f)
                await confirm_game(ctx, speciment["players"][0], speciment["players"][1], score[0], score[1], bot)
                break
        else:
            await ctx.reply("You have no pending games.")


@bot.command()
async def reject(ctx):
    with open("data/current_tournament.json", "r") as f:
        data = json.load(f)

    player_id = None
    for i in range(len(data["participants"])):
        if ctx.author.mention in data["participants"][i]:
            player_id = data["participants"][i]
            break
    if player_id is None:
        await ctx.reply("You are not registred")
        return

    with open("data/await_confirmation.json", "r") as f:
        await_conf = json.load(f)
    for speciment in await_conf:
        if player_id in speciment["players"]:
            await_conf.remove(speciment)
            with open("data/await_confirmation.json", "w") as f:
                json.dump(await_conf, f)
            players = speciment["players"]
            await ctx.send(f"{players[0]} VS {players[1]} - game results canceled.\nEnter correct results.")
            break
    else:
        await ctx.reply("You have no active games.")

        
@bot.command() 
async def metagame(ctx):       
    with open("data/metagame.json", "r") as f:
        meta_data = json.load(f)
    if os.path.isfile("data/metagame2vs2.json"):
        with open("data/metagame2vs2.json", "r") as f:
            meta_data_2 = json.load(f)
        for key in meta_data.keys():
            meta_data[key] += meta_data_2[key]

    sort_data = {k: v for k, v in sorted(meta_data.items(), key=lambda item: item[1], reverse=True)}
    summ = 0
    for key in meta_data.keys():
        summ += meta_data[key]
    if summ == 0:
        await ctx.reply("Some error has occured. Ask admins to fix it.")
        return

    ratings = []
    names = []
    percent = []

    color = []

    for key in sort_data:
        if sort_data[key] == 0:
            continue
        ratings.append(sort_data[key])
        names.append(key)
        percent.append(round(sort_data[key] / summ, 3))

        if key in ["Yarida", "Piekron", "Wooyari", "Kibadda", "Pyokorider", "Cannassault", "Charibasa"]:
            color.append("#8496ff")
        elif key in ["Taterazay", "Guardira", "Grenburr", "Tondenga", "Myamsar", "Destrobo", "Bowmunk"]:
            color.append("#f78a18")
        elif key in ["Yumiyacha", "Alosson", "Wondabarappa", "Jamsch", "Oohoroc", "Pingrek", "Cannogabang"]:
            color.append("#9cd721")
        elif key in ["Ragewolf", "Naughtyfins", "Sonarchy", "Ravenous", "Buzzcrave", "Slogturtle", "Covet-hiss"]:
            color.append("#b57df7")
        else:
            color.append("white")



    data = {
        "rating" : ratings,
        "name" : names,
        "percent" : percent 
    }

    fig, ax = matplotlib.pyplot.subplots()
        
    fig.patch.set_visible(False)
    ax.get_xaxis().set_visible(False)
    ax.barh(names[::-1], data["rating"][::-1], color=color[::-1])
    ax.bar_label(ax.containers[-1], fmt=' %d', label_type='edge', color='snow', fontsize=14)

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)

    matplotlib.pyplot.tight_layout()
    matplotlib.pyplot.savefig('metagame.png', transparent=True)

    with open('metagame.png', 'rb') as f:
        picture = discord.File(f)
        await ctx.send(file=picture)

    
    

@bot.command() 
async def metagame_old(ctx):
    with open("data/status.txt", "r") as f:
        STATUS = f.readline()
    with open("data/metagame.json", "r") as f:
        meta_data = json.load(f)
    if os.path.isfile("data/metagame2vs2.json"):
        with open("data/metagame2vs2.json", "r") as f:
            meta_data_2 = json.load(f)
        for key in meta_data.keys():
            meta_data[key] += meta_data_2[key]

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
        line += f"{i + 1}) {part}\n"
        for j in range(len(data['classes'][part])):
            line += f"{j + 1}. {data['classes'][part][j]}\n"
        line += "\n"
    await ctx.send(line)


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
async def print_status(ctx):
    global STATUS
    STATUS = read_status()
    await ctx.reply(STATUS)


@commands.has_permissions(administrator=True)
@bot.command() 
async def show_status(ctx):
    global STATUS
    STATUS = read_status()
    if STATUS == "NONE":
        await ctx.reply("There is no tournament.")
        return
    with open("data/current_tournament.json", "r") as f:
        data = json.load(f)
    line = "TOURNAMENT:\n\n"
    for i, part in enumerate(data["classes"]):
        line += f"{i + 1}) {part}\n"
        for j in range(len(data["classes"][part])):
            line += f"{j + 1}. {data['classes'][part][j]}\n"
        line += "\n"
    line += "\n"
    await ctx.reply(line)


@commands.has_permissions(administrator=True)
@bot.command() 
async def start_reg(ctx, message):
    if message.strip() == "1vs1":
        with open("data/mode.txt", "w") as f:
            f.write("1vs1")
    elif message.strip()[:-2] == "2vs2" :
        with open("data/mode.txt", "w") as f:
            f.write("2vs2")
        pull_size = int(message.strip()[-1])
        with open("data/pull_size.txt", "w") as f:
            f.write(str(pull_size))
    else:
        await ctx.reply(f"Unknown mode: {message}")
        return
    
    global STATUS
    STATUS = "REGISTR"
    with open("data/status.txt", "w") as f:
        f.write("REGISTR")
    
    mode = read_mode()
    if mode == "1vs1":
        with open(f"data/current_tournament.json", "w") as f:
            data = {"participants" : [], "classes" : {}}
            json.dump(data, f)
        await ctx.send("@everyone registration for the 1vs1 tournament starts now.\nType /reg and write names of 3 classes you want to play.\n\
Example: /reg Taterazay Yarida Yumiyacha")
    elif mode == "2vs2":
        with open("data/pull_size.txt", "r") as f:
            pull_size = int(f.readline())
        with open(f"data/current_tournament.json", "w") as f:
            data = {"participants" : [], "classes" : {}}
            json.dump(data, f)
        patapons = get_random_patapons(pull_size)
        line = f"@everyone registration for the 2vs2 tournament starts now.\nType /reg and write tag of your partner and {pull_size} classes you want to play.\n"
        line += "Example: /reg @myfriend"
        for i in range(pull_size):
            line += " " + patapons[i]
        line += ""
        await ctx.send(line)


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
    participants = sorted(part_data["participants"], key=lambda x: get_rating(x, mention=True), reverse=True)
    part_points = {"participants" : participants, "points" : [0] * len(participants)}

    part_number_total = len(participants)
    log_num = int(math.log2(part_number_total))
    if 2 ** log_num != part_number_total:
        log_num += 1
    with open("data/max_rounds.txt", "w") as f:
        f.write(str(log_num))

    with open("data/points.json", "w") as f:
        json.dump(part_points, f)

    with open("data/round_n.txt", "w") as f:
        f.write("0")

    await start_next_round(ctx, no_sort=True, bot=bot)


create_missing_data()
read_status()
with open("data/token.txt", "r") as f:
    token = f.readline()

bot.run(token)