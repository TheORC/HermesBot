from discord.ext import commands
from ..helpers import DatabaseManager, TTSManager
from ..utils import smart_print, PageEmbedManager

from dotenv import load_dotenv

import os
import discord


class QuoteController(commands.Cog):

    def __init__(self, bot):
        """Initialize important information."""
        self.bot = bot
        self.db_manager = DatabaseManager()
        self.embed_manager = PageEmbedManager()

        load_dotenv()
        tts_path = os.getenv('TTS_PATH')
        self.tts_manager = TTSManager(bot, filepath=tts_path)

    def _contains_user(self, username, users):
        for user in users:
            if user[2].lower() == username.lower():
                return user
        return None

    def _trim_quote(self, quote):
        if len(quote) > 1024:
            quote = quote[:1021] + '...'
        return quote

    def _get_next_segment(self, data):

        length = len(data)

        if length > 1024:
            last_index = data.rfind('- **')
            temp = data[:1024]
            text = temp[:last_index]
        else:
            text = data

        return last_index, text, data[:0]

    async def _check_for_missing_tts(self, ctx, guildid):

        missing = self.db_manager.get_missing_tts(guildid)

        await smart_print(ctx, 'Found **%s** objects with missing TTS.  Fixing.',  # noqa
                          data=[len(missing)])

        for quote in missing:
            file_name = f'{quote[0]}_{quote[2]}_{quote[1]}'
            await self.tts_manager.quote_to_tts(quote[0], quote[3], file_name)

    async def _add_user(self, ctx, name):

        if(not name):
            return await smart_print(ctx, 'Command missing arguments. Use .help for additional information.')  # noqa

        # Lets see if the name already exists
        users = self.db_manager.get_users(ctx.guild.id)
        user = self._contains_user(name, users)
        if(user):
            # This name does exist!  Oh no
            return await smart_print(ctx, 'This name has already been added.')

        # Ahhhhh shiiiiiit
        guild_id = ctx.guild.id

        self.db_manager.add_user(guild_id, name)
        return await smart_print(ctx, 'Added user **%s** to the database.',
                                 data=[name])

    async def _remove_user(self, ctx, name):
        if(not name):
            return await smart_print(ctx, 'Command missing arguments. Use .help for additional information.')  # noqa

        # Lets see if the name already exists
        users = self.db_manager.get_users(ctx.guild.id)
        user = self._contains_user(name, users)
        if(not user):
            # This name does exist!  Oh no
            return await smart_print(ctx, 'This name is not in the database.')

        # What do you do here!
        self.db_manager.remove_user(ctx.guild.id, user[0])
        await smart_print(ctx, 'The user **%s** has been deleted.',
                          data=[name])

    async def _get_user_quotes(self, ctx, name):

        # First, we need to get all the users
        users = self.db_manager.get_users(ctx.guild.id)
        user = self._contains_user(name, users)
        if(not user):
            return await smart_print(ctx, 'The user **%s** is not in the database.',  # noqa
                                     data=[name])

        user_quotes = self.db_manager.get_user_quote(ctx.guild.id, name)
        quotes = []

        for quote in user_quotes:
            quotes.append([quote[0], quote[4]])

        embed = self.embed_manager.CreateEmbed(
            title=f"{name}'s quotes",
            description=f'There is a total of **{len(quotes)}** quotes',
            inline=False
        )
        embed.add_items(quotes)
        await self.embed_manager.send(ctx, embed)

    async def _get_id_quote(self, ctx, id):
        quotes = self.db_manager.get_id_quote(ctx.guild.id, id)

        if len(quotes) == 0:
            return await smart_print(ctx, 'The quote with id **%s**` does not exist',  # noqa
                                     data=[id])

        quote = quotes[0]

        embed = discord.Embed(
            title=f"{quote[2]}'s Quote",
            color=discord.Colour.dark_teal(),
            description=self._trim_quote(quote[4])
            )
        await ctx.send(embed=embed)

    async def _get_all_quotes(self, ctx):

        # First, we need to get all the users
        users = self.db_manager.get_users(ctx.guild.id)

        print(users)

        # test_embed = MultiPageEmbed()

        quotes = []

        for user in users:
            # Get all the users quotes
            user_quotes = self.db_manager.get_user_quote(ctx.guild.id, user[2])

            print(user_quotes)

            for quote in user_quotes:
                quotes.append([f'{user[2]} - {quote[0]}', quote[4]])

        embed = self.embed_manager.CreateEmbed(
            title='All Quotes',
            description=f'There is a total of **{len(quotes)}** quotes',
            color=discord.Colour.dark_teal(),
            inline=False
            )
        embed.add_items(quotes)
        await self.embed_manager.send(ctx, embed)

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):

        if not user.bot:  # Check for user emotes.  The bot does not count.
            # Get the embedable
            embedable = await self.embed_manager.check(reaction.message.id,
                                                       reaction.emoji)
            # Does it exist?
            if embedable:
                # Remove the user interaction
                await reaction.remove(user)
                await reaction.message.edit(embed=embedable)

    @commands.command(
        name="users",
        help="- optional [(add | remove) <name:string>]"
    )
    async def user_commands(self, ctx, command=None, *, args=None):

        # What are we doing with this command?
        if command is None:
            users = self.db_manager.get_users(ctx.guild.id)
            fmt = '\n'.join(f'**{_[2]}**' for _ in users)
            embed = discord.Embed(
                title='Users', color=discord.Colour.dark_teal(),
                description=fmt)
            return await ctx.send(embed=embed)

        command = command.lower()

        # We have a command
        if command == 'add':
            return await self._add_user(ctx, args)
        elif command == 'remove':
            return await self._remove_user(ctx, args)
        else:
            return await smart_print(ctx, 'Unknown command. Check .help for command usage.')  # noqa

    @commands.command(
        name="add",
        help="- <name:string> <quote:string> : Add a new quote."
    )
    async def add_quote(self, ctx, name, *, args):
        """Says hello."""

        users = self.db_manager.get_users(ctx.guild.id)
        user = self._contains_user(name, users)

        # We only add a quote if the user exsists
        if(not user):
            return await smart_print(ctx,
                                     'User **%s** is not in the database. '
                                     'Add them before creating a quote.',
                                     data=[name])

        # We need the guild id for a quote
        guild_id = ctx.guild.id
        try:
            # Send the quote to the database
            quote_id = self.db_manager.add_user_quote(user[0], guild_id, args)
            await smart_print(ctx, 'Added quote for the user **%s** with an id of **%s**.',  # noqa
                              data=[user[2], quote_id])

            # Generate tts filename
            file_name = f'{quote_id}_{guild_id}_{user[0]}'

            # Create tts audio file
            await self.tts_manager.quote_to_tts(quote_id, args, file_name)
        except Exception as e:
            print(e)
            await smart_print(ctx, 'Unable to create due to an unknown error.')

    @commands.command(
        name="quotes",
        help="- [user <name:string> | id <id:int> | all <DANGER>]"
    )
    async def get_all_quotes(self, ctx, command=None, *, args=None):

        if not command:
            return await smart_print(ctx, 'Unknown command. Check .help for command usage.')  # noqa

        command = command.lower()

        if command == 'user':
            if not args:
                return await smart_print(ctx, 'Unknown command. Check .help for command usage.')  # noqa
            return await self._get_user_quotes(ctx, args)
        elif command == 'id':
            if not args:
                return await smart_print(ctx, 'Unknown command. Check .help for command usage.')  # noqa
            return await self._get_id_quote(ctx, args)
        elif command == 'all':
            return await self._get_all_quotes(ctx)
        else:
            return await smart_print(ctx, 'Unknown command. Check .help for command usage.')  # noqa

    @commands.command(
        name="remove",
        help="- <id:int> Removes the quote with the provided id."
    )
    async def remove_quote(self, ctx, id: int):

        if(not id):
            return await smart_print(ctx, 'Unknown command. Check .help for command usage.')  # noqa

        quote = self.db_manager.get_id_quote(ctx.guild.id, id)
        if len(quote) == 0:
            return await smart_print(ctx, 'Quote with id **%s** not found.',
                                     data=[id])

        self.db_manager.remove_quote(ctx.guild.id, id)
        await smart_print(ctx, 'Quote removed successfully.')

    @commands.command(
        name="fix_tts",
        help="- Sometimes something goes wrong.  This fixes it."
    )
    async def fix_tts(self, ctx):
        await self._check_for_missing_tts(ctx, ctx.guild.id)
        await smart_print(ctx, 'Finished fixing TTS.')


def setup(bot):
    bot.add_cog(QuoteController(bot))
