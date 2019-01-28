import discord
from discord.ext import commands
import random

with open("token.txt", 'r') as token_file:
    TOKEN = token_file.read()

HEROES = [
        'D.Va', 'Orisa', 'Reinhardt', 'Roadhog', 'Winston', 'Wrecking Ball', 'Zarya', 'Ashe', 'Bastion', 'Doomfist', 'Genji', 'Hanzo', 'Junkrat', 'McCree', 'Mei',
        'Pharah', 'Reaper', 'Solider: 76', 'Sombra', 'Symmetra', 'Torbjorn', 'Tracer', 'Widowmaker', 'Ana', 'Brigitte', 'Lucio', 'Mercy', 'Moira', 'Zenyatta'
    ]

ADJECTIVES = [
    'good', 'bad', 'great', 'terrible', 'a miracle', 'catastrophic', 'sexy', 'praiseworthy', 'the worst thing ever'
]

description = '''A helper bot, designed mostly to help overwatch teams in discord channels.'''
bot = commands.Bot(command_prefix='!', description=description)

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')

@bot.command()
async def roll(dice : str):
    """Rolls a dice in NdN format."""
    try:
        rolls, limit = map(int, dice.split('d'))
    except Exception:
        await bot.say('Format has to be in NdN!')
        return

    if limit > 0 and rolls > 0 and limit < 500 and rolls < 500:
        roll_results = [random.randint(1, limit) for r in range(rolls)]
        result = ', '.join([str(x) for x in roll_results])
        if rolls < 2:
            await bot.say(result)
        else:
            await bot.say(result + "\nTotal: " + str(sum(roll_results)))
    else:
        await bot.say('Illegal combination!')

@bot.command(name="opinion", description="states the bot's opinion on the listed item", brief="states the bot's opinion")
async def opinion(*items : str):
    item = ' '.join(map(str, items))
    while item[-1] == " ":
        item = item[:-1]
    if item == "Adam":
        await bot.say("I think Adam is a genius. Christ, what a man.")
    elif item == "Alex":
        await bot.say("I think Alex is *sick as eggs*.")
    else:
        await bot.say("I think " + item + " is " + random.choice(ADJECTIVES))

@bot.command(pass_context=True)
async def repeat(ctx, times : int, content='repeating...'):
    """Repeats a message multiple times."""
    if ctx.message.author.name != "Adam":
        if times > 5: times = 5
    for i in range(times):
        await bot.say(content)

@bot.command(name="choose", description="chooses a random item from the given parameters, or (if no parameters) from the voice channel the invoker is in", brief="chooses randomly", pass_context=True)
async def choose(ctx, *args):
    items = []
    if len(args) > 0:
        for item in args:
            items.append(item)
        await bot.say("The chosen one is: " + random.choice(items))
        return
    else:
        try:
            invoker = ctx.message.author
            items = invoker.voice.voice_channel.voice_members
            await bot.say("The chosen one is: " + random.choice(items).mention)
            return
        except AttributeError:
            await bot.say("You're not in a voice channel!")
            return

@bot.command(pass_context=True, brief="chooses an overwatch hero for you to play", description="chooses an overwatch hero for you to play")
async def whathero(ctx):
    await bot.say(ctx.message.author.mention + ", you should play " + random.choice(HEROES))

@bot.command(pass_context=True, brief="chooses an overwatch hero for everyone in your voice channel", description="if you're in a voice channel, assigns an overwatch hero for everyone to play with no duplicates")
async def whatheroes(ctx):
    heroes = HEROES
    try:
        names = ctx.message.author.voice.voice_channel.voice_members
    except AttributeError:
        await bot.say("You're not in a voice channel!")
        return

    printable = ""
    for i in range(len(names)):
        try:
            this_hero = random.choice(heroes)
        except IndexError:
            await bot.say("Not enough heroes to go around! I'll allow duplicates.")
            heroes = HEROES
        heroes.remove(this_hero)
        printable += names[i].mention + ": " + this_hero
        if i < len(names) - 1:
            printable += "\n"
    await bot.say(printable)

    
@bot.command(name="divide", description="2 modes:\n1) e.g.: !divide A B C D 2 ->\nTeam 1: B, D\nTeam 2: A, C\n2) !divide N -> this splits all members of your current voice channel into N teams", brief="splits", aliases=["split"], pass_context=True)
async def divide(ctx, *args):
    invoker = ctx.message.author
    
    if len(args) == 1:
        try:
            names = invoker.voice.voice_channel.voice_members
            # for name in names:
            #     print(name.mention)
        except AttributeError:
            await bot.say("You're not in a voice channel!")
            return
        try:
            num = int(args[0])
        except ValueError:
            await bot.say("Number seems wrong! Defaulting to 2. " + ctx.message.author.mention)
            num = 2
    else:
        try:
            num = int(args[-1])
        except ValueError:
            await bot.say("Number seems wrong! Defaulting to 2. " + ctx.message.author.mention)
            num = 2
            args = args[:-1]
        names = []
        for item in args:
            names.append(item)
    avg = len(names) / float(num)
    out = []
    last = 0.0

    if len(names) > (num * 3) or num > 9:
        await bot.say("Hmmm let's not do that, " + ctx.message.author.mention)
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
    await bot.say(printable)

bot.run(TOKEN)