import os
from dotenv import load_dotenv
import pandas as pd
import discord

def configure():
  load_dotenv()

# reading in sample role spreadsheet
df = pd.read_csv('sample.csv')
print(df)

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
  server = message.author.guild
  # ensuring that the messager isn't the bot itself
  if message.author == client.user:
    return
    
  # peep responds to messages containing peep
  if 'peep' in message.content:
    await message.channel.send("peep!")
    print(message.content)
    return
  
  # person verification command
  # !missing : spreadsheet_role_name
  if message.content.startswith('!missing'):
    # checking if messager is a server admin
    if 'Admin' not in str(message.author.roles):
      return
    input = message.content.split(' : ') 
    people = df[input[1]]
    members = server.members
    
    found = []
    for person in people:
      for m in members:
        if person in m.display_name: 
          found.append(person)
          break
    
    for person in people:
      if person not in found:
        await message.channel.send(f"{person} not found")
    return
  
  # autoassign roles command
  # !autoassign : spreadsheet_role_name : discord_server_role_name
  if message.content.startswith('!autoassign'):
    # checking if messager is a server admin
    if 'Admin' not in str(message.author.roles):
      return
    # converting input into a list of arguments
    input = message.content.split(" : ")
    # validating role argument
    role = discord.utils.get(server.roles, name=input[2])
    print(role)
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
      name = str(m.display_name)
      if role in m.roles:
        await message.channel.send(f"{name} already has role {role}")
      elif name in list(people):
        await m.add_roles(role)
        if role in m.roles:
          await message.channel.send(f"assigned {role} to {name}")
        else:
          await message.channel.send(f"failed to assign {role} to {name}")
      else:
        await message.channel.send(f"{name} was not been assigned {role}.")
    await message.channel.send("Finished.")
    return
  
configure()
client.run(os.getenv('peep'))

