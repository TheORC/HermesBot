from discord.ext import commands
from ..helpers import DatabaseManager
from dotenv import load_dotenv

import os
import discord


class QuoteController(commands.Cog):

    def __init__(self, bot):
        """Initialize important information."""
        self.bot = bot

        load_dotenv()
        db_host = os.getenv('DB_HOST')
        db_name = os.getenv('DB_NAME')

        self.db_manager = DatabaseManager(db_host, db_name)
        self.db_manager.connect()

    def _contains_user(self, username, users):
        for user in users:
            if user[2].lower() == username.lower():
                return user
        return None

    async def _add_user(self, ctx, name):

        if(not name):
            return await ctx.send('No name was provided.')

        # Lets see if the name already exists
        users = self.db_manager.get_users(ctx.guild.id)
        user = self._contains_user(name, users)
        if(user):
            # This name does exist!  Oh no
            return await ctx.send('This name is already in the database.')

        # Ahhhhh shiiiiiit
        guild_id = ctx.guild.id

        self.db_manager.add_user(guild_id, name)
        return await ctx.send(f'Added user {name}')

    async def _remove_user(self, ctx, name):
        if(not name):
            return await ctx.send('No name was provided.')

        # Lets see if the name already exists
        users = self.db_manager.get_users(ctx.guild.id)
        user = self._contains_user(name, users)
        if(not user):
            # This name does exist!  Oh no
            return await ctx.send('This name is not in the database.')

        # What do you do here!
        self.db_manager.remove_user(ctx.guild.id, user[0])
        await ctx.send('The user has been deleted.  There quotes have also been removed.')

    async def _get_user_quotes(self, ctx, name):
        quotes = []

        # First, we need to get all the users
        users = self.db_manager.get_users(ctx.guild.id)
        user = self._contains_user(name, users)
        if(not user):
            return await ctx.send(f'The user "{name}" could not be found')

        user_quotes = self.db_manager.get_user_quote(ctx.guild.id, name)
        for quote in user_quotes:
            quotes.append([quote[0], quote[2], quote[4], quote[5]])

        fmt = '\n'.join(f'**`ID ({_[0]}) : {_[2]}`**' for _ in quotes)
        embed = discord.Embed(title=f"{user[2]}'s Quotes", description=fmt)
        await ctx.send(embed=embed)

    async def _get_id_quote(self, ctx, id):
        quotes = self.db_manager.get_id_quote(ctx.guild.id, id)
        if len(quotes) == 0:
            return await ctx.send(f'No quote with the id "{id}" was found')

        quote = quotes[0]
        await ctx.send(f'**`{quote[2]}: {quote[4]}`**')

    async def _get_all_quotes(self, ctx):
        quotes = []

        # First, we need to get all the users
        users = self.db_manager.get_users(ctx.guild.id)

        for user in users:
            # Get all the users quotes
            user_quotes = self.db_manager.get_user_quote(ctx.guild.id, user[2])

            for quote in user_quotes:
                quotes.append([quote[2], quote[4], quote[5]])

        fmt = '\n'.join(f'**`{_[0]}: {_[1]}`**' for _ in quotes)
        embed = discord.Embed(title='All Quotes', description=fmt)
        await ctx.send(embed=embed)

    @commands.command(
        name="users",
        help="- optional [(add | remove) <name:string>]"
    )
    async def user_commands(self, ctx, command=None, *, args=None):

        # What are we doing with this command?
        if command is None:
            users = self.db_manager.get_users(ctx.guild.id)
            fmt = '\n'.join(f'**`{_[2]}`**' for _ in users)
            embed = discord.Embed(title='Users', description=fmt)
            return await ctx.send(embed=embed)

        command = command.lower()

        # We have a command
        if command == 'add':
            return await self._add_user(ctx, args)
        elif command == 'remove':
            return await self._remove_user(ctx, args)
        else:
            return await ctx.send('Unknown command. Check .help for command usage.')

    @commands.command(
        name="add",
        help="- <name:string> <quote:string> : Add a new quote."
    )
    async def add_quote(self, ctx, name, *, arg):
        """Says hello."""

        users = self.db_manager.get_users(ctx.guild.id)
        user = self._contains_user(name, users)

        # We only add a quote if the user exsists
        if(not user):
            return await ctx.send('The user "{}" is not in the database. '
                                  'Please add them before creating a quote.'
                                  .format(name))

        # We need the guild id for a quote
        guild_id = ctx.guild.id
        try:
            quote_id = self.db_manager.add_user_quote(user[0], guild_id, arg)
            await ctx.send(f'Added quote with id({quote_id}) for user {user[2]}')
        except Exception as e:
            print(e)
            await ctx.send(':( there was a problem adding your quote.')

    @commands.command(
        name="quotes",
        help="- [user <name:string> | id <id:int> | all <DANGER>]"
    )
    async def get_all_quotes(self, ctx, command=None, *, args=None):

        if not command:
            return await ctx.send('Unknown command. Check .help for command usage')

        command = command.lower()

        if command == 'user':
            if not args:
                return await ctx.send('Please provide a name.')
            return await self._get_user_quotes(ctx, args)
        elif command == 'id':
            if not args:
                return await ctx.send('Please provide an Id.')
            return await self._get_id_quote(ctx, args)
        elif command == 'all':
            return await self._get_all_quotes(ctx)
        else:
            return await ctx.send('Unknown command. Check .help for command usage')

    @commands.command(
        name="remove",
        help="- <id:int> Removes the quote with the provided id."
    )
    async def remove_quote(self, ctx, id: int):

        if(not id):
            return await ctx.send('Please provided the quotes id.')

        quote = self.db_manager.get_id_quote(ctx.guild.id, id)
        if len(quote) == 0:
            return await ctx.send(f'No quote with the id "{id}" was found')

        self.db_manager.remove_quote(ctx.guild.id, id)
        await ctx.send('Removed quote.')


def setup(bot):
    bot.add_cog(QuoteController(bot))
