import os
from dotenv import load_dotenv
import pandas as pd
import discord

def configure():
  load_dotenv()

# reading in sample role spreadsheet
df = pd.read_csv('sample.csv')

# establishing intents
intents = discord.Intents.all()
intents.members = True

# note that client refers to bot itself
# establishing the bot
client = discord.Client(intents = intents)

@client.event
async def on_ready():
  print(f'{client.user} is online!')

@client.event
async def on_message(message):
  messager = message.author
  server = messager.guild
  
  # bot shouldn't be processing its own messages
  if messager == client.user:
    return
    
  # peep command
  if message.content.startswith('peep'):
    await message.channel.send('peep!')
    return
  
  # person verification command
  # !verifymembers : spreadsheet_role_name
  # this function is currently broken
  if message.content.startswith('!verifymembers'):
    input = message.content.split(' : ') 
    people = df[input[1]]
    members = server.members
    
    for person in people:
      for m in members:
        if person in m.display_name: continue
      await message.channel.send(f"{person} could not be found on the server")
    return
  
  # autoassign roles command
  # !autoassign : spreadsheet_role_name : discord_server_role_name
  if message.content.startswith('!autoassign'):
    # checking if messager is a server admin
    admin = discord.utils.get(server.roles, name='Admin')
    if admin not in messager.roles:
      return
    # converting input into a list of arguments
    input = message.content.split(" : ")
    # validating role argument
    role = discord.utils.get(server.roles, name=input[2])
    if role == None:
      await message.channel.send("no such discord role exists")
      return
    # validating spreadsheet column
    try:
      people = df[input[1]]
    except:
      await message.channel.send("no such spreadsheet column exists")
      return
    # storing server members and iterating over them
    members = server.members 
    for m in members:
      name = m.display_name
      if role in m.roles:
        await message.channel.send(f"{name} already has role {role}")
      elif name in people:
        await m.add_roles(role)
        if role in m.roles:
          await message.channel.send(f"assigned {role} to {name}")
        else:
          await message.channel.send(f"failed to assign {role} to {name}")
      else:
        await message.channel.send(f"{name} has not been assigned {role}.")
    await message.channel.send("Finished.")
    return
  
configure()
client.run(os.getenv('peep'))

