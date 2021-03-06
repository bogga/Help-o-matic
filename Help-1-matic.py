import discord, aiohttp
from discord.ext import commands
import random, sqlite3, re, FlagHandler, urllib.request
from bs4 import BeautifulSoup
from datetime import datetime

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

    try:
        res = c.execute("SELECT * FROM adjective_authors").fetchone()
    except sqlite3.OperationalError:
        c.execute("CREATE TABLE adjective_authors (ID INTEGER UNIQUE, discordID varchar(255), FOREIGN KEY(ID) REFERENCES adjectives(ID))")   

async def get_owl_games(url):
    async with aiohttp.ClientSession() as cs:
        marker = 'style'
        games = []

        found = False
        async with cs.get(url) as link_r:
            link_content = await link_r.text()
            link_soup = BeautifulSoup(link_content, features="html.parser")

            tables = link_soup.find_all("table", {"class":True})
            match_tables = []
            for t in tables:
                try:
                    if "matchlist" in t['class']:
                        match_tables.append(t)
                except KeyError:
                    continue

            for match_table in match_tables:
                rows = match_table.find("tbody").find_all("tr")

                for row in rows:
                    if 'class' not in row.attrs:
                        if found:
                            break
                        else:
                            continue

                    match_list_slots = []
                    td = row.find_all("td")

                    match_list_slots.append(td[0])
                    match_list_slots.append(td[-1])
                    
                    try:
                        if marker not in match_list_slots[0].attrs and marker not in match_list_slots[1].attrs:
                            found = True
                            
                            # found first new game
                            team1 = match_list_slots[0].find("span", {"data-highlightingclass",True})["data-highlightingclass"]
                            team2 = match_list_slots[1].find("span", {"data-highlightingclass",True})["data-highlightingclass"]
                            games.append((team1, team2))
                    except KeyError:
                        continue

                if found:
                    return [datetime.now().strftime("%B %d, %Y")] + games
    
    return None

def get_spell(name):
    name = re.sub("[^a-zA-z0-9// ]", "", name)
    ans = spells_cursor.execute("SELECT * FROM spells WHERE spell_name IS \"" + name.lower() + "\"").fetchone()
    return ans

async def get_images(item):
    url = "https://www.bing.com/images/search?q={0}".format(item)
    async with aiohttp.ClientSession() as cs:
        async with cs.get(url) as r:
            content = await r.text()
            soup = BeautifulSoup(content, features="html.parser")
            images = soup.find_all('a', {"class":True})

            images = [i for i in images if "thumb" in i['class']]
            for i in images:
                i['href'] = i['href'].replace(" ", "%20")

            return images

    return []

@bot.command(name="games", brief="lists the next set of OWL games", description="lists the next set of OWL games from the given page")
async def games(ctx, url):
    if url == "" or url == None:
        await ctx.send("You need a url!")
        return

    next_games = await get_owl_games(url)
    if next_games == None:
        await ctx.send("No games found at that url.")
        return
    
    temp_games = ["{0} vs {1}".format(i[0], i[1]) for i in next_games[1:]]
    string = "\n".join(temp_games)

    await ctx.send(string)

@bot.command(name="spell", brief="gives spell details from PFSRD", description="gives important details from spells from PFSRD - no ACG.")
async def spell(ctx, *names : str):
    for name in names:
        details = get_spell(name)
        if details is None:
            while name[-1] is " ":
                name = name[:-1]
            await ctx.send(name + " not found!")
            continue
        sep = "=========================="
        response = "**{name}**: {desc}\nCasting time: {time}\nRange: {range}\nSR: {sr}\nComponents: {components}".format(name=details[0], desc=details[4], time=details[7], sr=details[6], range=details[9], components=details[11])
        await ctx.send(sep + "\n" + response)
        full = details[1]
        if len(full) >= 2000:
            remaining = len(full)
            point = 2000
            await ctx.send("\nFull:")
            while remaining > 0:
                while full[point] != " ":
                    point -= 1
                await ctx.send(full[:point])
                full = full[point + 1:]
                remaining = len(full)
                if remaining < 2000:
                    await ctx.send(full)
                    await ctx.send(sep)
                    break
        else:
            await ctx.send("\nFull: {full}".format(full=details[1]) + "\n" + sep)

