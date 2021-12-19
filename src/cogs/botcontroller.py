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

from ..helpers import AudioManager, GuildSettings
from ..utils import smart_print

import asyncio


class BotController(commands.Cog):

    def __init__(self, bot):
        """Initialize important information."""
        self.bot = bot
        self.audio_manager = AudioManager(bot)

    async def handle_disconnection(self, guild):
        await self.audio_manager.clear_audio_player(guild)

    @commands.command(name='connect',
                      aliases=['join'],
                      help="- Call bot to your voice channel.")
    async def player_connect(self, ctx, play_quote: bool = True):

        try:
            channel = ctx.author.voice.channel
        except AttributeError:
            return await smart_print(ctx, 'The bot can only be summoned from a voice channel')  # noqa

        vc = ctx.voice_client

        # Check if the vc already exists
        if(vc):

            if(self.audio_manager.has_player(ctx) is False):
                voice_state = ctx.guild.voice_client
                await voice_state.disconnect()
                await channel.connect()
            else:
                # Check if the bot is already in the voice channel
                if(vc.channel.id == channel.id):
                    print('Already in the same channel')
                    return
                # Connect to the new voice channel
                try:
                    print('Moving to channel')
                    await vc.move_to(channel)
                except asyncio.TimeoutError:
                    return await smart_print(ctx, 'Moving to channel: <%s> timed out.', data=[channel])  # noqa
        else:
            # The bot is not in a voice channel.  Lets join one
            try:
                print('Connecting to channel')
                await channel.connect()
            except asyncio.TimeoutError:
                return await smart_print(ctx, 'Connecting to channel: <%s> timed out.', data=[channel])  # noqa

        # if play_quote:
        #    await self.audio_manager.on_bot_join_channel(ctx, ctx.guild)

        await smart_print(ctx, 'Connected to: **%s**', data=[channel])

    @commands.command(name='disconnect',
                      aliases=['leave', 'go', 'goaway', 'go-away', 'stop'],
                      help="- Ask the bot to leave the voice channel.")
    async def player_disconnect(self, ctx):
        vc = ctx.voice_client

        if(not vc or not vc.is_connected()):
            return await smart_print(ctx, 'The bot is not connected to a channel.')  # noqa

        # Clean up the bot, its time for it to go.
        # await self.audio_manager.clear_audio_player(ctx.guild)
        await vc.disconnect()

    @commands.command(
        name="play",
        aliases=['p'],
        help="- <url:string | search:string> : Adds a song to the queue."
    )
    async def play_song(self, ctx, *, search: str = None):

        await ctx.invoke(self.player_connect)

        # No search was provided.  Maybe we need to resume?
        if(search is None):
            if self.audio_manager.can_resume(ctx):
                return await ctx.invoke(self.resume_song)
            else:
                return await smart_print(ctx, 'Command missing arguments. Use .help for additional information.')  # noqa

        # In some cases the bot may have been disconnected
        # manualy.  If this is the case, then the voice_client
        # exsists but is not conected.  Lets handle that now.
        vc = ctx.voice_client

        # Check if the bot needs connecting
        # if (not vc or not ctx.voice_client.is_connected()):

        vc = ctx.voice_client
        if(not vc):
            print('The bot was unable to create a voice client.')
            return

        # No resume.  This is a new song request.
        await self.audio_manager.play(ctx, search)

    @commands.command(
        name='play_quote',
        aliases=['pq'],
        description='- <ID:int> : Plays a quote with the specified ID.'
    )
    async def play_quote(self, ctx, id: int):
        await ctx.invoke(self.player_connect, play_quote=False)

        if id is None:
            return await smart_print(ctx, 'Command missing arguments. Use .help for additional information.')  # noqa

        # await self.audio_manager.play_quote(ctx, id)

    @commands.command(name="playnext",
                      aliases=['pn'],
                      help="- Adds a song to the top of the queue.")
    async def play_song_next(self, ctx, *, search: str = None):

        # No search was provided.  Maybe we need to resume?
        if(search is None):
            if self.audio_manager.can_resume(ctx):
                return await ctx.invoke(self.resume_song)
            else:
                return await smart_print(ctx, 'Command missing arguments. Use .help for additional information.')  # noqa

        vc = ctx.voice_client
        if (not vc):
            await ctx.invoke(self.player_connect)

        vc = ctx.voice_client
        if(not vc):
            print('The bot was unable to create a voice client.')
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

    @commands.command(name='clear', help='- Clear the current queue of songs.')
    async def clear_queue(self, ctx):
        await self.audio_manager.clear_queue(ctx)

    @commands.command(name='music_volume', aliases=['mvol'],
                      help='- <[1-100]: int> Sets the volume for music.')
    async def set_music_volume(self, ctx, volume: float):

        if volume < 0 or volume > 100:
            return await smart_print(ctx, 'The volume needs to be in the range of 1-100.')  # noqa

        guild_settings = GuildSettings(ctx.guild.id)
        guild_settings.save_music_volume(volume/100)

        await self.audio_manager.set_volume(ctx, volume)

    @commands.command(name='quote_volume', aliases=['qvol'],
                      help='- <[1-100]: int> Sets the volume for quotes.')
    async def set_quote_volume(self, ctx, volume: float):

        if volume < 0 or volume > 100:
            return await smart_print(ctx, 'The volume needs to be in the range of 1-100.')  # noqa

        guild_settings = GuildSettings(ctx.guild.id)
        guild_settings.save_quote_volume(volume/100)

        await smart_print(ctx, 'Quote volume set to **%s%**', data=[volume])


def setup(bot):
    bot.add_cog(BotController(bot))
