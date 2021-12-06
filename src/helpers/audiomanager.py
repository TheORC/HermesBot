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

from .audioplayer import AudioPlayer, FileSource
from .databasemanager import DatabaseManager

from ..utils import (get_full_info, get_quick_info,
                     resolve_video_urls, smart_print)

import itertools
import random
import discord


class AudioManager:
    """Class used to manage all bots.

    This class controlls communications with bots connected
    to different guilds.  It works in tandem with botcontroller.py
    to process commands and execute them.
    """

    def __init__(self, bot):
        self.bot = bot
        self.players = {}
        self.db_manager = DatabaseManager()

    def _get_player(self, ctx):
        """
        Get the `AudioPlayer()` currently in a guild. If one
        does not exsist, a new one is created.

        :return: `AudioPlayer()`

        """

        try:
            player = self.players[ctx.guild.id]
        except KeyError:
            player = AudioPlayer(ctx)
            self.players[ctx.guild.id] = player
        return player

    def has_player(self, ctx):
        if ctx.guild.id in self.players:
            return True
        return False

    def can_resume(self, ctx):
        """
        Check if an `AudioPlayer()` can be resumed.
        """
        vc = ctx.voice_client

        if(not vc or not vc.is_connected()):
            return False

        if(vc.is_playing()):
            return False

        return True

    async def on_bot_join_channel(self, ctx, guild):

        num_quotes = self.db_manager.get_number_quotes(guild.id)
        quotes = self.db_manager.get_all_quotes(guild.id)

        if(num_quotes == 0):
            return

        id = random.randrange(0, num_quotes)

        # Get the channel we are playing in
        player = self._get_player(ctx)

        # Add the random quote to the queue
        await player.queue.put(FileSource.create_source(ctx, quotes[id][5]))

    async def clear_audio_player(self, guild):
        """
        Properly dispose of an `AudioPlayer()` when it is
        no longer needed.

        :param guild: guild which is removing `AudioPlayer()`
        """
        try:
            await guild.voice_client.disconnect()
        except AttributeError:
            pass

        try:
            self.players[guild.id].audio_player.cancel()
        except Exception:
            pass

        try:
            del self.players[guild.id]
        except Exception:
            pass

    """
    The following commands are used to control an AudioPlayer
    These are invoked through commands issued in botcontroller.py
    """

    async def play(self, ctx, search, playnext=False):
        """
        Add a song for the bot to play.

        Songs are added to a first in first out queue.  This means
        songs added in the order they are played.  If a song should
        be played next, the playnext flag can be used.

        :param search: The url or search to be played
        :param playnext: Sets if song should be played next
        """

        # Get the channel we are playing in
        player = self._get_player(ctx)

        # Get the quick YouTube information from the search provided.
        results = get_quick_info(search)

        if results is False:
            await smart_print(ctx, 'No song with the search `%s` found.'
                                    ' Try a different search or use a URL instead.',  # noqa
                                    data=[search])
            return

        # This code sucks.  I should change how CustomQueue()
        # works so I dont need to do this.
        if(playnext):
            play_index = 0
        else:
            play_index = -1

        # Handle casses where a list of results were retreived.  This is
        # true when a link to a playlist was provided.
        if('entries' in results):

            # We dont want to process YouTube video if we dont have to as this
            # takes time to perform. This is asspecially true when handling
            # playlists since they can contain hundres of songs.  Because of
            # this, we simply pass the AudioPlayer() a list of urls.
            entries = list(results['entries'])
            await smart_print(ctx, '```[Adding %s songs to the queue.]```',
                              data=[len(entries)])

            # Since the playlist was not processed, the urls need to be
            # constructed manualy.
            for e in entries:
                items = {}
                items['ctx'] = ctx
                items['search'] = f'https://www.youtube.com/watch?v={e["url"]}'

                # Add the current song to the AudioPlayer() queue
                await player.queue.put(items)
        else:
            # Handle casses when single url, or a search was provided.
            # If a search was provided, we need to do a full video process to
            # find out which song YouTube think the user asked for.
            results = get_full_info(search)

            # Check if a list of videos were returned.
            if('entries' in results):
                # We will assume the first result is what the user wanted
                results = results['entries'][0]

            await smart_print(ctx, '```[Adding "%s" to the Queue.]```',
                              data=[results["title"]])

            items = {}
            items['ctx'] = ctx
            items['search'] = results['webpage_url']

            await player.queue.put(items, index=play_index)

    async def pause(self, ctx):
        """
        Pauses an `AudioPlayer()` if it is in a voice channel.
        """
        vc = ctx.voice_client

        # Check if the voice client exsists and is playing
        if(not vc or not vc.is_connected()):
            return await smart_print(ctx, 'The bot is not playing anything.')

        # We dont do anything if it is already paused
        if(vc.is_paused()):
            return await smart_print(ctx, 'The bot is already paused.')

        # Pause the bot
        await smart_print(ctx, 'Pause playing.')
        vc.pause()

    async def resume(self, ctx):
        """
        Resume an `AudioPlayer()` if it is in a voice channel.
        """
        vc = ctx.voice_client

        if(not vc or not vc.is_connected()):
            return await smart_print(ctx, 'The bot is not playing anything.')

        if(vc.is_playing()):
            return await smart_print(ctx, 'The bot is already playing.')

        await smart_print(ctx, 'Resume playing.')
        vc.resume()

    async def skip(self, ctx):
        """
        Skips the current song playing.
        """

        vc = ctx.voice_client

        if(not vc or not vc.is_connected()):
            return await smart_print('The bot is not playing anything.')

        vc.stop()
        await smart_print(ctx, '**`%s`** : Skipped the song.',
                          data=[ctx.author])

    async def show_song_playing(self, ctx):
        """
        Display information about the currently playing song.
        """
        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            return await smart_print(ctx, 'The bot is not playing anything.')

        # Get the AudioPlayer() for the current user
        player = self._get_player(ctx)

        # Check if the AudioPlayer() is playing anything
        if not player.current:
            return await smart_print(ctx, 'The bot is not playing anything.')

        embed = discord.Embed(
            color=discord.Colour.dark_teal()
        )
        embed.add_field(name='**Now Playing**',
                        value=f'[{vc.source.title}]({vc.source.url})')
        embed.add_field(name='Requested By', value=f'{vc.source.requester}')
        await ctx.send(embed=embed)

        # await smart_print(ctx,
        #                   '**Now Playing:** `[%s](%s)` requested by `%s`',
        #                   data=[vc.source.title, 'https://thelink', ])

    async def display_playing_queue(self, ctx):
        """
        Retrieve a basic queue of upcoming songs.
        """
        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            return await smart_print(ctx, 'The bot is not playing anything.')

        player = self._get_player(ctx)

        # Check if there is songs in the queue
        if player.queue.empty():
            return await smart_print(ctx, 'The queue is empty.')

        # Create a message and store it we want to reuse the same
        # message later.
        np = await ctx.send('> Fetching queue.  Please Wait.')

        # Grab up to 5 entries from the queue...
        upcoming = list(itertools.islice(player.queue._queue, 0, 5))

        # Get infomration about the upcoming songs.  At the moment
        # I am only intrested in titles, however, this could be
        # expanded to other things such as the video author.
        songs = resolve_video_urls(upcoming)

        fmt = '\n'.join(f'**`{_["title"]}`**' for _ in songs)
        embed = discord.Embed(
            title=f'Upcoming - Next {len(upcoming)}',
            color=discord.Colour.dark_teal(),
            description=fmt)

        await ctx.send(embed=embed)

        # Delete the please wait message
        try:
            await np.delete()
        except discord.HTTPException:
            pass

    async def shuffle(self, ctx):
        """
        Shuffles all the songs in an `AudioPlayer()`.
        """

        vc = ctx.voice_client
        if(not vc or not vc.is_connected()):
            return await smart_print(ctx, 'The bot is not playing anything.')

        player = self._get_player(ctx)

        # We dont do anything if there are no songs
        if(player.queue.empty()):
            return await smart_print(ctx, 'The queue is empty.')

        player.queue.shuffle_queue()
        await smart_print(ctx, 'Queue shuffled.')

    async def clear_queue(self, ctx):
        """
        Clear the queue of songs
        """

        vc = ctx.voice_client

        if(not vc or not vc.is_connected()):
            return await smart_print(ctx, 'The bot is not playing anything.')

        player = self._get_player(ctx)

        if(player.queue.empty()):
            return await smart_print(ctx, 'The queue is empty.')

        player.queue.clear_queue()
        await smart_print(ctx, 'The queue has been cleared by **%s**',
                          data=[ctx.author])

    async def set_volume(self, ctx, volume: float):

        vc = ctx.voice_client

        if(not vc or not vc.is_connected()):
            return await smart_print(ctx, 'The bot is not playing anything.')

        if(not 0 < volume <= 100):
            return await smart_print(ctx, 'Enter a value between 1 and 100')

        player = self._get_player(ctx)

        # If we are playing a song at the moment,
        # we should also change the voluem.
        if(vc.source):
            vc.source.volume = volume / 100

        player.volume = volume / 100
        await smart_print(ctx, 'Volume set to **%s%**', data=[volume])