@bot.command(name="roll", brief="rolls a dice in NdN format", description="rolls a dice in NdN format. E.g. !roll 3d6")
async def roll(ctx, dice : str):
    try:
        rolls, limit = map(int, dice.split('d'))
    except Exception:
        await ctx.send('Format has to be in NdN!')
        return

    if limit > 0 and rolls > 0 and limit < 500 and rolls < 500:
        roll_results = [random.randint(1, limit) for r in range(rolls)]
        result = ', '.join([str(x) for x in roll_results])
        if rolls < 2:
            await ctx.send(result)
        else:
            await ctx.send(result + "\nTotal: " + str(sum(roll_results)))
    else:
        await ctx.send('Illegal combination!')

@bot.command(name="invite", description="replies with an invite link for the bot to join your server!", brief="replies with an invite link")
async def invite(ctx):
    link = "https://discordapp.com/oauth2/authorize?client_id={0}&scope=bot&permissions=0".format(bot.user.id)
    await ctx.send("Follow this link to add me to your server!")
    await ctx.send(link)

@bot.command(name="image", brief="returns an image!", description="returns the first image that you searched for!")
async def image(ctx, *items):
    item = ' '.join(map(str, items))
    item = item.replace(" ", "%20")
    images = await get_images(item)

    if len(images) > 0:
        await ctx.send(images[0]['href'])
        return

    await ctx.send("Couldn't find anything!")
            
@bot.command(name="randomImage", brief="returns an image!", description="returns a random image from results that you searched for!")
async def randomImage(ctx, *items):
    item = ' '.join(map(str, items))
    item = item.replace(" ", "%20")
    images = await get_images(item)

    if len(images) > 0:
        index = random.randint(0, len(images))
        await ctx.send(images[index]['href'])
        return

    await ctx.send("Couldn't find anything!")

@bot.command(name="dumbQuote", description="says the thing again as a dumb quote", brief="dUMbqUOTe")
async def dumbQuote(ctx, *items):
    item = ' '.join(map(str, items))
    item = item.lower()
    new_str = ""
    for i, letter in enumerate(item):
        if i % 2 == 0:
            if not letter.isupper():
                new_str += letter.upper()
            else:
                new_str += letter.lower()
        else:
            new_str += letter
    if len(new_str) > 2000:
        await ctx.send("TOO LONG")
        return
    await ctx.send(new_str)

@bot.command(name="emojify", description="swaps all letters with their emoji version", brief="EMOJI")
async def emojify(ctx, *items):
    item = ' '.join(map(str, items))
    new_str = ""
    for letter in item:
        if letter.isalpha():
            new_str += ":regional_indicator_{0}:".format(letter.lower())
        else:
            new_str += letter
    if len(new_str) > 2000:
        await ctx.send("TOO LONG")
        return
    await ctx.send(new_str)

@bot.command(name="bthis", description="swaps all vowels with their respective emoji", brief=":b: :b: :b:")
async def bthis(ctx, *items):
    item = ' '.join(map(str, items))
    new_str = ""
    for letter in item:
        if letter.lower() in "aeiou":
            new_str += ":regional_indicator_{0}:".format(letter.lower())
        else:
            new_str += letter
    if len(new_str) > 2000:
        await ctx.send("TOO LONG")
        return
    await ctx.send(new_str)

@bot.command(name="listOpinions", description="lists all potential opinions on this server", brief="lists all potential opinions on this server", pass_context=True, no_pm=True)
async def listOpinions(ctx):
    c = adj_conn.cursor()
    server_id = ctx.message.guild.id
    res = c.execute("SELECT adjective FROM adjectives WHERE (server_id IS '{0}' OR server_id IS 'base')".format(server_id)).fetchall()
    opinions = [item[0] for item in res]
    string = ", ".join(opinions)
    message = "Here are my opinions available on this server:\n{0}".format(string)
    if len(message) >= 2000:
            remaining = len(message)
            point = 2000
            while remaining > 0:
                while message[point] != " ":
                    point -= 1
                await ctx.send(message[:point])
                message = message[point + 1:]
                remaining = len(message)
                if remaining < 2000:
                    await ctx.send(message)
                    break
    else:
        await ctx.send(message)

