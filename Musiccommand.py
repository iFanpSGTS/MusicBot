import discord
from discord.ext.commands import bot
from discord.ext import commands
from asyncio import sleep
import urllib.parse
import urllib.request
import re
import youtube_dl
import aiohttp

Queue = {}
LYRICS_URL = "https://some-random-api.ml/lyrics?title="

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(pass_context=True)
    async def pause(self, ctx):
        if (ctx.author.voice):
            voice = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
            if voice.is_playing():
                voice.pause()
                await ctx.send("**Selection paused.**")
                await sleep(500)  
                if ctx.voice_client and ctx.guild.voice_client.is_paused():
                    await ctx.send("Paused is too long!")
                    ctx.guild.voice_client.disconnect()
            else:
                await ctx.send("There is no music to pause!")
        else:
            await ctx.send("You are not in a voice channel, you must be in a voice channel to run this command.")

    @commands.command(pass_context=True)
    async def resume(self, ctx):
        if (ctx.author.voice):
            voice = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
            if voice.is_paused():
                voice.resume()
                await ctx.send("**Selection resumed.**")
            else:
                await ctx.send("There is no song to resume!")
        else:
            await ctx.send("You are not in a voice channel, you must be in a voice channel to run this command.")

    @commands.command()
    async def queue(self, ctx, page_num=1):
        embed = discord.Embed(color=0xa09c9c)
        if ctx.guild.id not in Queue:
            await ctx.send("No queue!")
        real_num = page_num - 1
        queue_pages = []
        page = []
        k = 1
        for i in range(len(Queue[ctx.guild.id])):
            page.append(Queue[ctx.guild.id][i])
            if k % 10 == 0:
                temp = page.copy()
                queue_pages.append(temp)
                page.clear()
            elif (k == len(Queue[ctx.guild.id])) and (k % 10 != 0):
                queue_pages.append(page)
            k = k + 1

        if (page_num > len(queue_pages)) or (page_num <= 0):
            return await ctx.send("Invalid page number. There are currently " + str(len(queue_pages)) + " page(s) in the queue.")

        embed.title = "**Current queue**"
        key = page_num - 1
        for j in range(len(queue_pages[real_num])):
            if page_num == 1:
                if j == 0:
                    embed.add_field(name="[0] is Playing:", value=queue_pages[real_num][j].get('title', None), inline=False)
                else:
                    embed.add_field(name=str(j) + ". ", value=queue_pages[real_num][j].get('title', None), inline=False)
            else:
                embed.add_field(name=str(key) + str(j) + ". ", value=queue_pages[real_num][j].get('title', None), inline=False)

        embed.set_footer(text="Page " + str(page_num) +"/" + str(len(queue_pages)))
        await ctx.send(embed=embed)
    
    @commands.command()
    async def skip(self, ctx, index=0):
        if ctx.author.voice:
            voice = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
            if index > 0:
                if index > len(Queue[ctx.guild.id]):
                    await ctx.send("Out of range, can't skip song!")
                else:
                    for i in range(index - 1):
                        del(Queue[ctx.guild.id][0])
            voice.stop()
            await ctx.send("Skipped!")
        else:
            await ctx.send("You are not in a voice channel, you must be in a voice channel to run this command.")
    
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def automatic_play(self, ctx):
        if ctx.guild.id not in Queue:
            await ctx.send("No song in queue")
        if not (ctx.voice_client):
            channel = ctx.message.author.voice.channel
            voice = await channel.connect()
        else:
            voice = ctx.guild.voice_client
            
        FFMPEG_OPTIONS = {
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
        YDL_OPTIONS = {'format': "bestaudio"}

        with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
            if Queue[ctx.guild.id][0]['from_playlist'] == True:
                url2 = ydl.extract_info(Queue[ctx.guild.id][0]['url'], download=False)
                url2 = url2['formats'][0]['url']
            else:
                url2 = Queue[ctx.guild.id][0].get('url', None)
            source = await discord.FFmpegOpusAudio.from_probe(url2, **FFMPEG_OPTIONS)
            voice.play(source)
        
        while (voice.is_playing() or voice.is_paused()):
            await sleep(1)
        del(Queue[ctx.guild.id][0])
        if len(Queue[ctx.guild.id]) != 0:
            await self.bot.get_command(name='automatic_play').callback(self, ctx)
        else:
            Queue.pop(ctx.guild.id,None)
            await voice.disconnect()
    
    @commands.command()
    async def play(self, ctx, *, search):
        query_string = urllib.parse.urlencode({
            'search_query': search
        })
        htm_content = urllib.request.urlopen(
            'http://www.youtube.com/results?' + query_string
        )
        search_results = re.findall(
            r"watch\?v=(\S{11})", htm_content.read().decode())
        
        url = 'http://www.youtube.com/watch?v=' + search_results[0]
        
        if (ctx.author.voice):
            if ctx.guild.id not in Queue:
                Queue[ctx.guild.id] = []
            if not (ctx.voice_client):
                channel = ctx.message.author.voice.channel
                voice = await channel.connect()
            else:
                voice = ctx.guild.voice_client
            ydl_opts = {
                'quiet': True,
                'skip_download': True,
            }
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url)

            Queue[ctx.guild.id].append(
                {'url': info['formats'][0]['url'], 'title': info['title'], 'from_playlist': False})
            
            await ctx.send(f'New selection is added!\nQueue selection is now **{len(Queue[ctx.guild.id])}**')
            
            if not (voice.is_playing() or voice.is_paused()):
                await self.bot.get_command(name='automatic_play').callback(self, ctx)
        else:
            await ctx.send("You are not in a voice channel, you must be in a voice channel to run this command.")

    @commands.command()
    async def lyric(self, ctx):
        if (ctx.author.voice):
            if ctx.voice_client:
                if song == None:
                    name = Queue[ctx.guild.id][0].get('title', None)
                    async with ctx.typing():
                        async with aiohttp.request("GET", LYRICS_URL + name, headers={}) as r:
                            if not 200 <= r.status <= 299:
                                await ctx.send(f"No lyrics found with this --> **Title** [***{name}***]")

                            data = await r.json()

                            embed = discord.Embed(
                                title = data["title"],
                                description = data["lyrics"],
                                colour=0xa09c9c,
                            )
                            
                            embed.set_thumbnail(url=data["thumbnail"]["genius"])
                            embed.set_author(name=data["author"])
                            embed.set_footer(text = "Lyric music")
                            await ctx.send(embed=embed)
                else:
                    async with ctx.typing():
                        async with aiohttp.request("GET", LYRICS_URL + song, headers={}) as r:
                            if not 200 <= r.status <= 299:
                                await ctx.send(f"No lyrics found with this --> **Title** [***{song}***]")

                            data = await r.json()

                            embed = discord.Embed(
                                title = data["title"],
                                description = data["lyrics"],
                                colour=0xa09c9c,
                            )
                            
                            embed.set_thumbnail(url=data["thumbnail"]["genius"])
                            embed.set_author(name=data["author"])
                            embed.set_footer(text = "Lyric music")
                            await ctx.send(embed=embed)
            else:
                return await ctx.send("I am not connected to a voice channel.")
        else:
            return await ctx.send("You are not in a voice channel, you must be in a voice channel to run this command.")            

def setup(bot):
    bot.add_cog(Music(bot))
