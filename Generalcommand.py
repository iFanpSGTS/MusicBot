from discord.ext.commands import bot
from discord.ext import commands

class usefulFunctions(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.command(name="ping", help=" - Display the latency of Vibe Bot.")
    async def ping(self, ctx):
        await ctx.send(f'Pong! :ping_pong: - {round(self.bot.latency * 1000)}ms')

    @commands.command(name="purge", help=" - Purges (clears) the last specified amount of messages.")
    @commands.has_permissions(manage_messages=True)
    async def purge(self, ctx, amount=5):
        await ctx.channel.purge(limit=amount)

def setup(bot):
    bot.add_cog(usefulFunctions(bot))
