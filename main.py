import asyncio

import discord
import sqlite3
from threading import Timer
from dotenv import load_dotenv
import os
from utils import create_env_template
import random
from Constants import *
from model import Model


intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

"""Checks for .env file and creates it if it doesn't exist."""
if not os.path.exists(".env"):
    print(".env file not found. Creating a template...")
    create_env_template()
else:
    print(".env file already exists.")

load_dotenv()

con = sqlite3.connect(DATABASE_NAME)
cur = con.cursor()
cur.execute("""
CREATE TABLE IF NOT EXISTS messages (
    message_id INTEGER PRIMARY KEY,
    message_content TEXT,
    time_sent INTEGER,
    classification BOOLEAN
);
""")
con.commit()
con.close()

def execute_sql_query(query, args=None):
    con = sqlite3.connect(DATABASE_NAME)
    cur = con.cursor()

    if args is None:
        res = cur.execute(query)
    else:
        res = cur.execute(query, args)

    res = res.fetchall()
    con.commit()
    con.close()
    return res

def get_table_size():
    res = execute_sql_query("SELECT COUNT(*) FROM messages;")
    return res[0][0]

classifier = Model()
classifier.train()

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

async def add_message_to_db(message):
    message_id = message.id
    message_content = message.content
    time_sent = message.created_at.timestamp()

    red_squares = 0
    green_squares = 0

    for r in message.reactions:
        if r.emoji == AFFIRMATIVE_EMOJI:
            green_squares = r.count
        elif r.emoji == NEGATIVE_EMOJI:
            red_squares = r.count

    classification = red_squares > green_squares

    args = (message_id, message_content, time_sent, classification)
    if red_squares != 1 or green_squares != 1:
        execute_sql_query("INSERT INTO messages VALUES (?,?,?,?)", args)
        classifier.train()
    await message.add_reaction(LOCKED_EMOJI)

def add_message_to_db_sync(message,loop):
    asyncio.run_coroutine_threadsafe(add_message_to_db(message), loop)

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if len(message.content) > 0:
        message_content = message.content
        message_prefix = message_content[0]
        message_content = message_content[1:]

        if classifier.trained:
            p_nonflag, p_flag = classifier.predict(message.content)
        else:
            p_nonflag = p_flag = 0
        print(p_nonflag, p_flag)
        rng = random.random()
        if message_prefix == PREFIX:
            if message_content.startswith("dbsize"):
                await message.channel.send(get_table_size())
        elif p_nonflag < p_flag or rng <= FLAG_PROBABILITY:
            if rng <= FLAG_PROBABILITY:
                await message.add_reaction(DISCOVER_EMOJI)
            await message.add_reaction(FLAG_EMOJI)
            await message.add_reaction(AFFIRMATIVE_EMOJI)
            await message.add_reaction(NEGATIVE_EMOJI)
            loop = asyncio.get_running_loop()
            Timer(VOTING_TIME, add_message_to_db_sync, args=[message,loop]).start()

ENVIRONMENT = os.environ['ENVIRONMENT']
PROD_KEY = os.environ["PROD_KEY"]
DEV_KEY = os.environ["DEV_KEY"]

if ENVIRONMENT == "prod":
    client.run(PROD_KEY)
elif ENVIRONMENT == "dev":
    client.run(DEV_KEY)
else:
    print("Invalid environment")
