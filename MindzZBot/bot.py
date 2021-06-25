import discord
from discord.ext import commands, tasks
from discord.utils import get
from itertools import cycle
from datetime import datetime, timedelta

import json
import os
import random

import time
import sched

client = commands.Bot(command_prefix = '.', intents = discord.Intents.all())
status = cycle(['Rocket League', 'Sea of Thieves', 'FIFA 21', 'Black Desert', 'Among Us', 'Hunt: Showdown', 'GFTO', 'Rainbow Six Siege', 'Farming simulator 19', 'CS:GO'])
sleepstatus = ["sleeping", "im tired, sleeping..", "gnight!", "offline.. maybe"]

# Different channels
userserver = "server-name"           # Add your servername
botchat = "bot-textchat"             # Add botchat (some channel only you can see)
botstatus = "bot-status-textchat"    # For bot-status messages

# welcome variables
welcomechat = "welcome"
startrole = "Member"
streamingrole = "Streaming"

@client.event
async def on_ready():
    change_status.start()
    for guild in client.guilds:
        if guild.name == userserver:
            for channel in guild.text_channels:
                if channel.name == botchat:
                    await channel.send(f'Bot is online!')

@tasks.loop(minutes=180)
async def change_status():
    await client.change_presence(status = discord.Status.online, activity=discord.Game(next(status)))

@client.command()
@commands.has_permissions(administrator=True)
async def botgaming(ctx):
    if ctx.channel.name == botchat:
        change_status.restart()
    else:
        await ctx.channel.purge(limit = 1)

@client.command()
@commands.has_permissions(administrator=True)
async def botsleep(ctx):
    if ctx.channel.name == botchat:
        change_status.stop()
        await client.change_presence(status = discord.Status.idle, activity=discord.Game(random.choice(sleepstatus)))
    else:
        await ctx.channel.purge(limit = 1)

@client.command()
@commands.has_permissions(administrator=True)
async def botbuilding(ctx):
    if ctx.channel.name == botchat:
        change_status.stop()
        await client.change_presence(status = discord.Status.idle, activity=discord.Game("under development"))
    else:
        await ctx.channel.purge(limit = 1)

@client.command()
@commands.has_permissions(administrator=True)
async def botmessage(ctx, message):
    if ctx.channel.name == botchat:
        for guild in client.guilds:
            if guild.name == userserver:
                for channel in guild.text_channels:
                    if channel.name == botstatus:
                        await channel.send(f'{message}')

@client.command()
@commands.has_permissions(administrator=True)
async def botonline(ctx):
    if ctx.channel.name == botchat:
        for guild in client.guilds:
            if guild.name == userserver:
                for channel in guild.text_channels:
                    if channel.name == botstatus:
                        await channel.send(f'Bot is online!')
    else:
        await ctx.channel.purge(limit = 1)

@client.command()
@commands.has_permissions(administrator=True)
async def botoffline(ctx):
    if ctx.channel.name == botchat:
        for guild in client.guilds:
            if guild.name == userserver:
                for channel in guild.text_channels:
                    if channel.name == botstatus:
                        await channel.send(f'Bot is offline!')
                        await client.change_presence(status = discord.Status.invisible, activity=discord.Game("offline"))
    else:
        await ctx.channel.purge(limit = 1)

@client.command()
@commands.has_permissions(administrator=True)
async def botrestarting(ctx):
    if ctx.channel.name == botchat:
        for guild in client.guilds:
            if guild.name == userserver:
                for channel in guild.text_channels:
                    if channel.name == botstatus:
                        await channel.send(f'Bot restarting...')
                        await client.change_presence(status = discord.Status.invisible, activity=discord.Game("restarting"))
    else:
        await ctx.channel.purge(limit = 1)

@client.event
async def on_voice_state_update(member, before, after):
    voice = member.voice
    if not voice == None:
        if voice.self_stream == True:
            for role in member.roles:
                if str(role.name) == streamingrole:
                    return
                else:
                    role = get(member.guild.roles, name = streamingrole)
                    await member.add_roles(role)

        if voice.self_stream == False:
            for role in member.roles:
                if str(role.name) == streamingrole:
                    roledelete = get(member.guild.roles, name = streamingrole)
                    await member.remove_roles(roledelete)

        with open(r"vcstats.json", "r") as f:
            vcstatus = json.load(f)

        author_name = member.name

        if not author_name in vcstatus:
            vcstatus[author_name] = {}
            vcstatus[author_name]["lastchat"] = "1"
            vcstatus[author_name]["time"] = "0"
            vcstatus[author_name]["day"] = "0"

        vcstatus[author_name]["lastchat"] = f"{voice.channel}"

        f = '%H:%M:%S'
        now = datetime.strftime(datetime.now(), f)
        day = datetime.today()
        d2 = day.strftime("%B %d, %Y")

        vcstatus[author_name]["time"] = f"{now}"
        vcstatus[author_name]["day"] = f"{d2}"

        with open(r"vcstats.json", "w") as f:
            json.dump(vcstatus, f, indent=4)

    if voice == None:
        for role in member.roles:
            if str(role.name) == streamingrole:
                roledelete = get(member.guild.roles, name = streamingrole)
                await member.remove_roles(roledelete)

@client.event
async def on_member_join(member):
    for guild in client.guilds:
        if guild.name == userserver:
            for channel in guild.text_channels:
                if channel.name == welcomechat:
                    await channel.send(f'Welcome to MindzZ Discord Server, {member.mention}!')

    role = get(member.guild.roles, name = startrole)
    await member.add_roles(role)
    print(f'{member} has joined a server.')

@client.event
async def on_member_remove(member):
    with open(r"userstatus.json", "r") as f:
        usersss = json.load(f)

    author_id = member.id
    usersss[author_id] = {}
    usersss[author_id]["name"] = str(member.name)

    with open(r"userstatus.json", "w") as f:
        json.dump(usersss, f, indent=4)

    print(f'{member} has left a server.')

# Error handling
@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Please pass in all required arguments.")

    if isinstance(error, commands.CommandNotFound):
        await ctx.send("Command is not active.")

# Load all cogs
for filename in os.listdir('./Cogs'):
    print({filename[:-3]})
    if filename.endswith('.py'):
        client.load_extension(f'Cogs.{filename[:-3]}')


client.run('00000')   # PUT IN YOUR TOKEN
