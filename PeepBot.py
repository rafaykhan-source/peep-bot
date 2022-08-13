import os
from dotenv import load_dotenv
import pandas as pd
import discord
from gcsa.google_calendar import GoogleCalendar
import datetime as dt

def configure():
  load_dotenv()
  
# helper method
def verify_admin(messager):
  if 'Admin' not in str(messager.roles):
      raise Exception("Messager must be an Admin")

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
  # ensures that the messager isn't the bot itself
  if message.author == client.user:
    return
  
  # responds 'peep!' to messages containing peep
  if 'peep' in message.content:
    await message.channel.send("peep!")
    print(message.content)
    return
  
  # retrieves discord server 
  server = message.author.guild
  
  """ 
  identifies missing server members based on spreadsheet
  !missing : spreadsheet_column_name
  """
  if message.content.startswith('!missing'):
    # checking if messager is an admin
    verify_admin(message.author)
    # parsing command arguments
    input = message.content.split(' : ') 
    # storing spreadsheet people
    people = list(df[input[1]])
    # identifying missing server members
    for person in people:
      m = discord.utils.find(lambda m : person in m.display_name, server.members)
      if m == None:
        await message.channel.send(f"could NOT find: {person}") 
    return
  
  ''' 
  autoassigns roles based on spreadsheet
  # !autoassign : spreadsheet_role_name : discord_server_role_name
  '''
  if message.content.startswith('!autoassign'):
    # checking if messager is a server admin
    verify_admin(message.author)
    # parsing command arguments
    input = message.content.split(" : ")
    # validating role argument
    role = discord.utils.get(server.roles, name=input[2])
    if role == None:
      await message.channel.send("no such discord role exists")
      return
    # validating spreadsheet column
    try:
      people = list(df[input[1]])
    except:
      await message.channel.send("no such spreadsheet column exists")
      return
    # storing server members and iterating over them
    for person in people:
      m = discord.utils.find(lambda m : person in m.display_name, server.members)
      if m == None: 
        await message.channel.send(f'could NOT find: {person}')
        continue
      if role in m.roles:
        await message.channel.send(f"{person} ALREADY has role {role}")
      else:
        await m.add_roles(role)
        await message.channel.send(f"ASSIGNED {role} to {person}")
    await message.channel.send("Finished.")
    return
  
  if message.content.startswith("!cal"):
    verify_admin(message.author)
    start = dt.datetime.now()
    end = dt.datetime.now().replace(hour=23, minute=59)
    halps_cal = GoogleCalendar(credentials_path="credentials.json", calendar=os.getenv('calendar_id'))
    events_today = "\nToday's HALPS are: "
    for event in halps_cal[start:end:'startTime']:
      events_today += "\n" + str(event.summary)
    await message.channel.send(events_today)
      
    
configure()
client.run(os.getenv('peep'))