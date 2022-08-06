import os
from dotenv import load_dotenv
import discord

def configure():
  load_dotenv()

# initializing bot
client = discord.Client()

# printing bot's servers
print(client.guilds) # broken attribute

@client.event
async def on_ready():
    print(f"{client.user} is online!")

@client.event
async def on_message(message):
    # ensuring bot isn't reading its own messages
    if message.author == client.user:
        return
    
    # peep command
    if 'peep' in message.content:
        await message.channel.send("peep!")
        print(message.content)
        return
    
    # staff supremacy
    if 'Staff' in str(message.author.roles):
        print(message.content)
        await message.add_reaction('❤️')
        return
    
    

configure()
client.run(os.environ['strong'])