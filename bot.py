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

