# This script is useless, why is this useless, because i make this just to check ping, and purge all testing message in my discord server
from discord.ext.commands import bot
from discord.ext import commands

class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.command()
    async def ping(self, ctx):
        await ctx.send(f'Pong! :ping_pong: - {round(self.bot.latency * 1000)}ms')

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def purge(self, ctx, amount=5):
        await ctx.channel.purge(limit=amount)

def setup(bot):
    bot.add_cog(General(bot))
