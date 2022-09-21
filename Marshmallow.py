import os
import pandas as pd
import discord
from discord.ext import commands

# setting bot permissions
intents = discord.Intents.all()

# creating bot instance
bot = commands.Bot(command_prefix='/', intents=intents)


# logs whether bot has successfully connected
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')

@bot.event
async def on_member_join(member):
    await member.send("""Hello Soon-to-be SIFPeep!
Nicknames must be set to your real first and last name. 
After all, we have to know who you are and who we're talking to! 
You will not be approved if we can't ID you. To change your nickname, 
right-click or tap on your user profile on the right side and edit 
your server profile. There'll be a nickname field you can type in.
""")

# Commands
@bot.command(pass_context=True)
async def peep(ctx):
    """Marshmallow responds with peep!"""
    await ctx.send("peep!")

@bot.command(pass_context=True)
@commands.has_any_role("SIFP Discord Admin", "Tech PAI-CA")
async def autoassign(ctx, spreadsheet_role: str, discord_role: discord.Role, csv_name: str):
    """Autoassigns students under spreadsheet column desired role"""
    if discord_role == None:
        await ctx.send("no such discord role exists")
        return
    
    df = pd.read_csv(csv_name)
    try:
        names = df[spreadsheet_role].astype("string")
    except:
        await ctx.send("no such spreadsheet column exists")
        return

    already = found = not_found = 0
    for n in names:
        m = discord.utils.find(lambda m: n.lower() in m.display_name.lower(),
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


@bot.command(pass_context=True)
@commands.has_any_role("SIFP Discord Admin", "Tech PAI-CA")
async def missing(ctx, column_name: str, csv_name: str):
    """Identifies students missing from discord based on spreadsheet column"""
    df = pd.read_csv(csv_name)
    try:
        names = df[column_name].astype("string")
    except:
        await ctx.send("no such spreadsheet column exists")
        return

    found = not_found = 0
    for n in names:
        m = discord.utils.find(lambda m: n.lower() in m.display_name.lower(),
                               ctx.guild.members)
        if m == None: 
            print(n)
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

bot.run(os.getenv('peep'))