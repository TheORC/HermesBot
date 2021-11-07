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
'''

from discord.ext import commands
from ..helpers import AudioManager

import asyncio


class BotController(commands.Cog):

    def __init__(self, bot):
        """Initialize important information."""
        self.bot = bot
        self.audio_manager = AudioManager()

    async def _sm(self, ctx, message: str):
        await ctx.send(f'`{message}`')

    async def clean_up(self, guild):
        await self.audio_manager.clean_up_player(guild)

    @commands.command(name='connect',
                      aliases=['join'],
                      help="- Call bot to your voice channel.")
    async def player_connect(self, ctx):

        try:
            channel = ctx.author.voice.channel
        except AttributeError:
            return await self._sm(ctx, 'You must be in a channel to summon the bot.')  # noqa

        vc = ctx.voice_client

        if(vc):
            if(vc.channel.id == channel.id):
                return
            try:
                await vc.move_to(channel)
            except asyncio.TimeoutError:
                return await self._sm(ctx, f'Moving to channel: <{channel}> timed out.')  # noqa
        else:
            try:
                await channel.connect()
            except asyncio.TimeoutError:
                return await self._sm(ctx, f'Connecting to channel: <{channel}> timed out.')  # noqa

        await self._sm(ctx, f'Connected to: **{channel}**')

    @commands.command(name='disconnect',
                      aliases=['leave', 'go', 'goaway', 'go-away', 'stop'],
                      help="- Ask the bot to leave the voice channel.")
    async def player_disconnect(self, ctx):
        vc = ctx.guild.voice_client
        if(not vc or not vc.is_connected()):
            return await self._sm(ctx, 'The bot is not connected to a channel')
        await self.clean_up(ctx.guild)

    @commands.command(
        name="play",
        help="- <url:string | search:string> : Adds a song to the queue."
    )
    async def play_song(self, ctx, *, search=None):
        vc = ctx.voice_client
        if (not vc):
            await ctx.invoke(self.player_connect)

        vc = ctx.voice_client
        if(not vc):
            return

        if(search is None):
            await ctx.invoke(self.resume_song)
            return

        await self.audio_manager.play(ctx, search)

    @commands.command(name="playnext",
                      aliases=['pn'],
                      help="- Adds a song to the top of the queue.")
    async def play_song_next(self, ctx, *, search=None):
        vc = ctx.voice_client
        if (not vc):
            await ctx.invoke(self.player_connect)

        vc = ctx.voice_client
        if(not vc):
            return

        if(search is None):
            await self._sm(ctx, 'No song provided')
            return

        await self.audio_manager.play(ctx, search, playnext=True)

    @commands.command(name='pause',
                      help="- Pause the music.")
    async def pause_song(self, ctx):
        await self.audio_manager.pause(ctx)

    @commands.command(name='resume',
                      help="- Resume the music.")
    async def resume_song(self, ctx):
        await self.audio_manager.resume(ctx)

    @commands.command(name='skip',
                      aliases=['next'],
                      help="- Skips the current song.")
    async def skip_song(self, ctx):
        await self.audio_manager.skip(ctx)

    @commands.command(name='queue',
                      aliases=['q', 'playlist'],
                      help="- Shows the current music queue.")
    async def play_queue(self, ctx):
        await self.audio_manager.display_playing_queue(ctx)

    @commands.command(name='playing',
                      aliases=['now', 'current', 'np'],
                      help="- Display the title of the song playing.")
    async def play_current(self, ctx):
        await self.audio_manager.show_song_playing(ctx)

    @commands.command(name='shuffle', aliases=['sh'],
                      help="- Shuffles the current song queue.")
    async def shuffle(self, ctx):
        await self.audio_manager.shuffle(ctx)


def setup(bot):
    bot.add_cog(BotController(bot))