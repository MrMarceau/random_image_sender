#!/usr/bin/env python3

import json
from datetime import datetime

import discord.ext.commands
import os, stat

from get_file import rdm

from oauth2client import client, file, tools
from oauth2client.service_account import ServiceAccountCredentials
from httplib2 import Http
from apiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import io

import schedule
import time

# read our environement variables
with open("env.json", "r") as env:
    ENV = json.load(env)

# set our environement variables
IMG_FOLDER = ENV["images_folder"]

GOOGLE_APPLICATION_CREDENTIALS = ENV["google_drive_api_credentials"]
GOOGLE_DRIVE_FOLDER_ID = ENV["google_drive_folder_id"]

COLORS = {
    "BLACK": "\033[30m",
    "RED": "\033[31m",
    "GREEN": "\033[32m",
    "YELLOW": "\033[33m",
    "BLUE": "\033[34m",
    "PURPLE": "\033[35m",
    "CYAN": "\033[36m",
    "GREY": "\033[37m",
    "WHITE": "\033[38m",
    "NEUTRAL": "\033[00m"
}

SIGN = (
    COLORS["RED"] + "/" +
    COLORS["YELLOW"] + "!" +
    COLORS["RED"] + "\\" +
    COLORS["NEUTRAL"] +
    " "
)

def getMemes():
    print('Started downloading files !')
    SCOPES = ['https://www.googleapis.com/auth/drive']

    credentials = ServiceAccountCredentials.from_json_keyfile_name(GOOGLE_APPLICATION_CREDENTIALS, SCOPES)

    http_auth = credentials.authorize(Http())
    drive = build('drive', 'v3', http=http_auth)

    request = drive.files().list(q="'" + GOOGLE_DRIVE_FOLDER_ID + "' in parents").execute()
    files = request.get('files', [])
    counter = 0;

    for f in files:
        fname = f.get('name')
        request = drive.files().get_media(fileId=f.get('id'))
        fh = io.FileIO('./images/' + fname, 'wb')
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            print ("Download ./images/" + fname + " at %d%%." % int(status.progress() * 100))
            os.chmod('./images/' + fname, stat.S_IRUSR | stat.S_IRGRP)
            counter = counter + 1;
    print ("Downloaded " + str(counter) + " files successfully !" )

def DISPLAY_ERROR(error_msg):
    print(
        "\n" +
        SIGN +
        " " +
        COLORS["RED"] +
        error_msg +
        COLORS["NEUTRAL"] +
        "\n"
    )


def log(context):
    channel = context.message.channel
    author = context.message.author

    channel_type = str(channel.type)
    name = author.name
    discriminator = author.discriminator
    nickname = author.display_name

    pseudo = (
        COLORS["RED"] +
        name + "#" + discriminator +
        COLORS["NEUTRAL"] +
        " (aka. " +
        COLORS["BLUE"] +
        nickname +
        COLORS["NEUTRAL"] +
        ")"
    )

    date = "{:04}/{:02}/{:02} {:02}:{:02}:{:02}".format(
        datetime.now().year,
        datetime.now().month,
        datetime.now().day,
        datetime.now().hour,
        datetime.now().minute,
        datetime.now().second
    )
    date = COLORS["PURPLE"] + date + COLORS["NEUTRAL"]

    if channel_type in ["text"]:
        guild = channel.guild

        server = (
            COLORS["GREEN"] +
            guild.name +
            COLORS["NEUTRAL"]
        )
        channel = (
            COLORS["CYAN"] +
            channel.name +
            COLORS["NEUTRAL"]
        )
        where = "on the server {srv} in {chan}".format(
            srv=server,
            chan=channel
        )
    elif channel_type in ["private"]:
        where = "in " + COLORS["GREEN"] + "direct message" + COLORS["NEUTRAL"]
    else:    # channel_type in ["voice", "group", "news", "store"]
        print(
            COLORS["RED"] +
            "This isn't a channel we can send images" +
            COLORS["NEUTRAL"]
        )

    print("{psd} ask for an image {where} at {date}".format(
        psd=pseudo,
        where=where,
        date=date
    ))


# read our discord acces token
with open("secrets.json", "r") as secrets:
    DISCORD_TOKEN = json.load(secrets)["discord"]

bot = discord.ext.commands.Bot(
    command_prefix="¤",
    description="Send a random image"
)


@bot.command(
    name="meme",
    description="Send an image"
)
async def random_image(context):
    log(context)
    if (
        str(context.message.channel.type) == "private" or
        context.message.channel.is_nsfw()
    ):
        try:
            msg_content = {
                "file": discord.File(
                    IMG_FOLDER + "/{}".format(rdm(IMG_FOLDER))
                )
            }
        except FileNotFoundError:
            DISPLAY_ERROR("The folder `{}` was not found".format(IMG_FOLDER))
            msg_content = {
                "content": "The folder with images is missing, sorry..."
            }
        except ValueError:
            DISPLAY_ERROR("The folder `{}` is empty".format(IMG_FOLDER))
            msg_content = {"content": "The folder with images is totaly empty"}
    else:
        msg_content = {"content": "Sorry, this channel isn't a NSFW channel"}

    try:
        await context.send(**msg_content)
    except:
        DISPLAY_ERROR("Somethings went wrong")
        msg_content = {"content": "Somethings went wrons, sorry.\n┬─┬ ︵ /(.□. \）"}
        await context.send(**msg_content)


@bot.event
async def on_ready():
    print(
        COLORS["YELLOW"] +
        "I'm logged in as {name} !\n".format(name=bot.user.name) +
        COLORS["NEUTRAL"]
    )

schedule.every().monday.at("14:00").do(getMemes)
schedule.every().tuesday.at("14:00").do(getMemes)
schedule.every().wednesday.at("14:00").do(getMemes)
schedule.every().thursday.at("14:00").do(getMemes)
schedule.every().friday.at("14:00").do(getMemes)
schedule.every().saturday.at("14:00").do(getMemes)
schedule.every().sunday.at("14:00").do(getMemes)
getMemes()
bot.run(DISCORD_TOKEN)

while True:
    schedule.run_pending()
    time.sleep(10800)
