import discord
from discord.ext import commands
import random, sqlite3, re, FlagHandler

with open("token.txt", 'r') as token_file:
    TOKEN = token_file.read()

HEROES = [
        'D.Va', 'Orisa', 'Reinhardt', 'Roadhog', 'Winston', 'Wrecking Ball', 'Zarya', 'Ashe', 'Bastion', 'Doomfist', 'Genji', 'Hanzo', 'Junkrat', 'McCree', 'Mei',
        'Pharah', 'Reaper', 'Solider: 76', 'Sombra', 'Symmetra', 'Torbjorn', 'Tracer', 'Widowmaker', 'Ana', 'Brigitte', 'Lucio', 'Mercy', 'Moira', 'Zenyatta'
    ]

ADJECTIVES = [
    'good', 'bad', 'great', 'terrible', 'a miracle', 'catastrophic', 'sexy', 'praiseworthy', 'the worst thing ever'
]

spells_conn = sqlite3.connect("./spells.db")
spells_cursor = spells_conn.cursor()

adj_conn = sqlite3.connect("./adjectives.db")

description = '''A helper bot, designed mostly to help overwatch teams in discord channels.'''
bot = commands.Bot(command_prefix='!', description=description)

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')

    c = adj_conn.cursor()
    try:
        res = c.execute("SELECT * FROM adjectives").fetchall()
        if res == []:
            for i, adj in enumerate(ADJECTIVES):
                c.execute("INSERT INTO adjectives VALUES ({0}, 'base', '{1}')".format(i, adj))
            adj_conn.commit()
    except sqlite3.OperationalError:
        c.execute("CREATE TABLE adjectives (ID INTEGER PRIMARY KEY, server_id varchar(255) NOT NULL, adjective varchar(255) NOT NULL)")
        for i, adj in enumerate(ADJECTIVES):
            c.execute("INSERT INTO adjectives VALUES ({0}, 'base', '{1}')".format(i, adj))
        adj_conn.commit()
    

def get_spell(name):
    name = re.sub("[^a-zA-z0-9// ]", "", name)
    ans = spells_cursor.execute("SELECT * FROM spells WHERE spell_name IS \"" + name.lower() + "\"").fetchone()
    return ans

@bot.command(name="spell", brief="gives spell details from PFSRD", description="gives important details from spells from PFSRD - no ACG.")
async def spell(*names : str):
    for name in names:
        details = get_spell(name)
        if details is None:
            while name[-1] is " ":
                name = name[:-1]
            await bot.say(name + " not found!")
            continue
        sep = "=========================="
        response = "**{name}**: {desc}\nCasting time: {time}\nRange: {range}\nSR: {sr}\nComponents: {components}".format(name=details[0], desc=details[4], time=details[7], sr=details[6], range=details[9], components=details[11])
        await bot.say(sep + "\n" + response)
        full = details[1]
        if len(full) >= 2000:
            remaining = len(full)
            point = 2000
            await bot.say("\nFull:")
            while remaining > 0:
                while full[point] != " ":
                    point -= 1
                await bot.say(full[:point])
                full = full[point + 1:]
                remaining = len(full)
                if remaining < 2000:
                    await bot.say(full)
                    await bot.say(sep)
                    break
        else:
            await bot.say("\nFull: {full}".format(full=details[1]) + "\n" + sep)

@bot.command(name="roll", brief="rolls a dice in NdN format", description="rolls a dice in NdN format. E.g. !roll 3d6")
async def roll(dice : str):
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

@bot.command(name="listOpinions", description="lists all potential opinions on this server", pass_context=True, no_pm=True)
async def listOpinions(ctx):
    c = adj_conn.cursor()
    server_id = ctx.message.server.id
    res = c.execute("SELECT adjective FROM adjectives WHERE (server_id IS '{0}' OR server_id IS 'base')".format(server_id)).fetchall()
    opinions = [item[0] for item in res]
    string = ", ".join(opinions)
    await bot.say("Here are my opinions available on this server:\n{0}".format(string))

