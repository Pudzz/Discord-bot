import discord
from discord.ext import commands
from discord.utils import get
from datetime import datetime, timedelta

import json
import asyncio
import random

import time
import sched

# Different channels
userserver = "server-name"                   # your servername
slotchannel = "🎰slot-machine"              # channelname for slots
lotterychannel = "🎲lottery"                # channelname for lottery
levelchannel = "🏆server-level-ups"         # channelname for levelups

# Words who DONT give XP
noexpwords = [".level", ".clear", ".help", ".ask", ".ping", ".rolldice", ".slap", ".poll", ".botsleep", ".botgaming", ".botbuilding", ".rps", ".spin", ".countdown", ".lovetest", ".msgstatus", ".jackpot"]

# Textchannels where no XP is given
noexpchannels = ["🏆server-level-ups", "❔commands-help", "🎧music-bots", "welcome", "botchat", "✅rules", "🎰slot-machine"]

# VoiceChannels where no XP is given
noexpvoicechannels = ["💤 AFK"]

# Bad words that's not OK writing
badwords = ["bad word", "bad bad word", "etc"]

# Roles at different levels
levelRoles = ["Copper Member", "Bronze Member", "Silver Member", "Gold Member", "Platinum Member", "Diamond Member", "Champion Member"]

# The levels for the different roles
levels = [5, 10, 15, 20, 25, 30, 50]

