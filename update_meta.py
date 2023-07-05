import discord
from discord.ext import commands
from discord.ext.commands import CommandNotFound
import json
import codecs
import math
import asyncio
from random import randint
import matplotlib.pyplot
from datetime import datetime
from PIL import Image, ImageFont, ImageDraw


COLOR = 'white'
matplotlib.pyplot.rcParams['text.color'] = COLOR
matplotlib.pyplot.rcParams['axes.labelcolor'] = COLOR
matplotlib.pyplot.rcParams['xtick.color'] = COLOR
matplotlib.pyplot.rcParams['ytick.color'] = COLOR

from constants import Constants
from functions import *
from async_functions import *

        
def metagame():       
    
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
        print("Some error has occured. Ask admins to fix it.")
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

    
metagame()
