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
    # create Embed object
    embedTitle = submission.title
    if len(embedTitle) > 256:
        embedTitle = embedTitle[:253] + "..."
    embed = discord.Embed(title=embedTitle, url=submission.url, color=discord.Color.light_gray())

    # set author
    user = submission.author
    await user.load()   # re-fetches the Redditor object
    embed.set_author(name=user.name, icon_url=user.icon_img)

    # set thumbnail, if the post has one
    if hasattr(submission, "preview"):
        if 'images' in submission.preview:
            thumbnailLink = submission.preview['images'][0]['source']['url']    # gets the thumbnail image link
            embed.set_thumbnail(url=thumbnailLink)

    # create footer that shows the time submitted in UTC
    unixTime = submission.created_utc
    readableTime = datetime.utcfromtimestamp(unixTime).strftime("%Y-%m-%d %H:%M:%S")    # convert unix time to datetime

    # get submission's subreddit and re-fetch the Subreddit object
    sub = submission.subreddit
    await sub.load()

    # footer format: r/<subreddit> • <time>
    # \u2022 is the bullet symbol
    embed.set_footer(text=f"r/{sub.display_name} \u2022 {readableTime}")

    return embed

async def track_new_submissions(channel):
    global end
    end = False

    # select the subreddits column
    # fetch the first row
    cur.execute("SELECT subreddits FROM tracking")
    subs = cur.fetchone() # result can be a tuple or None

    # reddit and subreddit instance have to be in an "async def" function 
    reddit = asyncpraw.Reddit("scraper", user_agent="scradditor")
    reddit.read_only = True
    subreddit = await reddit.subreddit(subs[0])

    # select the keywords column
    # fetch the first row
    cur.execute("SELECT keywords FROM tracking")
    keywords = cur.fetchone() # result can be a tuple or None
    keywordList = keywords[0].split(',')

    # helper flag to break out of while loop
    flag = False

    # keep checking for new submissions
    while True:
        try:
            async for submission in subreddit.stream.submissions(skip_existing=True):
                # if end is True, that means end_track() was called
                # set helper flag to True and break out of the stream loop
                if end:
                    flag = True
                    break

                if any(word in submission.title.lower() for word in keywordList):
                    # create embed
                    embeddedPost = await create_post_embed(submission)
                    await channel.send(embed=embeddedPost)
        # ignore exceptions
        except Exception as e:
            logFile = open("errors.log", "a")
            logFile.write(str(e))
            logFile.close()
            continue
        # break out of while loop
        if flag == True:
            break

async def end_track():
    # set end to True
    # should trigger the if statement inside the for loop in track_new_submissions()
    global end
    end = True