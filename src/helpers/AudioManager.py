from .AudioPlayer import AudioPlayer
from youtube_dl import YoutubeDL

import itertools
import discord

ytdlopts = {
    'format': 'bestaudio/best',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'  # ipv6 addresses cause issues sometimes
}

ytdl = YoutubeDL(ytdlopts)


class AudioManager:

    def __init__(self):
        self.players = {}

    def _resolveurls(self, urllist):
        results = []
        for item in urllist:
            res = ytdl.extract_info(
                item['search'], download=False, process=True)

            if('entries' in res):
                en_list = list(res.get('entries'))
                if(len(en_list) >= 1):
                    res = res.get('entries')[0]
                else:
                    res = {'title': 'None'}

            results.append(res)
        return results

    def _getplayer(self, ctx):
        try:
            player = self.players[ctx.guild.id]
        except KeyError:
            player = AudioPlayer(ctx)
            self.players[ctx.guild.id] = player
        return player

    async def cleanupplayer(self, guild):

        try:
            await guild.voice_client.disconnect()
        except AttributeError:
            pass

        try:
            del self.players[guild]
        except KeyError:
            pass

    """ Basic Controlls """

    async def play(self, ctx, search, playnext=False):

        if search is None:
            return await ctx.send('> Audio URL not specified. Did you mean to resume?')

        # Get the channel we are playing in
        player = self._getplayer(ctx)
        results = ytdl.extract_info(search, download=False, process=False)

        if(playnext):
            play_index = 0
        else:
            play_index = -1

        if('entries' in results):

            entries = list(results['entries'])
            await ctx.send(f'```ini\n[Adding {len(entries)} songs to the Queue.]\n```')

            for e in entries:
                items = {}
                items['ctx'] = ctx
                items['search'] = 'https://www.youtube.com/watch?v={}'.format(
                    e['url'])
                await player.queue.put(items)
        else:

            # This is a single song request.  We can handle it a bit better.
            results = ytdl.extract_info(search, download=False)

            if('entries' in results):
                results = results['entries'][0]

            await ctx.send(f'```ini\n[Adding "{results["title"]}" to the Queue.]\n```')

            items = {}
            items['ctx'] = ctx
            items['search'] = results['webpage_url']
            await player.queue.put(items, index=play_index)

    async def pause(self, ctx):

        vc = ctx.voice_client

        if(not vc or not vc.is_playing()):
            return await ctx.send('> The bot is not currently playing anything.')

        if(vc.is_paused()):
            return

        vc.pause()

    async def resume(self, ctx):
        vc = ctx.voice_client

        if(not vc or not vc.is_connected()):
            return await ctx.send('> The bot is not currently playing anything')

        if(vc.is_playing()):
            return

        vc.resume()

    async def skip(self, ctx):

        vc = ctx.voice_client

        if(not vc or not vc.is_connected()):
            return await ctx.send('> The bot is not currently playing anything')

        # Do nothing when it is not playing
        if(not vc.is_playing()):
            return

        vc.stop()
        await ctx.send(f'> **`{ctx.author}`**: Skipped the song!')

    """ END Basic Controlls """

    """ Advanced Controlls """

    async def displayplaying(self, ctx):
        """Display information about the currently playing song."""
        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            return await ctx.send('I am not currently connected to voice!', delete_after=20)

        player = self._getplayer(ctx)
        if not player.current:
            return await ctx.send('I am not currently playing anything!')

        await ctx.send(f'**Now Playing:** `{vc.source.title}` '
                       f'requested by `{vc.source.requester}`')

    async def displayqueue(self, ctx):
        """Retrieve a basic queue of upcoming songs."""
        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            return await ctx.send('I am not currently connected to voice!', delete_after=20)

        player = self._getplayer(ctx)
        if player.queue.empty():
            return await ctx.send('There are currently no more queued songs.')

        np = await ctx.send('> Fetching queue.  Please Wait.')

        # Grab up to 5 entries from the queue...
        upcoming = list(itertools.islice(player.queue._queue, 0, 5))
        songs = self._resolveurls(upcoming)

        fmt = '\n'.join(f'**`{_["title"]}`**' for _ in songs)
        embed = discord.Embed(
            title=f'Upcoming - Next {len(upcoming)}', description=fmt)

        await ctx.send(embed=embed)
        await np.delete()

    async def shuffle(self, ctx):
        vc = ctx.voice_client
        if(not vc):
            return await ctx.send('> The bot is not currently in a voice channel')

        player = self._getplayer(ctx)
        if(player.queue.empty()):
            return await ctx.send('> There are no songs in queue to be shuffled')

        player.queue.shuffle_queue()
        await ctx.send('> Queue finished shuffling.')
