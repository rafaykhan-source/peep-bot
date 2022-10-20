import os
from dotenv import load_dotenv
import pandas as pd
import discord
from discord.ext import commands

load_dotenv()

############################################
# Bot Intialization
############################################
# permissions
intents = discord.Intents.all()

# bot instance
bot = commands.Bot(command_prefix='/', intents=intents)

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
    await member.send("""Hello Soon-to-be SIFPeep!
Nicknames must be set to your real first and last name. 
After all, we have to know who you are and who we're talking to! 
You will not be approved if we can't ID you. To change your nickname, 
right-click or tap on your user profile on the right side and edit 
your server profile. There'll be a nickname field you can type in.
""")


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
async def autoassign(ctx, column_name: str, discord_role: discord.Role, csv_name: str):
    """Autoassigns students under spreadsheet column desired role"""
    if discord_role == None:
        await ctx.send("no such discord role exists")
        return
    
    df = pd.read_csv(csv_name)
    
    try:
        names = df[column_name].dropna().astype(str)
        print(names)
    except:
        await ctx.send("no such spreadsheet column exists")
        return

    already = found = not_found = 0
    for n in names:
        n_comp1 = n.lower()
        n_comp2 = n.lower().replace(" ", "")
        m = discord.utils.find(lambda m: n_comp1 in m.display_name.lower() 
                               or n_comp2 in m.display_name.lower(),
                               ctx.guild.members)
        if m == None: 
          print(f"could NOT find {n}")
          not_found += 1
        elif discord_role in m.roles:
          print(f"{m.display_name} ALREADY has {discord_role}")
          already += 1
          found += 1
        else:
          await m.add_roles(discord_role)
          await ctx.send(f"{m.display_name} was ASSIGNED {discord_role}")
          found += 1 
    await ctx.send(f"""
```
Done.
Found: {found}
Not Found: {not_found}
Already Had Role: {already}
People in the Discord: {len(ctx.guild.members)}
```
""")

############################################
@bot.command(pass_context=True)
@commands.has_any_role("SIFP Discord Admin", "Tech PAI-CA")
async def missing(ctx, column_name: str, csv_name: str):
    """Identifies students missing from discord based on spreadsheet column"""
    df = pd.read_csv(csv_name)
    try:
        names = df[column_name].dropna().astype(str)
        print(names)
    except:
        await ctx.send("no such spreadsheet column exists")
        return

    found = not_found = 0
    for n in names:
        n_comp1 = n.lower()
        n_comp2 = n.lower().replace(" ", "")
        m = discord.utils.find(lambda m: n_comp1 in m.display_name.lower() 
                               or n_comp2 in m.display_name.lower(),
                               ctx.guild.members)
        if m == None: 
            await ctx.send(f"Not found: {n}")
            not_found += 1
        else: found += 1
    await ctx.send(f"""
```
Done.
Found: {found}
Not Found: {not_found}
People in the Discord: {len(ctx.guild.members)}
```
""")

############################################
@bot.command(pass_context=True)
@commands.has_any_role("SIFP Discord Admin", "Tech PAI-CA")
async def assigngroups(ctx, csv_name: str):
    df = pd.read_csv(csv_name)
    
    for col in df:
        r = discord.utils.find(lambda r: r.name == str(col), ctx.guild.roles)
        if r == None:
            await ctx.send(f"Role corresponding with {str(col)} could not be found.")
            continue
        names = isolate_mentor_group(col, df)   
        await mentor_group_missing(ctx, col, names)
        await mentor_group_autoassign(ctx, col, r, names)

    await ctx.send("Task Completed.")

############################################
# HELPER FUNCTIONS
############################################
def isolate_mentor_group(column_name: str, df: pd.DataFrame):
    try:
        names = df[column_name].dropna().astype(str)
        print(names)
    except:
        print(f"Spreadsheet column, {column_name}, not found. Moving to next Column.")
    
    return names
    
############################################
async def mentor_group_missing(ctx, column_name: str, names: pd.Series):
    await ctx.send(f"""
*Starting {column_name} User Search.*
""")
    found = not_found = 0
    for n in names:
        n_comp1 = n.lower()
        n_comp2 = n.lower().replace(" ", "")
        m = discord.utils.find(lambda m: n_comp1 in m.display_name.lower() 
                               or n_comp2 in m.display_name.lower(),
                               ctx.guild.members)
        if m == None: 
            await ctx.send(f"Not found: {n}")
            not_found += 1
        else: found += 1
    await ctx.send(f"""
*Finished {column_name} User Search.*
```
---User Search Report---
Found: {found}
Not Found: {not_found}
People in {column_name}: {len(names)}
```
""")
    
############################################ 
async def mentor_group_autoassign(ctx, column_name: str, discord_role: discord.Role, names: pd.Series):
    await ctx.send(f"""
*Starting {column_name} Role Assignments.*
""")
    already = found = not_found = 0
    for n in names:
        n_comp1 = n.lower()
        n_comp2 = n.lower().replace(" ", "")
        m = discord.utils.find(lambda m: n_comp1 in m.display_name.lower() 
                               or n_comp2 in m.display_name.lower(),
                               ctx.guild.members)
        if m == None:
          not_found += 1
        elif discord_role in m.roles:
          print(f"{m.display_name} ALREADY has {discord_role}")
          already += 1
          found += 1
        else:
          await m.add_roles(discord_role)
          await ctx.send(f"{m.display_name} was ASSIGNED {discord_role}")
          found += 1 
    
    await ctx.send(f"""
*Finished {column_name} Role Assignments.*
```
---Role Assignment Report---
People Assigned {column_name} Role: {found}
Already Had Role: {already}
People Not Found: {not_found}
People in {column_name}: {len(names)}
```
""")

bot.run(os.environ['TOKEN'])