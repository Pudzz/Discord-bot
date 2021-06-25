import random
import discord
from discord.ext import commands
from discord.utils import get
from datetime import datetime, timedelta

import json
import asyncio

import time
import sched

userserver = "server-name"                   # your servername
slotchannel = "🎰slot-machine"              # channelname for slots

class slotmachine(commands.Cog):
    def __init__(self,client):
        self.client = client

        with open(r"slotmachine.json", "r") as f:
            self.users = json.load(f)

        self.client.loop.create_task(self.save_slots())
        self.client.loop.create_task(self.check_time())

        self.nextwinner = "0"

    async def check_time(self):
        await self.client.wait_until_ready()
        while not self.client.is_closed():

            f = '%H:%M:%S'
            now = datetime.strftime(datetime.now(), f)

            if "00:05:00" == now:
                for member in self.users:
                    self.users[member]["turns"] = 0
                    self.users[member]["jackpot"] = 0

                for guild in self.client.guilds:
                    if guild.name == userserver:
                        for channel in guild.text_channels:
                            if channel.name == slotchannel:
                                await channel.send(f'Spins are being restored right now...')
                                await asyncio.sleep(10)
                                await channel.send(f'Spins restored, happy spinning! 🎰')

            await asyncio.sleep(1)

    async def save_slots(self):
        await self.client.wait_until_ready()
        while not self.client.is_closed():
            with open(r"slotmachine.json", "w") as f:
                json.dump(self.users, f, indent=4)

            await asyncio.sleep(3)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def nextwinstate(self, ctx):
        await ctx.channel.send(f"Next win state is: {self.nextwinner}")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def nextwin(self, ctx):
        self.nextwinner = "1"
        await ctx.channel.send("Next spinner will be a winner.")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def resetmemberspin(self, ctx, member: discord.Member = None):
         member = ctx.author if not member else member

         author_id = str(member.id)

         if author_id in self.users:
             self.users[author_id]["turns"] -= 1

             await asyncio.sleep(5)
             for server in self.client.guilds:
                 if server.name == userserver:
                     for channel in server.text_channels:
                         if channel.name == slotchannel:
                             await channel.send(f"You got one spin back, {member.mention}!")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def resetallspins(self, ctx, *, member: discord.Member = None):
        for user in self.users:
            self.users[user]["turns"] = 0
            self.users[user]["jackpot"] = 0

        for server in self.client.guilds:
            if server.name == userserver:
                for channel in server.text_channels:
                    if channel.name == slotchannel:
                        await channel.send(f'Spins are being restored manually right now...')
                        await asyncio.sleep(10)
                        await channel.send(f'Spins restored, happy spinning! 🎰')

    @commands.command()
    async def spin(self, ctx):
        if ctx.channel.name == slotchannel:
            author_id = str(ctx.message.author.id)

            if not author_id in self.users:
                self.users[author_id] = {}
                self.users[author_id]["turns"] = 0
                self.users[author_id]["jackpot"] = 0

            if self.users[author_id]["jackpot"] == 1:
                await ctx.channel.send(f"You already got your bonus for today, {ctx.message.author.mention}! :cowboy: ")
                return

            if self.users[author_id]["jackpot"] == 2:
                await ctx.channel.send(f"You already got your bonus for today, {ctx.message.author.mention}! :cowboy: ")
                return

            await ctx.channel.send(f"Wait five sec.. spinning")
            await asyncio.sleep(5)

            turns = int(self.users[author_id]["turns"])
            turnsleft = 3 - turns - 1
            if not turns == 3:
                self.users[author_id]["turns"] += 1

                signs = [":trophy:", ":cherries:", ":four_leaf_clover:"]

                if self.nextwinner == "0":
                    signone = random.choice(signs)
                    signtwo = random.choice(signs)
                    signthree = random.choice(signs)

                if self.nextwinner == "1":
                    signone = random.choice(signs)
                    signtwo = signone
                    signthree = signone
                    self.nextwinner = "0"

                description = ""
                description += "Row: "
                description += signone + "  |  "
                description += signtwo + "  |  "
                description += signthree + "  "
                embed = discord.Embed(color = 0x38a9f0, title=f"Slot machine [Exp Booster] :slot_machine:", description = description)
                embed.add_field(name = "Player", value = f"{ctx.message.author.mention}", inline= True)
                embed.add_field(name = "Spins left", value = turnsleft, inline= True)

                if signone == signtwo:
                    if signtwo == signthree:
                        if signone == ":trophy:":
                            self.users[author_id]["jackpot"] = 2
                        else:
                            self.users[author_id]["jackpot"] = 1

                        embed.add_field(name = "CONGRATZ", value = "You gain more EXP for today", inline= True)
                    else:
                        embed.add_field(name = "Try again", value = "Better luck next time.", inline= True)
                else:
                    embed.add_field(name = "Try again", value = "Better luck next time.", inline= True)

                embed.set_thumbnail(url=ctx.message.author.avatar_url)
                await ctx.channel.send(embed=embed)
            else:
                await ctx.channel.send(f"Oh.. you don't have any spins left today, {ctx.message.author.mention}. Please try again tomorrow!")
        else:
            await ctx.channel.purge(limit = 1)
            await ctx.channel.send(f"Oh! {ctx.message.author.mention}, please type this in the chat: 🎰slot-machine. Thank you!")


    @commands.command()
    async def boosted(self, ctx):
        if ctx.channel.name == slotchannel:
            await ctx.channel.purge(limit = 1)
            author_id = str(ctx.message.author.id)

            description = "What is an EXP boost? Check '❔commands-help'.."
            embed = discord.Embed(color = 0x15c534, title=f"Todays [EXP BOOST] winners :medal:", description = description)

            onewinner = "| "
            for member in self.users:
                if self.users[member]["jackpot"] == 1:
                    user = await self.client.fetch_user(member)
                    onewinner += f"{user.name} | "

            embed.add_field(name = "1 EXP Winner", value = onewinner, inline= True)


            twowinner = "| "
            for member in self.users:
                if self.users[member]["jackpot"] == 2:
                    user = await self.client.fetch_user(member)
                    twowinner += f"{user.name} | "

            embed.add_field(name = "2 EXP Winner", value = twowinner, inline= False)
            await ctx.channel.send(embed=embed)
        else:
            await ctx.channel.purge(limit = 1)
            await ctx.channel.send(f"Oh! {ctx.message.author.mention}, please type this in the chat: 🎰slot-machine. Thank you!")


    @commands.command()
    @commands.has_permissions(administrator=True)
    async def testspin(self, ctx):
        signs = [":trophy:", ":cherries:", ":four_leaf_clover:"]
        signone = random.choice(signs)
        signtwo = random.choice(signs)
        signthree = random.choice(signs)
        description = ""
        description += "Row: "
        description += signone + "  |  "
        description += signtwo + "  |  "
        description += signthree + "  "
        embed = discord.Embed(color = 0x38a9f0, title=f"TEST Slot machine [Exp Booster] :slot_machine:", description = description)
        embed.add_field(name = "Player", value = f"{ctx.message.author.mention}", inline= True)
        embed.add_field(name = "Spins left", value = "Infinite", inline= True)
        embed.add_field(name = "Test spin", value = "Completed", inline= True)
        await ctx.channel.send(embed=embed)

def setup(client):
    client.add_cog(slotmachine(client))
