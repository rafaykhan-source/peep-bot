import config
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
# HELPER FUNCTIONS
############################################
def clean_column(col_name: str, df: pd.DataFrame):
    """
    Provided a series name of the dataframe and the dataframe.
    Series associated with column is cleaned and casted as a string
    """
    try:
        names = df[col_name].dropna()
        print(names)
    except:
        print(f"Spreadsheet column, {col_name}, not found.")
    
    return names
    
############################################
async def report_missing(ctx, col_name: str, names: pd.Series):
    await ctx.send(f"""
*Starting {col_name} User Search.*
""")
    found = not_found = 0
    for n in names:
        n = pp.clean_name(n)
        m = discord.utils.find(lambda m: n in pp.clean_name(m.display_name),
                               ctx.guild.members)
        if m is None: 
            await ctx.send(f"Not found: {n}")
            not_found += 1
        else: found += 1
    await ctx.send(f"""
*Finished {col_name} User Search.*
```
---User Search Report---
Found: {found}
Not Found: {not_found}
People in {col_name}: {len(names)}
```
""")
    
############################################ 
async def autoassign(ctx, col_name: str, role: discord.Role, names: pd.Series):
    await ctx.send(f"""
*Starting {col_name} Role Assignments.*
""")
    already = found = 0
    not_found = []
    for n in names:
        nclean = pp.clean_name(n)
        m = discord.utils.find(lambda m: nclean in pp.clean_name(m.display_name),
                               ctx.guild.members)
        if m is None:
          not_found.append(n)
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