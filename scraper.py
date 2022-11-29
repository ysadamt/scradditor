import asyncpraw
import discord
import sqlite3
from datetime import datetime

# connect to database
conn = sqlite3.connect('tracking.db')
cur = conn.cursor()

# global variable to act as a trigger to track new submissions 
end = False

async def create_post_embed(submission):
    pass

async def track_new_submissions(channel):
    global end
    end = False

    # select the subreddits column
    # fetch the first row
    cur.execute("SELECT subreddits FROM tracking")
    subs = cur.fetchone() # result can be a tuple or None

    # reddit and subreddit instance have to be in an "async def" function 
    reddit = asyncpraw.Reddit("scraper", user_agent="reddit scraper")
    subreddit = await reddit.subreddit(subs[0])

    # select the keywords column
    # fetch the first row
    cur.execute("SELECT keywords FROM tracking")
    keywords = cur.fetchone() # result can be a tuple or None
    keywordList = keywords[0].split(',')

    # keep checking for new submissions
    async for submission in subreddit.stream.submissions(skip_existing=True):
        # if end is True, that means end_track() was called
        # break out of the stream loop
        if end:
            break

        # TODO: check if keywords in submission title
        if any(word in submission.title.lower() for word in keywordList):
            # create embed
            embeddedPost = await create_post_embed(submission)
            await channel.send(embed=embeddedPost)