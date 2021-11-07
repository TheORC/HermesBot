# Source : https://gist.github.com/EvieePy/ab667b74e9758433b3eb806c53a19f34

from async_timeout import timeout
from functools import partial
from .CustomQueue import CustomQueue

import asyncio
import discord

from youtube_dl import YoutubeDL

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


class YTDLError(Exception):
    pass


class YTDLSource(discord.PCMVolumeTransformer):

    FFMPEG_OPTIONS = {
        'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
        'options': '-vn',
    }

    def __init__(self, source, *, data, requester):
        super().__init__(source)
        self.requester = requester
        self.title = data.get('title')
        self.web_url = data.get('webpage_url')

    def __getitem__(self, item: str):
        return self.__getattribute__(item)

    @classmethod
    async def regather_stream(cls, data, *, loop):
        """Used for preparing a stream, instead of downloading.
        Since Youtube Streaming links expire."""
        loop = loop or asyncio.get_event_loop()
        requester = data['ctx'].author

        to_run = partial(ytdl.extract_info,
                         url=data['search'], download=False)
        data = await loop.run_in_executor(None, to_run)

        return cls(discord.FFmpegPCMAudio(data['url']), data=data, requester=requester)


class AudioPlayer:

    def __init__(self, ctx):
        self.bot = ctx.bot
        self._guild = ctx.guild
        self._channel = ctx.channel
        self._cog = ctx.cog
        self.queue = CustomQueue()
        self.next = asyncio.Event()
        self.current = None
        self.bot.loop.create_task(self.player_loop())

    async def _getclient(self):
        """Get the current audio client for this bot"""
        if(self._guild.voice_client is None):  # Check to see if the voice client exists
            try:
                await self._channel.connect()
            except (asyncio.TimeoutError, AttributeError):
                await self._channel.send(f'Problem getting the audio player.  Bye bye. ;-;')
                self.destroy(self._guild)
                return None
        return self._guild.voice_client

    async def player_loop(self):
        await self.bot.wait_until_ready()

        while not self.bot.is_closed():

            self.next.clear()

            try:
                # Wait for the next song. If we timeout cancel the player and disconnect...
                async with timeout(300):  # 5 minutes...
                    source = await self.queue.get()
            except asyncio.TimeoutError:
                print('Bot disconnecting due to no new song requests.')
                return self.destroy(self._guild)

            try:
                source = await YTDLSource.regather_stream(source, loop=self.bot.loop)
            except Exception as e:
                await self._channel.send(f'There was an error processing your song.\n'
                                         f'```css\n[{e}]\n```')
                continue

            self.current = source
            client = await self._getclient()

            if(client is None):
                continue

            client.play(
                source, after=lambda _: self.bot.loop.call_soon_threadsafe(self.next.set))

            await self._channel.send(f'**Now Playing:** `{source.title}` requested by '
                                     f'`{source.requester}`')
            await self.next.wait()

            # Make sure the FFmpeg process is cleaned up.
            source.cleanup()
            self.current = None

    def destroy(self, guild):
        print('Bot recieved not new music.  Closing.')
        return self.bot.loop.create_task(self._cog.cleanup(guild))
