# -*- coding: utf-8 -*-
'''
Copyright (c) 2021 Oliver Clarke.

This file is part of HermesBot.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.


This file makes use of code found at the following address.
Source : https://gist.github.com/EvieePy/ab667b74e9758433b3eb806c53a19f34
'''

import discord
import asyncio

from async_timeout import timeout
from functools import partial
from ..utils import CustomQueue, get_full_info, smart_print


class FileSource(discord.PCMVolumeTransformer):

    def __init__(self, source, *, data, requester):
        super().__init__(source)

        self.requester = requester
        self.filename = data.get('filename')
        self.title = data.get('title')

    def __getitem__(self, item: str):
        return self.__getattribute__(item)

    @classmethod
    def create_source(cls, ctx, filename: str):
        data = {'filename': f'tts_files/{filename}.mp3', 'title': filename}
        return cls(discord.FFmpegPCMAudio(data['filename']), data=data, requester=ctx.author)  # noqa


class YTDLSource(discord.PCMVolumeTransformer):
    """
    This class creates a live stream AudioSource.

    Using a source url or search, this creates an
    audio source with the discord voice client can
    stream.
    """

    def __init__(self, source, *, data, requester):
        super().__init__(source)
        self.requester = requester

        self.title = data.get('title')
        self.ctx = data.get('ctx')
        self.search = data.get('search')

        self.url = f'https://www.youtube.com/watch?v={data.get("id")}'

    def __getitem__(self, item: str):
        return self.__getattribute__(item)

    @classmethod
    async def regather_stream(cls, data, *, loop):
        """Used for preparing a stream, instead of downloading.
        Since Youtube Streaming links expire."""
        loop = loop or asyncio.get_event_loop()
        author = data['ctx'].author

        # Create a request to youtube and get the response
        to_run = partial(get_full_info, url=data['search'])
        data = await loop.run_in_executor(None, to_run)

        # Create and retunr a new YTDLSource object
        return cls(discord.FFmpegPCMAudio(data['url']), data=data, requester=author)  # noqa


class AudioPlayer:
    """
    Class responsible for playing song in a discord channel.

    The `AudioPlayer()` uses a loop which waits for a new
    song to be in the queue.  It will then attempt to play the
    song.  In the event of a failure, it will either skip to
    the next song, or discconect.
    """

    def __init__(self, ctx, guild_settings):
        self.ctx = ctx
        self.guild_settings = guild_settings
        self.bot = ctx.bot
        self._guild = ctx.guild
        self._channel = ctx.channel
        self._cog = ctx.cog
        self._now_playing = None
        self.queue = CustomQueue()
        self.next = asyncio.Event()
        self.current = None

        self.volume = .05  # 5% seams like a nice starting point.
        self.audio_player = self.bot.loop.create_task(self.player_loop())

    async def _get_client(self):
        """
        Get the current audio client.

        If the `voice_client` does not exsist then bad
        things have happened. It is likely the internet
        of the machine running this has disconnected.

        :return: Guild voice_client | None
        """
        # Check to see if the voice client exists
        if(not self._guild.voice_client):
            return None
        return self._guild.voice_client

    async def player_loop(self):
        """
        The music bot loop controlling songs.

        This method contains a loop which waits for songs to appear
        in the `queue`.  When it receieves one, it attempts to play
        the song in the voice channel.

        If a song is not received in `300` seconds, the loop is
        terminated and the bot disconected from the voice channel.
        """

        await self.bot.wait_until_ready()

        # Lets loop for as loong as the bot exsists
        while not self.bot.is_closed():

            try:
                self.next.clear()

                try:
                    # Wait for the next song. If we timeout,
                    # cancel the player and disconnect...
                    async with timeout(300):  # 5 minutes...
                        source = await self.queue.get()
                except asyncio.TimeoutError:
                    await smart_print(self._channel,
                                      'No more songs.  Going to sleep.')
                    return self.destroy(self._guild)

                # Check if this is from youtube
                if not isinstance(source, FileSource):
                    try:
                        # Attempt to create the music audio stream.
                        source = await YTDLSource.regather_stream(source, loop=self.bot.loop)  # noqa
                    except Exception as e:

                        # Handle errors retreving the music stream.
                        # We dont want to end the bot, so simply alert
                        # the channel and try the next song.
                        await smart_print(self._channel,
                                          'There was an error processing your song.\n'  # noqa
                                          '```css\n[%s]\n```',
                                          data=[e])
                        continue

                    # Store the current song being played
                    volume = self.guild_settings.get_music_volume()
                else:
                    volume = self.guild_settings.get_quote_volume()

                print(f'Volume is: {volume}')

                self.current = source
                self.current.volume = volume

                client = await self._get_client()

                # If this is true, then chances are we
                # disconnected from the internet
                if(not client.is_connected()):
                    print('The client is not connected.  Just clean up...')
                    return self.destroy(self._guild)

                # Play the current audio stream
                client.play(source, after=lambda _: self.bot.loop.call_soon_threadsafe(self.next.set))  # noqa

                # self._now_playing = await self._channel.send(f'> **Now Playing:** `{source.title}` requested by '  # noqa
                #                          f'`{source.requester}`')

                # Wait for the song to finish
                await self.next.wait()

                # Make sure the FFmpeg process is cleaned up.
                source.cleanup()
                self.current = None

                # try:
                #    await self._now_playing.delete()
                # except discord.HTTPException:
                #    pass
            except asyncio.CancelledError:
                print('AudioPlayer loop cancelled Error.  Cleanup.')
                return self.destroy(self._guild)

    def destroy(self, guild):
        """
        Destory this `AudioPlayer()`

        There might be no more songs, or something went wrong.
        """
        return self.bot.loop.create_task(self._cog.handle_disconnection(guild))
