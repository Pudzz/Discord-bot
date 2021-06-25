import discord
import asyncio
from discord.ext import commands
from discord.utils import get

# Your roles at different levels
levelRoles = ["Copper Member", "Bronze Member", "Silver Member", "Gold Member", "Platinum Member", "Diamond Member", "Champion Member"]

class admin(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def clear(self, ctx, amount : int):
        await ctx.channel.purge(limit = amount)
        await asyncio.sleep(5)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def checkmember(self, ctx, id : int):
        user = await self.client.fetch_user(id)
        await ctx.send(f"This is: {user.name}")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def checkmemberid(self, ctx, *, member : discord.Member):
        await ctx.send(f"This is: {member.id}")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def kick(self, ctx, member : discord.Member, *, reason=None):
        await ctx.channel.purge(limit = 1)
        await member.kick(reason = reason)
        await ctx.send(f'{member} has been kicked from the server.')

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def ban(self, ctx, member : discord.Member, *, reason=None):
        await member.ban(reason = reason)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def unban(self, ctx, *, member):
        banned_users = await ctx.guild.bans()
        member_name, member_descriminator = member.split('#')

        for ban_entry in banned_users:
            user = ban_entry.user

            if(user.name, user.discriminator) == (member, member_descriminator):
                await ctx.guild.unban(user)
                await ctx.send(f'Unbanned {user.mention}')
                return

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def ping(self, ctx):
        await ctx.send(f'Ping latency: {round(self.client.latency * 1000)}ms')

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def load(self, ctx, extension):
        self.client.load_extension(f'Cogs.{extension}')

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def unload(self, ctx, extension):
        self.client.unload_extension(f'Cogs.{extension}')

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def reload(self, ctx, extension):
        self.client.unload_extension(f'Cogs.{extension}')
        self.client.load_extension(f'Cogs.{extension}')

def setup(client):
    client.add_cog(admin(client))
