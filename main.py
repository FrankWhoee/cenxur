import discord
import sqlite3
from threading import Timer
from dotenv import load_dotenv
import os
from utils import create_env_template
import random

# CONSTANTS
VOTING_TIME = 600 # How long before voting closes on flagged messages in seconds
AFFIRMATIVE_EMOJI = "🟩"
NEGATIVE_EMOJI = "🟥"
FLAG_EMOJI = "🚩"
DATABASE_NAME = "data.db"
FLAG_PROBABILITY = 0.1 # Probability that a message gets randomly flagged for data collection
PREFIX = "!"

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

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

def add_message_to_db(message):
    con = sqlite3.connect(DATABASE_NAME)
    cur = con.cursor()

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

    cur.execute("INSERT INTO messages VALUES (?,?,?,?)", args)
    con.commit()
    con.close()

def get_table_size():
    con = sqlite3.connect(DATABASE_NAME)
    cur = con.cursor()
    res = cur.execute("SELECT COUNT(*) FROM messages;")
    return res.fetchone()[0]

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith(PREFIX + "dbsize"):
        await message.channel.send(get_table_size())
    elif random.random() <= FLAG_PROBABILITY:
        await message.add_reaction(FLAG_EMOJI)
        await message.add_reaction(AFFIRMATIVE_EMOJI)
        await message.add_reaction(NEGATIVE_EMOJI)
        Timer(VOTING_TIME, add_message_to_db, args=[message]).start()

ENVIRONMENT = os.environ['ENVIRONMENT']
PROD_KEY = os.environ["PROD_KEY"]
DEV_KEY = os.environ["DEV_KEY"]

if ENVIRONMENT == "prod":
    client.run(PROD_KEY)
elif ENVIRONMENT == "dev":
    client.run(DEV_KEY)
else:
    print("Invalid environment")
