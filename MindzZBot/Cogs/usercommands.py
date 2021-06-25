import random
import discord
from discord.ext import commands

import asyncio

# Textchannels where you can't write these commands
nowritingchannels = ["🏆server-level-ups", "❔commands-help", "🎧music-bots", "welcome", "botchat", "✅rules", "🎰slot-machine"]

rockpaperscissor = ["rock", "paper", "scissors"]

class usercmds(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command()
    async def rps(self,ctx):
        if not ctx.channel.name in nowritingchannels:
            await ctx.channel.purge(limit = 1)
            await ctx.send(f"{ctx.author.mention}, chooses **{random.choice(rockpaperscissor)}**")
        else:
            await ctx.channel.purge(limit = 1)


    @commands.command()
    async def slap(self, ctx, *, member : discord.Member):
        if not ctx.channel.name in nowritingchannels:
            await ctx.channel.purge(limit = 1)
            await ctx.send(f'{ctx.author.mention} just slapped {member.mention}!')
        else:
            await ctx.channel.purge(limit = 1)

    @commands.command()
    async def rolldice(self, ctx):
        if not ctx.channel.name in nowritingchannels:
            await ctx.channel.purge(limit = 1)
            numbers = ['1','2','3','4','5','6']
            await ctx.send(f"{ctx.author.mention}, you rolled a **{random.choice(numbers)}**")
        else:
            await ctx.channel.purge(limit = 1)

    @commands.command()
    async def ask(self, ctx, *, question):
        if not ctx.channel.name in nowritingchannels:
            responses = [   'It is certain.',
                            'Outlook not so good.',
                            'Yes - definitely.',
                            'You may rely on it.',
                            'My reply is no.',
                            'As I see it, yes.',
                            'Most likely.',
                            'Outlook good.',
                            'Signs point to yes.',
                            'Reply hazy, try again.',
                            'Yes.',
                            'It is decidedly so.',
                            'Ask again later.',
                            'Better not tell you now.',
                            'Cannot predict now.',
                            'Concentrate and ask again.',
                            "Don't count on it.",
                            'My sources say no.',
                            'Without a doubt.',
                            'Very doubtful.'    ]
            await ctx.channel.purge(limit = 1)
            await ctx.send(f'Question: {question}\nAnswer: {random.choice(responses)}')
        else:
            await ctx.channel.purge(limit = 1)

    @commands.command(pass_context=True)
    async def poll(self, ctx, question, *options: str):
        if not str(ctx.channel.name) in nowritingchannels:
            await ctx.channel.purge(limit = 1)

            if len(options) <= 1:
                await ctx.send('You need more than one option to make a poll!')
                return
            if len(options) > 10:
                await ctx.send('You cannot make a poll for more than 10 things!')
                return

            if len(options) == 2 and options[0] == 'yes' and options[1] == 'no':
                reactions = ['✅', '❌']
            else:
                reactions = ['1⃣', '2⃣', '3⃣', '4⃣', '5⃣', '6⃣', '7⃣', '8⃣', '9⃣', '🔟']

            embed = discord.Embed(title="{}'s poll request".format(ctx.author.name))
            embed.add_field(name = "Question: ", value = f"{question}", inline= False)

            for x, option in enumerate(options):
                embed.add_field(name = f"{option}", value = f"{reactions[x]}", inline= True)

            embed.set_thumbnail(url=ctx.author.avatar_url)
            react_message = await ctx.send(embed=embed)

            for reaction in reactions[:len(options)]:
                await react_message.add_reaction(reaction)
        else:
            await ctx.channel.purge(limit = 1)

    @commands.command()
    async def countdown(self, ctx):
        '''It's the final countdown'''
        countdown = ['five', 'four', 'three', 'two', 'one']
        for num in countdown:
            message = await ctx.send('**:{0}:**'.format(num))
            await asyncio.sleep(1)
        await ctx.send('**:ok:**')


def setup(client):
    client.add_cog(usercmds(client))