class levelsystem(commands.Cog):
    def __init__(self, client):
        self.client = client

        with open(r"userexp.json", "r") as f:
            self.users = json.load(f)

        with open(r"jackpotmachine.json", "r") as f:
            self.jackpotusers = json.load(f)

        with open(r"tickets.json", "r") as f:
            self.tickets = json.load(f)

        self.client.loop.create_task(self.save_users())
        self.client.loop.create_task(self.save_jackpotslots())
        self.client.loop.create_task(self.save_tickets())
        self.client.loop.create_task(self.check_time())
        self.client.loop.create_task(self.checkvoicechannels())
        self.client.loop.create_task(self.lottery_time())

        self.threewinner = "0"
        self.fourwinner = "0"
        self.fivewinner = "0"

    @commands.Cog.listener()
    async def on_ready(self):
        print("Levelsystem is online.")

    async def checkvoicechannels(self):
        await self.client.wait_until_ready()
        while not self.client.is_closed():
            for server in self.client.guilds:
                for channel in server.voice_channels:
                    for member in channel.members:
                        voice = member.voice
                        if not channel.name in noexpvoicechannels:
                            if voice.self_mute == False & voice.self_deaf == False:

                                author_id = str(member.id)

                                if not author_id in self.users:
                                    self.users[author_id] = {}
                                    self.users[author_id]["level"] = 1
                                    self.users[author_id]["exp"] = 0

                                self.users[author_id]["exp"] += 2

                                with open(r"slotmachine.json", "r") as f:
                                    self.slot = json.load(f)

                                if author_id in self.slot:
                                    if self.slot[author_id]["jackpot"] == 1:
                                        self.users[author_id]["exp"] += 1

                                    if self.slot[author_id]["jackpot"] == 2:
                                        self.users[author_id]["exp"] += 2

                                xp = self.users[author_id]["exp"]
                                lvl = self.users[author_id]["level"]

                                if xp >= ((50*(lvl**2))+(50*lvl)):
                                    self.users[author_id]['level'] += 1
                                    for guild in self.client.guilds:
                                        if guild.name == userserver:
                                            for channel in guild.text_channels:
                                                if channel.name == levelchannel:
                                                    await channel.send(f"Well done {member.mention}! You leveled up to **level {self.users[author_id]['level']}**!")

                                    for i in range(len(levels)):
                                        if self.users[author_id]['level'] == levels[i]:
                                            role = get(member.guild.roles, name = levelRoles[i])
                                            await member.add_roles(role)
                                            embed = discord.Embed(title=f"Congratz! You got a new role.")
                                            embed.add_field(name = "Member", value = f"{member.mention}", inline= True)
                                            embed.add_field(name = "New role", value = f"{levelRoles[i]}", inline= True)
                                            embed.set_thumbnail(url=member.avatar_url)
                                            for guild in self.client.guilds:
                                                if guild.name == userserver:
                                                    for channel in guild.text_channels:
                                                        if channel.name == levelchannel:
                                                            await channel.send(embed=embed)

            await asyncio.sleep(300)

    async def save_users(self):
        await self.client.wait_until_ready()
        while not self.client.is_closed():
            with open(r"userexp.json", "w") as f:
                json.dump(self.users, f, indent=4)

            await asyncio.sleep(5)

    async def save_jackpotslots(self):
        await self.client.wait_until_ready()
        while not self.client.is_closed():
            with open(r"jackpotmachine.json", "w") as f:
                json.dump(self.jackpotusers, f, indent=4)

            await asyncio.sleep(3)

    async def save_tickets(self):
        await self.client.wait_until_ready()
        while not self.client.is_closed():
            with open(r"tickets.json", "w") as f:
                json.dump(self.tickets, f, indent=4)

            await asyncio.sleep(3)

    async def check_time(self):
        await self.client.wait_until_ready()
        while not self.client.is_closed():

            f = '%H:%M:%S'
            now = datetime.strftime(datetime.now(), f)

            if "00:06:00" == now:
                for member in self.jackpotusers:
                    self.jackpotusers[member]["turns"] = 0

                for guild in self.client.guilds:
                    if guild.name == userserver:
                        for channel in guild.text_channels:
                            if channel.name == slotchannel:
                                await channel.send(f'Jackpot spins are being restored right now...')
                                await asyncio.sleep(5)
                                await channel.send(f'Jackpot spins restored, happy spinning! 🎰 *(.jackpot to play)*')

            await asyncio.sleep(1)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def resetjackpotspins(self, ctx, *, member: discord.Member = None):
        for user in self.jackpotusers:
            self.jackpotusers[user]["turns"] = 0
            self.jackpotusers[user]["jackpot"] = 0

        for server in self.client.guilds:
            if server.name == userserver:
                for channel in server.text_channels:
                    if channel.name == slotchannel:
                        await channel.send(f'Jackpot spins are being restored manually right now...')
                        await asyncio.sleep(5)
                        await channel.send(f'Jackpot spins restored, happy spinning! 🎰 *(.jackpot to play)*')

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def resetjackpotspin(self, ctx, member: discord.Member = None):
         member = ctx.author if not member else member
         author_id = str(member.id)

         if author_id in self.jackpotusers:
             self.jackpotusers[author_id]["turns"] -= 1

             await asyncio.sleep(5)
             for server in self.client.guilds:
                 if server.name == userserver:
                     for channel in server.text_channels:
                         if channel.name == slotchannel:
                             await channel.send(f"You got one spin back, {member.mention}!")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.channel.name not in noexpchannels:

            if message.author.bot:
                return

            for word in noexpwords:
                if word in message.content:
                    return

            words = str(message.content)
            for word in badwords:
                if word in words:
                    return

            author_id = str(message.author.id)

            if not author_id in self.users:
                self.users[author_id] = {}
                self.users[author_id]["level"] = 1
                self.users[author_id]["exp"] = 0

            self.users[author_id]["exp"] += 2 #random.randint(2, 4) # 5 innan

            with open(r"slotmachine.json", "r") as f:
                self.slot = json.load(f)

            if author_id in self.slot:
                if self.slot[author_id]["jackpot"] == 1:
                    self.users[author_id]["exp"] += 1

                if self.slot[author_id]["jackpot"] == 2:
                    self.users[author_id]["exp"] += 2

            xp = self.users[author_id]["exp"]
            lvl = self.users[author_id]["level"]

            if xp >= ((50*(lvl**2))+(50*lvl)):
                self.users[author_id]['level'] += 1
                for guild in self.client.guilds:
                    if guild.name == userserver:
                        for channel in guild.text_channels:
                            if channel.name == levelchannel:
                                await channel.send(f"Well done {message.author.mention}! You leveled up to **level {self.users[author_id]['level']}**!")

                for i in range(len(levels)):
                    if self.users[author_id]['level'] == levels[i]:
                        role = get(message.author.guild.roles, name = levelRoles[i])
                        await message.author.add_roles(role)
                        embed = discord.Embed(title=f"Congratz! You got a new role.")
                        embed.add_field(name = "Member", value = f"{message.author.mention}", inline= True)
                        embed.add_field(name = "New role", value = f"{levelRoles[i]}", inline= True)
                        embed.set_thumbnail(url=message.author.avatar_url)
                        for guild in self.client.guilds:
                            if guild.name == userserver:
                                for channel in guild.text_channels:
                                    if channel.name == levelchannel:
                                        await channel.send(embed=embed)

    @commands.command()
    async def level(self, ctx, member: discord.Member = None):
        if ctx.channel.name == levelchannel:
            member = ctx.author if not member else member
            author_id = str(member.id)

            if author_id in self.users:

                xp = self.users[author_id]["exp"]
                lvl = self.users[author_id]["level"]

                xp_tomake_this_prev_lvl = ((50*((lvl-1)**2))+(50*(lvl-1)))
                xp_tomake_this_lvl = ((50*(lvl**2))+(50*lvl))
                xp_to_make = xp_tomake_this_lvl - xp_tomake_this_prev_lvl
                xp_done_this_lvl = xp - xp_tomake_this_prev_lvl

                boxes = int((xp_done_this_lvl/xp_to_make)*20)

                embed = discord.Embed(color = 0x38a9f0, title="{}'s level status".format(member.name))
                embed.add_field(name = "Name", value = member.mention, inline= True)
                embed.add_field(name = "Total XP", value = f"{xp}", inline= True)
                embed.add_field(name = "Level", value = f"{lvl}", inline= True)
                embed.add_field(name = f"Level Prograss Bar ( {xp_done_this_lvl}/{xp_to_make} XP )", value = boxes * ":blue_square:" + (20-boxes) * ":white_large_square:", inline= True)
                embed.set_thumbnail(url=member.avatar_url)
                await ctx.channel.send(embed = embed)
            else:
                await ctx.channel.send(f"{member} doesn't have a level.")
        else:
            await ctx.channel.purge(limit = 1)
            await ctx.channel.send(f"Oh! {ctx.message.author.mention}, please type this in the chat: 🏆server-level-ups. Thank you!")


    @commands.command()
    @commands.has_permissions(administrator=True)
    async def givexp(self, ctx, member : discord.Member = None, *, amount : int):
        member = ctx.author if not member else member
        author_id = str(member.id)

        if author_id in self.users:
            self.users[author_id]["exp"] += amount

        await ctx.channel.send(f"{member.name} has got {amount} XP.")


    # JACKPOT MACHINE SYSTEM
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def threewin(self, ctx):
        self.threewinner = "1"
        self.fourwinner = "0"
        self.fivewinner = "0"
        await ctx.channel.send("Next spinner will be at least a 3 row winner.")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def fourwin(self, ctx):
        self.threewinner = "0"
        self.fourwinner = "1"
        self.fivewinner = "0"
        await ctx.channel.send("Next spinner will be at least a 4 row winner.")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def fivewin(self, ctx):
        self.threewinner = "0"
        self.fourwinner = "0"
        self.fivewinner = "1"
        await ctx.channel.send("Next spinner will be a 5 row winner.")

    @commands.command()
    async def jackpot(self, ctx):
        if ctx.channel.name == slotchannel:
            author_id = str(ctx.message.author.id)
            member = ctx.author

            if not author_id in self.users:
                self.users[author_id] = {}
                self.users[author_id]["level"] = 1
                self.users[author_id]["exp"] = 0

            if not author_id in self.jackpotusers:
                self.jackpotusers[author_id] = {}
                self.jackpotusers[author_id]["turns"] = 0

            await ctx.channel.send(f"Wait a few sec.. spinning jackpot wheel")
            await asyncio.sleep(3)

            turns = int(self.jackpotusers[author_id]["turns"])
            turnsleft = 10 - turns - 1

            if not turns == 10:
                self.jackpotusers[author_id]["turns"] += 1

                signs = [":seven:", ":cherries:", ":lemon:", ":strawberry:", ":four_leaf_clover:"]

                if self.threewinner == "1":
                    threesign = random.choice(signs)
                    signone = threesign
                    signtwo = threesign
                    signthree = threesign
                    signfour = random.choice(signs)
                    signfive = random.choice(signs)
                    self.threewinner = "0"

                elif self.fourwinner == "1":
                    foursign = random.choice(signs)
                    signone = foursign
                    signtwo = foursign
                    signthree = foursign
                    signfour = foursign
                    signfive = random.choice(signs)
                    self.fourwinner = "0"

                elif self.fivewinner == "1":
                    fivewin = random.choice(signs)
                    signone = fivewin
                    signtwo = fivewin
                    signthree = fivewin
                    signfour = fivewin
                    signfive = fivewin
                    self.fivewinner = "0"

                else:
                    signone = random.choice(signs)
                    signtwo = random.choice(signs)
                    signthree = random.choice(signs)
                    signfour = random.choice(signs)
                    signfive = random.choice(signs)

                description = ""
                description += "Row: "
                description += signone + "  |  "
                description += signtwo + "  |  "
                description += signthree + "  |  "
                description += signfour + "  |  "
                description += signfive + " "

                embed = discord.Embed(color = 0x38a9f0, title=f"Fruit jackpot machine [Exp] :slot_machine:", description = description)
                embed.add_field(name = "Player", value = f"{ctx.message.author.mention}", inline= True)
                embed.add_field(name = "Spins left", value = turnsleft, inline= True)


                if signone == signtwo == signthree:
                    if signthree == signfour:
                        if signfour == signfive:
                            if signfive == ":seven:":
                                if author_id in self.users:
                                    self.users[author_id]["exp"] += 1000
                                    embed.add_field(name = "CONGRATZ", value = f"You won 1000 EXP!", inline= True)


                            elif signfive == ":cherries:":
                                if author_id in self.users:
                                    self.users[author_id]["exp"] += 200
                                    embed.add_field(name = "CONGRATZ", value = f"You won 200 EXP!", inline= True)


                            elif signfive == ":lemon:":
                                if author_id in self.users:
                                    self.users[author_id]["exp"] += 50
                                    embed.add_field(name = "CONGRATZ", value = f"You won 50 EXP!", inline= True)


                            elif signfive == ":strawberry:":
                                if author_id in self.users:
                                    self.users[author_id]["exp"] += 100
                                    embed.add_field(name = "CONGRATZ", value = f"You won 100 EXP!", inline= True)


                            elif signfive == ":four_leaf_clover:":
                                 if author_id in self.jackpotusers:
                                     self.jackpotusers[author_id]["turns"] -= 3
                                     embed.add_field(name = "CONGRATZ", value = f"You won 3 extra spins.", inline= True)

                        else:
                            if signfour == ":seven:":
                                if author_id in self.users:
                                    self.users[author_id]["exp"] += 500
                                    embed.add_field(name = "CONGRATZ", value = f"You won 500 EXP!", inline= True)


                            elif signfour == ":cherries:":
                                if author_id in self.users:
                                    self.users[author_id]["exp"] += 100
                                    embed.add_field(name = "CONGRATZ", value = f"You won 100 EXP!", inline= True)


                            elif signfour == ":lemon:":
                                if author_id in self.users:
                                    self.users[author_id]["exp"] += 20
                                    embed.add_field(name = "CONGRATZ", value = f"You won 20 EXP!", inline= True)


                            elif signfour == ":strawberry:":
                                if author_id in self.users:
                                    self.users[author_id]["exp"] += 50
                                    embed.add_field(name = "CONGRATZ", value = f"You won 50 EXP!", inline= True)


                            elif signfour == ":four_leaf_clover:":
                                if author_id in self.jackpotusers:
                                    self.jackpotusers[author_id]["turns"] -= 2
                                    embed.add_field(name = "CONGRATZ", value = f"You won 2 extra spins.", inline= True)

                    else:
                        if signthree == ":seven:":
                            if author_id in self.users:
                                self.users[author_id]["exp"] += 250
                                embed.add_field(name = "CONGRATZ", value = f"You won 250 EXP!", inline= True)


                        elif signthree == ":cherries:":
                            if author_id in self.users:
                                self.users[author_id]["exp"] += 50
                                embed.add_field(name = "CONGRATZ", value = f"You won 50 EXP!", inline= True)


                        elif signthree == ":lemon:":
                            if author_id in self.users:
                                self.users[author_id]["exp"] += 10
                                embed.add_field(name = "CONGRATZ", value = f"You won 10 EXP!", inline= True)


                        elif signthree == ":strawberry:":
                            if author_id in self.users:
                                self.users[author_id]["exp"] += 25
                                embed.add_field(name = "CONGRATZ", value = f"You won 25 EXP!", inline= True)


                        elif signthree == ":four_leaf_clover:":
                            if author_id in self.jackpotusers:
                                self.jackpotusers[author_id]["turns"] -= 1
                                embed.add_field(name = "CONGRATZ", value = f"You won 1 extra spins.", inline= True)


                    while True:
                        xp = self.users[author_id]["exp"]
                        lvl = self.users[author_id]["level"]

                        if xp >= ((50*(lvl**2))+(50*lvl)):
                            self.users[author_id]['level'] += 1
                            for guild in self.client.guilds:
                                if guild.name == userserver:
                                    for channel in guild.text_channels:
                                        if channel.name == levelchannel:
                                            await channel.send(f"Well done {ctx.message.author.mention}! You leveled up to **level {self.users[author_id]['level']}**!")

                            for i in range(len(levels)):
                                if self.users[author_id]['level'] == levels[i]:
                                    role = get(ctx.author.guild.roles, name = levelRoles[i])
                                    await ctx.author.add_roles(role)
                                    embed = discord.Embed(title=f"Congratz! You got a new role.")
                                    embed.add_field(name = "Member", value = f"{ctx.message.author.mention}", inline= True)
                                    embed.add_field(name = "New role", value = f"{levelRoles[i]}", inline= True)
                                    embed.set_thumbnail(url=ctx.message.author.avatar_url)
                                    for guild in self.client.guilds:
                                        if guild.name == userserver:
                                            for channel in guild.text_channels:
                                                if channel.name == levelchannel:
                                                    await channel.send(embed=embed)
                        else:
                            break

                else:
                    embed.add_field(name = "Try again", value = "Better luck next time.", inline= True)

                embed.set_thumbnail(url=ctx.message.author.avatar_url)
                await ctx.channel.send(embed=embed)
            else:
                await ctx.channel.send(f"Oh.. you don't have any spins left today, {ctx.message.author.mention}. Please try again tomorrow!")
        else:
            await ctx.channel.purge(limit = 1)
            await ctx.channel.send(f"Oh! {ctx.message.author.mention}, please type this in the chat: 🎰slot-machine. Thank you!")


    # TICKET MACHINESYSTEM
    @commands.command()
    async def ticket(self, ctx):
        if ctx.channel.name == lotterychannel:
            author_id = str(ctx.message.author.id)
            member = ctx.author

            if not author_id in self.tickets:
                self.tickets[author_id] = {}
                self.tickets[author_id]["ticket"] = 0
                self.tickets[author_id]["number"] = 0
                self.tickets[author_id]["corrects"] = 0
                self.tickets[author_id]["wins"] = 0

            if self.tickets[author_id]["ticket"] != 1:
                self.tickets[author_id]["ticket"] = 1
                signs = [":one:", ":two:", ":three:", ":four:", ":five:", ":six:", ":seven:", ":eight:", ":nine:"]

                signone = random.choice(signs)
                signtwo = random.choice(signs)
                signthree = random.choice(signs)
                signfour = random.choice(signs)
                signfive = random.choice(signs)
                number = (f"{signone} {signtwo} {signthree} {signfour} {signfive}")

                numberarray = [signone, signtwo, signthree, signfour, signfive]
                self.tickets[author_id]["number"] = numberarray

                await ctx.channel.send(f"Your ticket number is: {number} \n The lottery takes place at 21:00! Good luck, {member.mention}!")
            else:
                await ctx.channel.send(f"Your already got a ticket for todays lottery {member.mention}!")
        else:
            await ctx.channel.purge(limit = 1)
            await ctx.channel.send(f"Oh! {ctx.message.author.mention}, please type this in the chat: 🎲lottery. Thank you!")


    @commands.command()
    async def ticketnr(self, ctx):
        if ctx.channel.name == lotterychannel:
            author_id = str(ctx.message.author.id)
            member = ctx.author

            if not author_id in self.tickets:
                self.tickets[author_id] = {}
                self.tickets[author_id]["ticket"] = 0
                self.tickets[author_id]["number"] = 0
                self.tickets[author_id]["corrects"] = 0
                self.tickets[author_id]["wins"] = 0

            if self.tickets[author_id]["ticket"] == 1:
                temp = self.tickets[author_id]["number"]
                signone = temp[0]
                signtwo = temp[1]
                signthree = temp[2]
                signfour = temp[3]
                signfive = temp[4]
                number = (f"{signone} {signtwo} {signthree} {signfour} {signfive}")
                await ctx.channel.send(f"Your ticket number is: {number}")
            else:
                await ctx.channel.send(f"You have not claimed a ticket for today yet {member.mention}!")
        else:
            await ctx.channel.purge(limit = 1)
            await ctx.channel.send(f"Oh! {ctx.message.author.mention}, please type this in the chat: 🎲lottery. Thank you!")


    @commands.command()
    @commands.has_permissions(administrator=True)
    async def lottery(self, ctx):
        for guild in self.client.guilds:
            if guild.name == userserver:
                for channel in guild.text_channels:
                    if channel.name == lotterychannel:
                        signs = [":one:", ":two:", ":three:", ":four:", ":five:", ":six:", ":seven:", ":eight:", ":nine:"]

                        signone = random.choice(signs)
                        signtwo = random.choice(signs)
                        signthree = random.choice(signs)
                        signfour = random.choice(signs)
                        signfive = random.choice(signs)

                        number = (f"{signone} {signtwo} {signthree} {signfour} {signfive}")
                        numberarray = [signone, signtwo, signthree, signfour, signfive]
                        await channel.send(f"This evenings first numbers are: {number}")

                        for id in self.tickets:
                            mynumbers = self.tickets[id]["number"]

                            if mynumbers !=  0:
                                if mynumbers[0] == numberarray[0]:
                                    self.tickets[id]["corrects"] += 1

                                if mynumbers[1] == numberarray[1]:
                                    self.tickets[id]["corrects"] += 1

                                if mynumbers[2] == numberarray[2]:
                                    self.tickets[id]["corrects"] += 1

                                if mynumbers[3] == numberarray[3]:
                                    self.tickets[id]["corrects"] += 1

                                if mynumbers[4] == numberarray[4]:
                                    self.tickets[id]["corrects"] += 1

                        await asyncio.sleep(5)

                        signone = random.choice(signs)
                        signtwo = random.choice(signs)
                        signthree = random.choice(signs)
                        signfour = random.choice(signs)
                        signfive = random.choice(signs)

                        number = (f"{signone} {signtwo} {signthree} {signfour} {signfive}")
                        numberarray = [signone, signtwo, signthree, signfour, signfive]

                        await channel.send(f"Second numbers are: {number}")

                        for id in self.tickets:
                            mynumbers = self.tickets[id]["number"]

                            if mynumbers != 0:
                                if mynumbers[0] == numberarray[0]:
                                    self.tickets[id]["corrects"] += 1

                                if mynumbers[1] == numberarray[1]:
                                    self.tickets[id]["corrects"] += 1

                                if mynumbers[2] == numberarray[2]:
                                    self.tickets[id]["corrects"] += 1

                                if mynumbers[3] == numberarray[3]:
                                    self.tickets[id]["corrects"] += 1

                                if mynumbers[4] == numberarray[4]:
                                    self.tickets[id]["corrects"] += 1

                        await asyncio.sleep(5)

                        signone = random.choice(signs)
                        signtwo = random.choice(signs)
                        signthree = random.choice(signs)
                        signfour = random.choice(signs)
                        signfive = random.choice(signs)

                        number = (f"{signone} {signtwo} {signthree} {signfour} {signfive}")
                        numberarray = [signone, signtwo, signthree, signfour, signfive]

                        await channel.send(f"And the last numbers for today are: {number}")

                        for id in self.tickets:
                            mynumbers = self.tickets[id]["number"]

                            if mynumbers != 0:
                                if mynumbers[0] == numberarray[0]:
                                    self.tickets[id]["corrects"] += 1

                                if mynumbers[1] == numberarray[1]:
                                    self.tickets[id]["corrects"] += 1

                                if mynumbers[2] == numberarray[2]:
                                    self.tickets[id]["corrects"] += 1

                                if mynumbers[3] == numberarray[3]:
                                    self.tickets[id]["corrects"] += 1

                                if mynumbers[4] == numberarray[4]:
                                    self.tickets[id]["corrects"] += 1

                                self.tickets[id]["wins"] = self.tickets[id]["corrects"] * 50

                        embed = discord.Embed(title=f"Todays winners")

                        for id in self.tickets:
                            author = self.tickets[id]
                            if self.tickets[id]["corrects"] != 0:
                                user = await self.client.fetch_user(id)
                                val = str(self.tickets[id]["wins"])
                                val += " EXP"
                                embed.add_field(name = f"{user.name}", value = val, inline= True)

                                if not id in self.users:
                                     self.users[id] = {}
                                     self.users[id]["level"] = 1
                                     self.users[id]["exp"] = 0

                                self.users[id]["exp"] += self.tickets[id]["wins"]

                        await channel.send(embed=embed)

                        for id in self.tickets:
                            self.tickets[id]["ticket"] = 0
                            self.tickets[id]["number"] = 0
                            self.tickets[id]["corrects"] = 0
                            self.tickets[id]["wins"] = 0



    async def lottery_time(self):
        await self.client.wait_until_ready()
        while not self.client.is_closed():

            f = '%H:%M:%S'
            now = datetime.strftime(datetime.now(), f)

            if "21:00:00" == now:
                for guild in self.client.guilds:
                    if guild.name == userserver:
                        for channel in guild.text_channels:
                            if channel.name == lotterychannel:
                                signs = [":one:", ":two:", ":three:", ":four:", ":five:", ":six:", ":seven:", ":eight:", ":nine:"]

                                signone = random.choice(signs)
                                signtwo = random.choice(signs)
                                signthree = random.choice(signs)
                                signfour = random.choice(signs)
                                signfive = random.choice(signs)

                                number = (f"{signone} {signtwo} {signthree} {signfour} {signfive}")
                                numberarray = [signone, signtwo, signthree, signfour, signfive]
                                await channel.send(f"This evenings first numbers are: {number}")

                                for id in self.tickets:
                                    mynumbers = self.tickets[id]["number"]

                                    if mynumbers != 0:
                                        if mynumbers[0] == numberarray[0]:
                                            self.tickets[id]["corrects"] += 1

                                        if mynumbers[1] == numberarray[1]:
                                            self.tickets[id]["corrects"] += 1

                                        if mynumbers[2] == numberarray[2]:
                                            self.tickets[id]["corrects"] += 1

                                        if mynumbers[3] == numberarray[3]:
                                            self.tickets[id]["corrects"] += 1

                                        if mynumbers[4] == numberarray[4]:
                                            self.tickets[id]["corrects"] += 1

                                await asyncio.sleep(5)

                                signone = random.choice(signs)
                                signtwo = random.choice(signs)
                                signthree = random.choice(signs)
                                signfour = random.choice(signs)
                                signfive = random.choice(signs)

                                number = (f"{signone} {signtwo} {signthree} {signfour} {signfive}")
                                numberarray = [signone, signtwo, signthree, signfour, signfive]

                                await channel.send(f"Second numbers are: {number}")

                                for id in self.tickets:
                                    mynumbers = self.tickets[id]["number"]

                                    if mynumbers != 0:

                                        if mynumbers[0] == numberarray[0]:
                                            self.tickets[id]["corrects"] += 1

                                        if mynumbers[1] == numberarray[1]:
                                            self.tickets[id]["corrects"] += 1

                                        if mynumbers[2] == numberarray[2]:
                                            self.tickets[id]["corrects"] += 1

                                        if mynumbers[3] == numberarray[3]:
                                            self.tickets[id]["corrects"] += 1

                                        if mynumbers[4] == numberarray[4]:
                                            self.tickets[id]["corrects"] += 1

                                await asyncio.sleep(5)

                                signone = random.choice(signs)
                                signtwo = random.choice(signs)
                                signthree = random.choice(signs)
                                signfour = random.choice(signs)
                                signfive = random.choice(signs)

                                number = (f"{signone} {signtwo} {signthree} {signfour} {signfive}")
                                numberarray = [signone, signtwo, signthree, signfour, signfive]

                                await channel.send(f"And the last numbers for today are: {number}")

                                for id in self.tickets:
                                    mynumbers = self.tickets[id]["number"]

                                    if mynumbers != 0:
                                        if mynumbers[0] == numberarray[0]:
                                            self.tickets[id]["corrects"] += 1

                                        if mynumbers[1] == numberarray[1]:
                                            self.tickets[id]["corrects"] += 1

                                        if mynumbers[2] == numberarray[2]:
                                            self.tickets[id]["corrects"] += 1

                                        if mynumbers[3] == numberarray[3]:
                                            self.tickets[id]["corrects"] += 1

                                        if mynumbers[4] == numberarray[4]:
                                            self.tickets[id]["corrects"] += 1

                                        self.tickets[id]["wins"] = self.tickets[id]["corrects"] * 50

                                embed = discord.Embed(title=f"Todays winners")

                                for id in self.tickets:
                                    author = self.tickets[id]
                                    if self.tickets[id]["corrects"] != 0:
                                        user = await self.client.fetch_user(id)
                                        val = str(self.tickets[id]["wins"])
                                        val += " EXP"
                                        embed.add_field(name = f"{user.name}", value = val, inline= True)

                                        if not id in self.users:
                                             self.users[id] = {}
                                             self.users[id]["level"] = 1
                                             self.users[id]["exp"] = 0

                                        self.users[id]["exp"] += self.tickets[id]["wins"]

                                await channel.send(embed=embed)

                                for id in self.tickets:
                                    self.tickets[id]["ticket"] = 0
                                    self.tickets[id]["number"] = 0
                                    self.tickets[id]["corrects"] = 0
                                    self.tickets[id]["wins"] = 0

            await asyncio.sleep(1)


def setup(client):
    client.add_cog(levelsystem(client))