@bot.command(name="whoAdded", description="returns the user who added that option to potential opinions", brief="returns the user who added that option to potential opinions", pass_context=True, no_pm=True)
async def whoAdded(ctx, *items : str):
    item = ' '.join(map(str, items))
    while item[-1] == " ":
        item = item[:-1]
    item = re.sub("[^a-zA-Z0-9 ',\"]", "", item)
    item_nums = re.sub("[^0-9]", "", item)
    if len(item) > 254:
        await ctx.send("Too long winky face")
        return
    if items == None or items.count(" ") == len(items) or item_nums == item:
        await ctx.send("Bad opinion! Wrong! Stop!")
        return
    c = adj_conn.cursor()
    server_id = ctx.message.guild.id
    res = c.execute("SELECT ID FROM adjectives WHERE (server_id IS '{0}' OR server_id IS 'base') AND adjective IS \"{1}\"".format(server_id, item)).fetchone()
    if res == None:
        await ctx.send("Opinion not found!")
        return
    opinionID = int(res[0])
    authorID = c.execute("SELECT discordID from adjective_authors WHERE ID IS '{0}'".format(opinionID)).fetchone()
    if authorID != None:
        name = authorID[0]
        await ctx.send("Option {0} added by {1}".format(item, name))
    else:
        await ctx.send("Sorry, the archives are incomplete.")

@bot.command(name="addOpinion", description="adds an option to the bot's opinions (for this server)", brief="adds an option to the bot's opinions (for this server)", pass_context=True, no_pm=True)
async def addOpinion(ctx, *items : str):
    item = ' '.join(map(str, items))
    while item[-1] == " ":
        item = item[:-1]
    item = re.sub("[^a-zA-Z0-9 ',\"]", "", item)
    item_nums = re.sub("[^0-9]", "", item)
    if len(item) > 254:
        await ctx.send("Too long winky face")
        return
    if items == None or items.count(" ") == len(items) or item_nums == item:
        await ctx.send("Bad opinion! Wrong! Stop!")
        return
    c = adj_conn.cursor()
    server_id = ctx.message.guild.id
    if c.execute("SELECT * FROM adjectives WHERE (server_id IS '{0}' OR server_id IS 'base') AND adjective IS \"{1}\"".format(server_id, item)).fetchall() != []:
        await ctx.send("Opinion already found")
        return
    opinion_id = c.execute("SELECT MAX(ID) from adjectives").fetchone()[0] + 1
    c.execute("INSERT INTO adjectives VALUES ({0}, '{1}', \"{2}\")".format(opinion_id, server_id, item))
    c.execute("INSERT INTO adjective_authors VALUES ({0}, '{1}')".format(opinion_id, ctx.message.author.mention))
    adj_conn.commit()
    await ctx.send("Added {0} to potential opinions for this server".format(item))

@bot.command(name="removeOpinion", description="removes an option from the bot's opinions (for this server)", brief="removes an option from the bot's opinions (for this server)", pass_context=True, no_pm=True)
async def removeOpinion(ctx, *items : str):
    item = ' '.join(map(str, items))
    while item[-1] == " ":
        item = item[:-1]
    item = re.sub("[^a-zA-Z0-9 ',\"]", "", item)
    item_nums = re.sub("[^0-9]", "", item)
    if len(item) > 254:
        await ctx.send("Too long winky face")
        return
    if items == None or items.count(" ") == len(items) or item_nums == item:
        await ctx.send("Bad opinion! Wrong! Stop!")
        return
    c = adj_conn.cursor()
    server_id = ctx.message.guild.id
    adjID = c.execute("SELECT ID FROM adjectives WHERE server_id IS '{0}' AND adjective IS \"{1}\"".format(server_id, item)).fetchall()
    if adjID == []:
        await ctx.send("Opinion not found")
        return
    adjID = adjID[0][0]
    c.execute("DELETE FROM adjectives WHERE adjective IS \"{0}\" AND server_id IS '{1}'".format(item, server_id))
    c.execute("DELETE FROM adjective_authors WHERE ID is {0}".format(adjID))
    adj_conn.commit()
    await ctx.send("Removed {0} as an option for this server".format(item))

