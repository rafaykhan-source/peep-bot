import config
import json
import preprocessing as pp
import pandas as pd
import discord
from discord.ext import commands

############################################
# Bot Intialization
############################################
# permissions
intents = discord.Intents.all()

# bot instance
bot = commands.Bot(command_prefix='/', intents=intents)

# loading up database
data = open('messages.json')
db = json.load(data)
data.close()

# bot connection message
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')

############################################
# Events
############################################

############################################
@bot.event
async def on_member_join(member):
    await member.send(db['welcomeMsg'])

############################################
# Commands 
############################################

############################################
@bot.command(pass_context=True)
async def peep(ctx):
    """Marshmallow responds with peep!"""
    await ctx.send("peep!")
    
############################################
@bot.command(pass_context=True)
@commands.has_any_role("SIFP Discord Admin", "Tech PAI-CA")
async def assign(ctx):
    groups = pp.get_role_data()
    
    for i, group in groups.iteritems():
        r = discord.utils.find(lambda r: r.name == group, ctx.guild.roles)
        if r is None:
            await ctx.send(f"Role corresponding with {group} could not be found.")
            continue
        
    await autoassign(ctx)
    await ctx.send("Task Completed.")
    
############################################ 
async def autoassign(ctx):
    await ctx.send(f"""
*Starting Role Assignments.*
""")
    mentees = pp.get_mentee_data()
    already = found = 0
    not_found = []
    for index, row in mentees.iterrows():
        role = row['group_role']
        name = row['mentee']
        c_name = row['clean_name']
        m = discord.utils.find(lambda m: c_name in pp.clean_name(m.display_name),
                               ctx.guild.members)
        if m is None:
          not_found.append((name, role))
          continue
      
        if role in m.roles:
          print(f"{m.display_name} ALREADY has {role}")
          already += 1
          found += 1
        else:
          await m.add_roles(role)
          await ctx.send(f"{m.display_name} was newly ASSIGNED {role}")
          found += 1 
        
    if len(not_found):
        await ctx.send("Not Found:")
        await ctx.send("\n".join(not_found))
        
    await ctx.send(f"""
*Finished Role Assignments.*
```
---Assignment Report---
People Found: {found}
People Already With Role: {already}
People Not Found: {len(not_found)/2}
```
""")

bot.run(config.TOKEN)

