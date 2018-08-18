import discord
from discord import Game
from discord.ext import commands
import random

BOT_PREFIX = "!"
TOKEN = "NDc4NjcxMjkwMDk0MzIxNjY5.DlOHaA.aqi7y0o0xhKOK04RnzQzBQ0Ha7o"

HEROES = [
        'D.Va', 'Orisa', 'Reinhardt', 'Roadhog', 'Winston', 'Wrecking Ball', 'Zarya', 'Bastion', 'Doomfist', 'Genji', 'Hanzo', 'Junkrat', 'McCree', 'Mei',
        'Pharah', 'Reaper', 'Solider: 76', 'Sombra', 'Symmetra', 'Torbjorn', 'Tracer', 'Widowmaker', 'Ana', 'Brigitte', 'Lucio', 'Mercy', 'Moira', 'Zenyatta'
    ]

client = commands.Bot(BOT_PREFIX)

@client.event
async def on_ready():
    await client.change_presence(game=Game(name="with your feelings"))
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

@client.command(name="hello", description="h e l l o", brief="hello", aliases=["hi"], pass_context=True)
async def hello(ctx):
    await client.say("Hello " + ctx.message.author.mention + "!")
    pass

@client.command(name="choose", description="chooses a random item from the given parameters, or (if no parameters) from the voice channel the invoker is in", brief="chooses randomly", pass_context=True)
async def choose(ctx, *args):
    items = []
    if len(args) > 0:
        for item in args:
            items.append(item)
        await client.say("The chosen one is: " + random.choice(items))
        return
    else:
        try:
            invoker = ctx.message.author
            items = invoker.voice.voice_channel.voice_members
            await client.say("The chosen one is: " + random.choice(items).mention)
            return
        except AttributeError:
            await client.say("You're not in a voice channel!")
            return

@client.command(pass_context=True)
async def whathero(ctx):
    await client.say(ctx.message.author.mention + ", you should play " + random.choice(HEROES))

@client.command(pass_context=True)
async def whatheroes(ctx):
    heroes = HEROES
    try:
        names = ctx.message.author.voice.voice_channel.voice_members
    except AttributeError:
        await client.say("You're not in a voice channel!")
        return

    printable = ""
    for name in names:
        this_hero = random.choice(heroes)
        heroes.remove(this_hero)
        printable += name.mention + ": " + this_hero
    await client.say(printable)

    
@client.command(name="divide", description="2 modes:\n1) e.g.: !divide A B C D 2 ->\nTeam 1: B, D\nTeam 2: A, C\n2) !divide N -> this splits all members of your current voice channel into N teams", brief="splits", aliases=["split"], pass_context=True)
async def divide(ctx, *args):
    if len(args) == 1:
        invoker = ctx.message.author

        try:
            names = invoker.voice.voice_channel.voice_members
        except AttributeError:
            await client.say("You're not in a voice channel!")
            return
        try:
            num = int(args[0])
        except ValueError:
            await client.say("Number seems wrong! Defaulting to 2. " + ctx.message.author.mention)
            num = 2
    else:
        try:
            num = int(args[-1])
            args = args[:-1]
        except ValueError:
            await client.say("Number seems wrong! Defaulting to 2. " + ctx.message.author.mention)
            num = 2
        names = []
        for item in args:
            names.append(item)
    avg = len(names) / float(num)
    out = []
    last = 0.0

    if len(names) > (num * 3) or num > 9 or num < 1:
        await client.say("Hmmm let's not do that, " + ctx.message.author.mention)
        return

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
                if j < (len(out[i]) - 1):
                    printable += ", "
            printable += "\n"
    await client.say(printable)

client.run(TOKEN)