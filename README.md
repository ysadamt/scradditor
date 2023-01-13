# Scradditor

Scradditor is a Discord bot that allows you to track new posts for any subreddit. The bot is developed with Python using the discord.py and Async PRAW library. Hosted on Google Cloud Platform.

## Setting up the bot

There are four main steps to set up this bot: creating a Reddit app, creating a Discord app, setting up Google Cloud, and configuring the Python code.

### Creating a Reddit App

1. Navigate to https://www.reddit.com/prefs/apps
2. Click the "create another app..." button
3. Name the app anything you want
4. Select "script" as the application type
5. Click "create app"
6. After the app is created, save the ID under "personal use script"
7. Click "edit"
8. Save the ID next to "secret"

### Creating a Discord App
1. Navigate to the [Discord Developer Portal](https://discord.com/developers/applications)
2. Sign in to your Discord account
3. On the "Applications" page, click on "New Application" on the top right corner
4. Name the app to your liking
5. On the "Bot" page, click on "Add Bot"
6. Toggle all the options in the "Privileged Gateway Intents" section[^1]
7. Click "Reset Token" and save this token somewhere in your local machine

### Setting up Google Cloud
1. Create a Google Cloud account if you haven't already
2. Create a new project with any name
3. Click on "Create a VM" on the project welcome page
4. It will prompt you to create a billing account as it is required to use Google Cloud's [free tier](https://cloud.google.com/free/docs/free-cloud-features#compute)[^2]
5. Set up billing account
6. You should now be at the "Create an instance" page
7. Choose a name for your VM instance
8. For the region, choose either `us-west1`, `us-central1`, or `us-east1`
9. The zone can be any of the ones available
10. For the machine family, choose "GENERAL-PURPOSE"
11. For series, choose `E2`
12. For the series type, choose `e2-micro`
13. Next, at the "Boot disk" section, click "CHANGE"
14. For the OS, choose `Ubuntu`
15. For the version, choose `Ubuntu 22.04 LTS` for `x86/64`
16. Set boot disk type as `Standard persistent disk`
17. Set size to `30` GB, as shown in the free tier documentation
18. Although it might say that you will be charged for creating this instance, you won't

### Preparing the VM
1. Install the gcloud CLI with these [instructions](https://cloud.google.com/sdk/docs/install)
2. In the "VM instances" tab, click on the name of your VM instance
3. Click the dropdown arrow next to the "SSH" button
4. Click "View gcloud command"
5. The command should look something like this:
```
$ gcloud compute ssh --zone "ZONE" "VM_NAME" --project "PROJECT_ID"
```
6. Copy the command and run it in your terminal
7. Now you have your VM running!
8. In your VM terminal, create a new folder for your bot and navigate to the folder
```
$ mkdir YOUR_BOT_NAME
$ cd YOUR_BOT_NAME
```
9. For this step, you can either `git clone` this repo[^3] or manually create each file and copy paste the code
```
$ git clone https://github.com/ysadamt/scradditor.git
```
```
$ touch bot.py
$ touch scraper.py
```
10. If you are doing the second option, do this for `bot.py` and `scraper.py`
    1. Run `vim <filename>`
    2. Type `i` (enter insert mode in Vim)
    3. Paste code using `CTRL V` or right-click
    4. Press `ESC` (exit insert mode)
    5. Type `:w` then `:q` (write the code to file, then quit Vim)

### Creating Environment Variables
1. Create two files
```
$ touch .env
$ touch praw.ini
```
2. Using the Vim instructions above, copy this code to `.env`
```
DISCORD_TOKEN=
DISCORD_GUILD=
```
3. Paste the token you saved when creating a Discord app after `DISCORD_TOKEN=`
4. Similarly, paste the name of your server you plan to use the bot in after `DISCORD_GUILD=`
5. Using the Vim instructions above, copy this code to `praw.ini`
```
[scraper]
client_id=
client_secret=
```
6. Paste the ID you saved when creating a Reddit app after `client_id=`
7. Similarly, paste the secret ID after `client_secret=`

### Running the Bot
1. Run the command `screen`
2. Run `python3 bot.py`
3. Press `CTRL A D`
4. You can exit the VM by running `exit`, and your bot is now running in the background of the VM

## Using the Bot
Run the `$help` command in your server to view all the commands. You can set the subreddits, keywords, and channel to send new submissions in. If you made it this far, congrats! You will now be notified whenever a submission that matches your keywords is posted.

[^1]: This is to give our bot extra permissions

[^2]: Don't worry, you won't be charged if you stay within the limits

[^3]: To `git clone` the repository, you will need to sign in to GitHub in the VM