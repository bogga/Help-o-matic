import discord
from discord import Game
from discord.ext import commands
import random

BOT_PREFIX = "!"
TOKEN = "NDc4NjcxMjkwMDk0MzIxNjY5.DlOHaA.aqi7y0o0xhKOK04RnzQzBQ0Ha7o"

client = commands.Bot(BOT_PREFIX)

@client.event
async def on_ready():
    await client.change_presence(game=Game(name="with your feelings"))
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

@client.command(name="hello", description="h e l l o", brief="hello", aliases=["hi"])
async def hello():
    pass

@client.command(name="divide", description="splits the given values into n groups", brief="splits", aliases=["split"])
async def divide(name : str, num : int):
    names = name.split(",")
    avg = len(names) / float(num)
    out = []
    last = 0.0

    random.shuffle(names)
    while last < len(names):
        out.append(names[int(last):int(last + avg)])
        last += avg

    printable = ""
    for i in range(num):
        printable += "Team " + str(i + 1) + ": "
        for j in range(len(out[i])):
            if out[i][j][0] == " ":
                out[i][j] = out[i][j][1:]
            if out[i][j][-1] == " ":
                out[i][j] = out[i][j][:-1]
            printable += out[i][j]
            if j < (len(out[i]) - 1):
                printable += ", "
        printable += "\n"
    await client.say(printable)

client.run(TOKEN)