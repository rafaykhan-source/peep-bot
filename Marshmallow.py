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

# loading up moderation data
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
async def assign(ctx, csv_name: str):
    df = pd.read_csv(csv_name, dtype=str)
    print(df)
    
    for col in df:
        r = discord.utils.find(lambda r: r.name == col, ctx.guild.roles)
        if r is None:
            await ctx.send(f"Role corresponding with {col} could not be found.")
            continue
        
        names = clean_column(col, df)
        await autoassign(ctx, col, r, names)

    await ctx.send("Task Completed.")
    
############################################ 
async def autoassign(ctx, col_name: str, role: discord.Role, names: pd.Series):
    await ctx.send(f"""
*Starting {col_name} Role Assignments.*
""")
    mentees = pp.get_mentee_data()
    already = found = 0
    not_found = []
    for index, mentee in mentees.iterrows():
        m = discord.utils.find(lambda m: mentee['clean_name'] in pp.clean_name(m.display_name),
                               ctx.guild.members)
        if m is None:
          not_found.append(mentee['mentee'])
        elif role in m.roles:
          print(f"{m.display_name} ALREADY has {role}")
          already += 1
          found += 1
        else:
          await m.add_roles(role)
          await ctx.send(f"{m.display_name} was ASSIGNED {role}")
          found += 1 
    
    if len(not_found) > 0:
        await ctx.send("People Not Found:")
        await ctx.send("\n".join(not_found))
    await ctx.send(f"""
*Finished {col_name} Role Assignments.*
```
---Role Assignment Report---
People Assigned {col_name} Role: {found}
Already Had Role: {already}
People Not Found: {len(not_found)}
People in {col_name}: {len(names)}
```
""")

bot.run(config.TOKEN)