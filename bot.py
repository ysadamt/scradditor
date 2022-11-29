import os
import sqlite3

import discord
from discord.ext import commands
from dotenv import load_dotenv

# get token and guild IDs from .env file
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
GUILD = os.getenv("DISCORD_GUILD")

# give bot all intents
# $ is the command prefix
# remove default help command
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='$', intents=intents, help_command=None)

# connect to database
conn = sqlite3.connect('tracking.db')
cur = conn.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS tracking(subreddits TEXT, keywords TEXT, channel INTEGER)")

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')

@bot.command(name="help")
async def help(ctx):
    embeddedHelp = discord.Embed(title="Help", description="List of commands", color=discord.Color.light_gray())
    embeddedHelp.add_field(name="`$start`", value="Starts tracking", inline=False)
    embeddedHelp.add_field(name="`$end`", value="Stops tracking", inline=False)
    embeddedHelp.add_field(name="`$track`", value="Track a subreddit or keyword. Separate multiple subreddits/keywords with a space.", inline=False)
    embeddedHelp.add_field(name="`$untrack`", value="Untrack a subreddit. Separate multiple subreddits with a space.", inline=False)
    embeddedHelp.add_field(name="`$add`", value="Add a keyword. Separate multiple keywords with a space.", inline=False)
    embeddedHelp.add_field(name="`$remove`", value="Remove a keyword. Separate multiple keywords with a space.", inline=False)
    embeddedHelp.add_field(name="`$current`", value="Show currently tracked subreddits/keywords.", inline=False)
    embeddedHelp.add_field(name="`$setchannel`", value="Set the channel to send posts to. Only one channel can be set at a time.", inline=False)
    embeddedHelp.add_field(name="`$help`", value="Show this help message.", inline=False)

    await ctx.send(embed=embeddedHelp)
