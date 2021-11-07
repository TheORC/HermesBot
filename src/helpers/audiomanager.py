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

from .audioplayer import AudioPlayer
from ..utils import get_full_info, get_quick_info

import itertools
import discord


class AudioManager:
    """Class used to manage all bots.

    This class controlls communications with bots connected
    to different guilds.  It works in tandem with botcontroller.py
    to process commands and execute them.
    """

    def __init__(self):
        self.players = {}

    def _resolve_video_urls(self, list):
        """
        Resolve video information from a list of urls.
        This uses you `YoutubeDL.extract_info()` to retrieve
        video information.

        :param list: The list of urls to resolve
        :return: List of resolved urls
        """
        results = []
        for item in list:
            res = get_full_info(item['search'])  # Perform the search

            # Handle cases where a list is returned
            if('entries' in res):
                en_list = list(res.get('entries'))
                if(len(en_list) >= 1):
                    res = res.get('entries')[0]
                else:
                    res = {'title': 'None'}

            results.append(res)
        return results

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

    async def clean_up_player(self, guild):
        """
        Properly dispose of an `AudioPlayer()` when it is
        no longer needed.

        :param guild: guild which is removing `AudioPlayer()`
        """
        try:
            # Try and discconect the voice_client
            await guild.voice_client.disconnect()
        except AttributeError:
            pass

        try:
            # Free up memory
            del self.players[guild]
        except KeyError:
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

        if search is None:
            return await ctx.send('> Audio URL not specified. Did you mean to resume?')  # noqa

        # Get the channel we are playing in
        player = self._get_player(ctx)

        # Get the quick YouTube information from the search provided.
        results = get_quick_info(search)

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
            await ctx.send(f'```ini\n[Adding {len(entries)} songs to the Queue.]\n```')  # noqa

            for e in entries:
                items = {}
                items['ctx'] = ctx

                # Since the playlist was not processed, the urls need to be
                # constructed manualy.
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

            await ctx.send(f'```ini\n[Adding "{results["title"]}" to the Queue.]\n```')  # noqa

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
        if(not vc or not vc.is_playing()):
            return await ctx.send('> The bot is not currently playing anything.')  # noqa

        # We dont do anything if it is already paused
        if(vc.is_paused()):
            return

        vc.pause()

    async def resume(self, ctx):
        """
        Resume an `AudioPlayer()` if it is in a voice channel.
        """
        vc = ctx.voice_client

        if(not vc or not vc.is_connected()):
            return await ctx.send('> The bot is not currently playing anything.')  # noqa

        if(vc.is_playing()):
            return

        vc.resume()

    async def skip(self, ctx):
        """
        Skips the current song playing.
        """

        vc = ctx.voice_client

        if(not vc or not vc.is_connected()):
            return await ctx.send('> The bot is not currently playing anything.')  # noqa

        # Do nothing when it is not playing
        if(not vc.is_playing()):
            return

        vc.stop()
        await ctx.send(f'> **`{ctx.author}`**: Skipped the song!')

    async def show_song_playing(self, ctx):
        """
        Display information about the currently playing song.
        """
        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            return await ctx.send('> The bot is not currently connected to voice.')  # noqa

        # Get the AudioPlayer() for the current user
        player = self._get_player(ctx)

        # Check if the AudioPlayer() is playing anything
        if not player.current:
            return await ctx.send('> The bot is not currently playing anything.')  # noqa

        await ctx.send(f'**Now Playing:** `{vc.source.title}` '
                       f'requested by `{vc.source.requester}`')

    async def display_playing_queue(self, ctx):
        """
        Retrieve a basic queue of upcoming songs.
        """
        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            return await ctx.send('I am not currently connected to voice!')

        player = self._get_player(ctx)

        # Check if there is songs in the queue
        if player.queue.empty():
            return await ctx.send('> There are currently no queued songs.')

        # Create a message and store it we want to reuse the same
        # message later.
        np = await ctx.send('> Fetching queue.  Please Wait.')

        # Grab up to 5 entries from the queue...
        upcoming = list(itertools.islice(player.queue._queue, 0, 5))

        # Get infomration about the upcoming songs.  At the moment
        # I am only intrested in titles, however, this could be
        # expanded to other things such as the video author.
        songs = self._resolve_video_urls(upcoming)

        fmt = '\n'.join(f'**`{_["title"]}`**' for _ in songs)
        embed = discord.Embed(
            title=f'Upcoming - Next {len(upcoming)}', description=fmt)

        await ctx.send(embed=embed)

        try:
            # Delete the please wait message
            await np.delete()
        except discord.HTTPException:
            pass

    async def shuffle(self, ctx):
        """
        Shuffles all the songs in an `AudioPlayer()`.
        """

        vc = ctx.voice_client
        if(not vc):
            return await ctx.send('> The bot is not currently in a voice channel.')  # noqa

        player = self._get_player(ctx)

        # We dont do anything if there are no songs
        if(player.queue.empty()):
            return await ctx.send('> There are no songs in queue to be shuffled.')  # noqa

        player.queue.shuffle_queue()
        await ctx.send('> Queue finished shuffling.')