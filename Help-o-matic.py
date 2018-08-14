import discord
from discord.ext import commands
import random

description = '''An example bot to showcase the discord.ext.commands extension
module.
There are a number of utility commands being showcased here.'''
bot = commands.Bot(command_prefix='!', description=description)

# permissions integer = 67584

client = discord.Client()

@client.event
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

    result = ', '.join(str(random.randint(1, limit)) for r in range(rolls))
    await bot.say(result)

@bot.command()
async def split(names : str, num : int):
    avg = len(names) / float(num)
    out = []
    last = 0.0

    random.shuffle(names)
    while last < len(names):
        out.append(names[int(last):int(last + avg)])
        last += avg

    for i in range(num):
        printable = "Team " + str(i + 1) + ": "
        for j in range(len(out[i])):
            printable += out[i][j]
            if j < (len(out[i]) - 1):
                printable += ", "
        bot.say(printable)

print("let's try this!")
client.run('NDc4NjcxMjkwMDk0MzIxNjY5.DlOHaA.aqi7y0o0xhKOK04RnzQzBQ0Ha7o')