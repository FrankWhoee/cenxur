import discord
import sqlite3
from threading import Timer
from dotenv import load_dotenv
import os
from utils import create_env_template

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

con = sqlite3.connect("data.db")
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
    con = sqlite3.connect("data.db")
    cur = con.cursor()

    message_id = message.id
    message_content = message.content
    time_sent = message.created_at.timestamp()

    red_squares = 0
    green_squares = 0

    for r in message.reactions:
        if r.emoji == "🟩":
            green_squares = r.count
        elif r.emoji == "🟥":
            red_squares = r.count

    classification = red_squares > green_squares

    args = (message_id, message_content, time_sent, classification)

    cur.execute("INSERT INTO messages VALUES (?,?,?,?)", args)
    con.commit()
    con.close()


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    # react to message with a red flag
    await message.add_reaction("🚩")
    await message.add_reaction("🟩")
    await message.add_reaction("🟥")
    Timer(5, add_message_to_db, args=[message]).start()

    if message.content.startswith('$hello'):
        await message.channel.send('Hello!')

ENVIRONMENT = os.environ['ENVIRONMENT']
PROD_KEY = os.environ["PROD_KEY"]
DEV_KEY = os.environ["DEV_KEY"]

if ENVIRONMENT == "prod":
    client.run(PROD_KEY)
elif ENVIRONMENT == "dev":
    client.run(DEV_KEY)
else:
    print("Invalid environment")