@bot.command(name="addOpinion", description="adds an option to the bot's opinions (for this server)", pass_context=True, no_pm=True)
async def addOpinion(ctx, *items : str):
    item = ' '.join(map(str, items))
    while item[-1] == " ":
        item = item[:-1]
    item = re.sub("[^a-zA-Z0-9 ',\"]", "", item)
    item_nums = re.sub("[^0-9]", "", item)
    if len(item) > 254:
        await bot.say("Too long winky face")
        return
    if items == None or items.count(" ") == len(items) or item_nums == item:
        await bot.say("Bad opinion! Wrong! Stop!")
        return
    c = adj_conn.cursor()
    server_id = ctx.message.server.id
    if c.execute("SELECT * FROM adjectives WHERE (server_id IS '{0}' OR server_id IS 'base') AND adjective IS \"{1}\"".format(server_id, item)).fetchall() != []:
        await bot.say("Opinion already found")
        return
    opinion_id = c.execute("SELECT MAX(ID) from adjectives").fetchone()[0] + 1
    c.execute("INSERT INTO adjectives VALUES ({0}, '{1}', \"{2}\")".format(opinion_id, server_id, item))
    adj_conn.commit()
    await bot.say("Added {0} to potential opinions for this server".format(item))

@bot.command(name="removeOpinion", description="removes an option from the bot's opinions (for this server)", pass_context=True, no_pm=True)
async def removeOpinion(ctx, *items : str):
    item = ' '.join(map(str, items))
    while item[-1] == " ":
        item = item[:-1]
    item = re.sub("[^a-zA-Z0-9 ',\"]", "", item)
    item_nums = re.sub("[^0-9]", "", item)
    if len(item) > 254:
        await bot.say("Too long winky face")
        return
    if items == None or items.count(" ") == len(items) or item_nums == item:
        await bot.say("Bad opinion! Wrong! Stop!")
        return
    c = adj_conn.cursor()
    server_id = ctx.message.server.id
    if c.execute("SELECT * FROM adjectives WHERE (server_id IS '{0}' OR server_id IS 'base') AND adjective IS \"{1}\"".format(server_id, item)).fetchall() == []:
        await bot.say("Opinion not found")
        return
    c.execute("DELETE FROM adjectives WHERE adjective IS \"{0}\" AND server_id IS '{1}'".format(item, server_id))
    adj_conn.commit()
    await bot.say("Removed {0} as an option for this server".format(item))

@bot.command(name="opinion", description="states the bot's opinion on the listed item", brief="states the bot's opinion", pass_context=True, no_pm=True)
async def opinion(ctx, *items : str):
    item = ' '.join(map(str, items))
    while item[-1] == " ":
        item = item[:-1]
    if item == "Adam":
        await bot.say("I think Adam is a genius. Christ, what a man.")
    elif item == "Alex":
        await bot.say("I think Alex is *sick as eggs*.")
    else:
        c = adj_conn.cursor()
        server_id = ctx.message.server.id
        res = c.execute("SELECT adjective FROM adjectives WHERE server_id IS '{0}' OR server_id IS 'base'".format(server_id)).fetchall()
        await bot.say("I think " + item + " is " + random.choice(res)[0])

@bot.command(pass_context=True)
async def repeat(ctx, times : int, content='repeating...'):
    """Repeats a message multiple times."""
    if ctx.message.author.name != "Adam":
        for _ in range(times):
            await bot.say(content)
    else:
        await bot.say("I'm sorry Dave, I'm afraid I can't do that.")

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
        except (ValueError, IndexError) as e:
            await bot.say("Number seems wrong! Defaulting to 2. " + ctx.message.author.mention)
            num = 2
            args = args[:-1]
        names = []
        for item in args:
            names.append(item)
    avg = len(names) / float(num)
    out = []
    last = 0.0

    if num > 9:
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