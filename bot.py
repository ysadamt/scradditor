import os
import sqlite3

import discord
from discord.ext import commands
from dotenv import load_dotenv

from scraper import track_new_submissions, end_track

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

@bot.command()
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

# command to trigger new submission tracking
@bot.command()
async def start(ctx):
    cur.execute("SELECT channel FROM tracking")
    channelID = cur.fetchone()
    if channelID == None or channelID[0] == None or channelID[0] == 0:
        await ctx.send("No tracking channel provided")
    else:
        await ctx.send("Tracking started!")
        channel = bot.get_channel(channelID[0])
        await track_new_submissions(channel)

# command to trigger new submission tracking
@bot.command()
async def end(ctx):
    await ctx.send("Tracking ended!")
    await end_track()

# command to add subreddits to track
@bot.command()
async def track(ctx, *args):
    # remove duplicates in args
    args = [*set(args)]

    # initialize two empty lists
    # stores not tracked/already tracked subreddit from args
    alreadyTracked = []
    notTracked = []

    # select the subreddits column
    # fetch the first row
    cur.execute("SELECT subreddits FROM tracking")
    subs = cur.fetchone() # result can be a tuple or None

    # if there is a row
    if subs != None:
        if subs[0] == None or subs[0] == "":
            existingSubs = []
        else:
            # existingSubs is a list of subreddit strings split from a longer string with format:
            # "subreddit1+subreddit2+subreddit3"
            existingSubs = subs[0].split('+')
        # loop through args to see which subreddits are already tracked/not tracked
        for subreddit in args:
            if subreddit in existingSubs:
                alreadyTracked.append(subreddit)
            else:
                notTracked.append(subreddit)
        
        # if there are currently no subreddits being tracked, preceding '+' is not required
        if len(existingSubs) == 0:
            # create updatedSubs string
            updatedSubs = '+'.join(notTracked)
        else:
            # create updatedSubs string
            updatedSubs = '+'.join(existingSubs) + '+' + '+'.join(notTracked)
        
        # if args contains any subreddits that are already tracked, then this should execute
        if len(alreadyTracked) > 0:
            await ctx.send(f"Already tracking these subreddit(s): `{', '.join(alreadyTracked)}`")

        # update database
        if len(notTracked) > 0:
            cur.execute("UPDATE tracking SET subreddits=?", (updatedSubs,))
            conn.commit()
    # subs is None; table has no rows
    else:
        # all subreddits in args are not being tracked
        notTracked = args

        # create updatedSubs string
        updatedSubs = '+'.join(notTracked)

        # update database
        cur.execute("INSERT INTO tracking (subreddits) VALUES(?)", (updatedSubs,))
        conn.commit()

    # if there is at least one subreddit in args that is not currently being tracked, then this should execute
    if len(notTracked) > 0:
        await ctx.send(f"Added `{len(notTracked)}` subreddit(s) to track: `{', '.join(notTracked)}`")

@bot.command()
async def untrack(ctx, *args):
    # remove duplicates in args
    args = [*set(args)]

    toUntrack = []
    notCurrentlyTracked = []

    cur.execute("SELECT subreddits FROM tracking")
    subreddits = cur.fetchone() # result can be a tuple or None

    if subreddits != None and subreddits[0] != None and subreddits[0] != "":
        existingSubs = subreddits[0].split('+')

        if len(existingSubs) == 0:
            await ctx.send("No subreddit(s) are currently being tracked")
        else:
            for subreddit in args:
                if subreddit in existingSubs:
                    existingSubs.remove(subreddit)
                    toUntrack.append(subreddit)
                else:
                    notCurrentlyTracked.append(subreddit)
            updatedSubs = '+'.join(existingSubs)

            if len(notCurrentlyTracked) > 0:
                await ctx.send(f"Subreddit(s) not currently being tracked: `{', '.join(notCurrentlyTracked)}`")
            
            if len(toUntrack) > 0:
                cur.execute("UPDATE tracking SET subreddits=?", (updatedSubs,))
                conn.commit()
    else:
        await ctx.send("No subreddit(s) are currently being tracked")
    
    if len(toUntrack) > 0:
        await ctx.send(f"Removed `{len(toUntrack)}` subreddit(s): `{', '.join(toUntrack)}`")

# command to add keywords to track
@bot.command()
async def add(ctx, *args):
    # remove duplicates in args
    args = [*set(args)]

    # initialize two empty lists
    # stores not tracked/already tracked keywords from args
    alreadyTracked = []
    notTracked = []

    # select the keywords column
    # fetch the first row
    cur.execute("SELECT keywords FROM tracking")
    keywords = cur.fetchone() # result can be a tuple or None

    # if there is a row
    if keywords != None:
        # existingWords is a list of keywords strings split from a longer string with format:
        # "keyword1,keyword2,keyword3"
        if keywords[0] == None or keywords[0] == "":
            existingWords = []
        else:
            existingWords = keywords[0].split(',')    

        # loop through args to see which keywords are already tracked/not tracked
        for keyword in args:
            keyword = keyword.lower()
            if keyword in existingWords:
                alreadyTracked.append(keyword)
            else:
                notTracked.append(keyword)
        
        # if there are currently no keywords being tracked, preceding ',' is not required
        if len(existingWords) == 0:
            # create updatedWords string
            updatedWords = ','.join(notTracked)
        else:
            # create updatedWords string
            updatedWords = ','.join(existingWords) + ',' + ','.join(notTracked)
        
        # if args contains any keywords that are already tracked, then this should execute
        if len(alreadyTracked) > 0:
            await ctx.send(f"Already tracking these keywords(s): `{', '.join(alreadyTracked)}`")

        # update database
        if len(notTracked) > 0:
            cur.execute("UPDATE tracking SET keywords=?", (updatedWords,))
            conn.commit()
    # subs is None; table has no rows
    else:
        # all keywords in args are not being tracked
        notTracked = args

        # create updatedWords string
        updatedWords = ','.join(notTracked)

        # update database
        cur.execute("INSERT INTO tracking (keywords) VALUES(?)", (updatedWords,))
        conn.commit()

    # if there is at least one keyword in args that is not currently being tracked, then this should execute
    if len(notTracked) > 0:
        await ctx.send(f"Added `{len(notTracked)}` keyword(s) to track: `{', '.join(notTracked)}`")