import discord
from discord.ext import commands
from discord.utils import get
from datetime import datetime, timedelta

import json
import random
import asyncio

# Different channels
userserver = "server-name"            # Add your servername
levelchannel = "🏆server-level-ups"   # Add your levelup channel
botchat = "bot-textchat"              # Add botchat (some channel only you can see)

# StreamingRole to check if active
streamingrole = "Streaming"

# Bad words that's not OK writing
badwords = ["bad word", "bad bad word", "etc"]

# Words who DONT give XP
nowords = [".level", ".clear", ".help", ".ask", ".ping", ".rolldice", ".slap", ".poll", ".botsleep", ".botgaming", ".botbuilding", ".rps", ".spin", ".countdown", ".lovetest", ".msgstatus"]

# Textchannels where no XP is given
nowordschannels = ["🏆server-level-ups", "❔commands-help", "🎧music-bots", "welcome", "botchat", "✅rules", "🎰slot-machine"]

# Achievement for messages
messageRoles = ["100Messenger", "500Messenger", "1000Messenger", "2500Messenger", "5000Messenger"]
totalmessages = [100, 500, 1000, 2500, 5000]

lmaowords = ["lmao", "LMAO"]
lolwords = ["lol", "LOL"]
roflwords = ["rofl", "ROFL"]

class userstatus(commands.Cog):
    def __init__(self,client):
        self.client = client

        with open(r"usermessages.json", "r") as f:
            self.usermessages = json.load(f)

        self.client.loop.create_task(self.checkstream())
        self.client.loop.create_task(self.save_messages())

    async def save_messages(self):
        await self.client.wait_until_ready()
        while not self.client.is_closed():
            with open(r"usermessages.json", "w") as f:
                json.dump(self.usermessages, f, indent=4)

            await asyncio.sleep(5)


    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        words = str(message.content)
        for word in badwords:
            if word in words:
                await message.channel.purge(limit = 1)
                await message.channel.send(f"Bad word! {message.author.mention}")
                return

        for word in lmaowords:
            if word in words:
                await message.channel.send(f"Learn to write {message.author.mention}, you mean 'laughing my ass off', right?")

        for word in lolwords:
            if word in words:
                await message.channel.send(f"Oh my god {message.author.mention}... you mean 'laughing out loud'?")

        for word in roflwords:
            if word in words:
                await message.channel.send(f"Ye ye ye, haha. *Rolling on the floor laughing*.. at you {message.author.mention}")

        for word in nowords:
            if word in words:
                return

        if message.channel.name in nowordschannels:
            return

        author_id = str(message.author.id)
        if not author_id in self.usermessages:
            self.usermessages[author_id] = {}
            self.usermessages[author_id]["messages"] = 0

        self.usermessages[author_id]["messages"] += 1

        for i in range(len(totalmessages)):
            if self.usermessages[author_id]["messages"] == totalmessages[i]:
                role = get(message.author.guild.roles, name = messageRoles[i])
                await message.author.add_roles(role)
                embed = discord.Embed(title=f"Congratz! You got a new role.")
                embed.add_field(name = "Member", value = f"{message.author.mention}", inline= True)
                embed.add_field(name = "New role", value = f"{messageRoles[i]}", inline= True)
                embed.set_thumbnail(url=message.author.avatar_url)
                for guild in self.client.guilds:
                    if guild.name == userserver:
                        for channel in guild.text_channels:
                            if channel.name == levelchannel:
                                await channel.send(embed=embed)

    async def checkstream(self):
        await self.client.wait_until_ready()
        while not self.client.is_closed():
            for server in self.client.guilds:
                if server.name == userserver:
                    for channel in server.voice_channels:
                        for member in channel.members:
                            voice = member.voice
                            if voice.self_stream == True:
                                for role in member.roles:
                                    if str(role.name) == streamingrole:
                                        return
                                    else:
                                        role = get(member.guild.roles, name = streamingrole)
                                        await member.add_roles(role)

                            if voice.self_stream == False:
                                for role in member.roles:
                                    if role.name == streamingrole:
                                        roledelete = get(member.guild.roles, name = streamingrole)
                                        await member.remove_roles(roledelete)

            for server in self.client.guilds:
                if server.name == userserver:
                    for member in server.members:
                        if member.voice == None:
                            for role in member.roles:
                                if str(role.name) == streamingrole:
                                    roledelete = get(member.guild.roles, name = streamingrole)
                                    await member.remove_roles(roledelete)

            await asyncio.sleep(3)


    @commands.command()
    async def msgstatus(self, ctx, member: discord.Member = None):
        member = ctx.author if not member else member
        author_id = str(member.id)

        if author_id in self.usermessages:
            messages = str(self.usermessages[author_id]["messages"])

            embed = discord.Embed(color = 0x15c114, title=f"{member.name}'s Messagestatus")
            embed.add_field(name = "Messages sent:", value = f"{messages}", inline= True)

            roles = member.roles
            currentRole = "None"
            nextRole = "None"

            for role in roles:
                for x, msgroles in enumerate(messageRoles):
                    if str(role) == str(msgroles):
                        currentRole = str(role)
                        nextRole = messageRoles[x+1]
                        break

            if currentRole == "None":
                embed.add_field(name = "Current message role:", value = f"{currentRole}", inline= False)
                embed.add_field(name = "Next message role:", value = f"{messageRoles[0]}", inline= False)
            else:
                embed.add_field(name = "Current message role:", value = f"{currentRole}", inline= False)
                if nextRole == "None":
                    embed.add_field(name = "Next message role:", value = f"{nextRole}", inline= False)
                else:
                    embed.add_field(name = "Next message role:", value = f"{nextRole}", inline= False)

            embed.set_thumbnail(url=member.avatar_url)
            await ctx.channel.send(embed=embed)


def setup(client):
    client.add_cog(userstatus(client))