@bot.command(name="opinion", description="states the bot's opinion on the listed item", brief="states the bot's opinion", pass_context=True, no_pm=True)
async def opinion(ctx, *items : str):
    name = ctx.message.guild.me.nick
    item = ' '.join(map(str, items))
    while item[-1] == " ":
        item = item[:-1]
    if item == "Adam":
        await ctx.send("I think Adam is a genius. Christ, what a man.")
    elif item == "Alex":
        await ctx.send("I think Alex is *sick as eggs*.")
    elif item == name:
        await ctx.send("I think I'm great. I also think I was designed by a genius.")
    else:
        c = adj_conn.cursor()
        server_id = ctx.message.guild.id
        res = c.execute("SELECT adjective FROM adjectives WHERE server_id IS '{0}' OR server_id IS 'base'".format(server_id)).fetchall()
        await ctx.send("I think " + item + " is " + random.choice(res)[0])

@bot.command(name="repeat", description="repeats the next bits (for God King Adam only)", brief="not for you", pass_context=True)
async def repeat(ctx, times : int, *content : str):
    content = ' '.join(content)
    """Repeats a message multiple times."""
    if ctx.message.author.name == "Adam" and len(content) > 0:
        for _ in range(times):
            await ctx.send(content)
    else:
        await ctx.send("I'm sorry Dave, I'm afraid I can't do that.")

@bot.command(name="choose", description="chooses a random item from the given parameters, or (if no parameters) from the voice channel the invoker is in", brief="chooses randomly", pass_context=True)
async def choose(ctx, *args):
    items = []
    if len(args) > 0:
        for item in args:
            items.append(item)
        await ctx.send("The chosen one is: " + random.choice(items))
        return
    else:
        try:
            invoker = ctx.message.author
            items = invoker.voice.voice_channel.voice_members
            await ctx.send("The chosen one is: " + random.choice(items).mention)
            return
        except AttributeError:
            await ctx.send("You're not in a voice channel!")
            return

@bot.command(pass_context=True, brief="chooses an overwatch hero for you to play", description="chooses an overwatch hero for you to play")
async def whathero(ctx):
    await ctx.send(ctx.message.author.mention + ", you should play " + random.choice(HEROES))

@bot.command(pass_context=True, brief="chooses an overwatch hero for everyone in your voice channel", description="if you're in a voice channel, assigns an overwatch hero for everyone to play with no duplicates")
async def whatheroes(ctx):
    heroes = HEROES
    try:
        names = ctx.message.author.voice.channel.members
    except AttributeError:
        await ctx.send("You're not in a voice channel!")
        return

    printable = ""
    for i in range(len(names)):
        try:
            this_hero = random.choice(heroes)
        except IndexError:
            await ctx.send("Not enough heroes to go around! I'll allow duplicates.")
            heroes = HEROES
        heroes.remove(this_hero)
        printable += names[i].mention + ": " + this_hero
        if i < len(names) - 1:
            printable += "\n"
    await ctx.send(printable)

    
@bot.command(name="divide", description="2 modes:\n1) e.g.: !divide A B C D 2 ->\nTeam 1: B, D\nTeam 2: A, C\n2) !divide N -> this splits all members of your current voice channel into N teams", brief="splits", aliases=["split"], pass_context=True)
async def divide(ctx, *args):    
    if len(args) == 1:
        try:
            names = ctx.message.author.voice.channel.members
            # for name in names:
            #     print(name.mention)
        except AttributeError:
            await ctx.send("You're not in a voice channel!")
            return
        try:
            num = int(args[0])
        except ValueError:
            await ctx.send("Number seems wrong! Defaulting to 2. " + ctx.message.author.mention)
            num = 2
    else:
        try:
            num = int(args[-1])
        except (ValueError, IndexError) as _:
            await ctx.send("Number seems wrong! Defaulting to 2. " + ctx.message.author.mention)
            num = 2
            args = args[:-1]
        names = []
        for item in args:
            names.append(item)
    avg = len(names) / float(num)
    out = []
    last = 0.0

    if num > 9:
        await ctx.send("Hmmm let's not do that, " + ctx.message.author.mention)
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
    await ctx.send(printable)

bot.run(TOKEN)