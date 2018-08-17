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
    # await client.say(str(command))
    pass

@client.command(name="divide", description="splits the given values into n groups", brief="splits", aliases=["split"], pass_context=True)
async def divide(ctx, *args):
    if len(args) == 1:
        invoker = ctx.message.author

        if invoker.voice != None:
            names = invoker.voice.voice_channel.voice_members
        num = int(args[0])
    else:
        try:
            num = int(args[-1])
            args = args[:-1]
        except ValueError:
            num = 2
        names = []
        for item in args:
            names.extend(item)
    avg = len(names) / float(num)
    out = []
    last = 0.0

    random.shuffle(names)
    while last < len(names):
        out.append(names[int(last):int(last + avg)])
        last += avg

    if len(args) != 1:
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
    else:
        printable = ""
        for i in range(num):
            printable += "Team " + str(i + 1) + ": "
            for j in range(len(out[i])):
                printable += out[i][j].mention
            printable += "\n"
    await client.say(printable)

client.run(TOKEN)