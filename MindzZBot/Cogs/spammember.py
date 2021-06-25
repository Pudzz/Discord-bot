import discord
from discord.ext import commands
from discord.utils import get

import json
import asyncio
import random

# What you want the bot to spam
spamming = ["Shit yourself", "Bla bla bla bla", "You are boring"]

class spammember(commands.Cog):
    def __init__(self, client):
        self.client = client

        with open(r"userspam.json", "r") as f:
            self.userspam = json.load(f)

        self.client.loop.create_task(self.save_userspam())

    async def save_userspam(self):
        await self.client.wait_until_ready()
        while not self.client.is_closed():
            with open(r"userspam.json", "w") as f:
                json.dump(self.userspam, f, indent=4)

            await asyncio.sleep(5)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        author_id = str(message.author.id)
        if author_id in self.userspam:
            if self.userspam[author_id]["spamming"] == 1:
                await message.channel.send(f"{random.choice(spamming)}, {message.author.mention}.")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def spam(self, ctx, *, member: discord.Member = None):
        member = ctx.author if not member else member
        author_id = str(member.id)

        if not author_id in self.userspam:
            self.userspam[author_id] = {}
            self.userspam[author_id]["spamming"] = 0

        self.userspam[author_id]["spamming"] = 1
        await ctx.channel.send(f"{member.mention} is gonna get spammed.")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def unspam(self, ctx, member: discord.Member = None):
        member = ctx.author if not member else member
        author_id = str(member.id)

        if not author_id in self.userspam:
            self.userspam[author_id] = {}
            self.userspam[author_id]["spamming"] = 0

        self.userspam[author_id]["spamming"] = 0
        await ctx.channel.send(f"{member.mention} not gonna get spammed anymore.")

def setup(client):
    client.add_cog(spammember(client))
