"""

Commands relating to the modification of quotes.

@author: Oliver Clarke
@date: 10/04/2021

"""
from discord.ext import commands
from DataHandler import DataHandler

import datetime
import random


class RetreiveCommands(commands.Cog):
    """Commands for controlling Hermes Quotes."""

    def __init__(self, bot):
        """Initialize important information."""
        self.bot = bot
        self.data = DataHandler.public_data

    @commands.command(
        name='names',
        help=" - .names : Display all names."
    )
    async def names(self, ctx):
        """Display names."""
        name_list = '\n'.join([x for x in self.data.list_names()])
        await ctx.send('Names\n >>> {}'.format(name_list))

    @commands.command(
        name='random',
        help=" - .random : Display a random quote."
    )
    async def random(self, ctx):
        """Display names."""
        quotes = self.data.get_quotes()
        quotes = quotes[random.randint(0, len(quotes)-1)]

        output = '\"{}\"\n{} - {}'.format(quotes['string'],
                                          quotes['name'], quotes['date'])

        await ctx.send('>>> {}'.format(output))

    @commands.command(
        name='quote_author',
        help=' - .quotes_author <name:string> : Display quotes from an author'
    )
    async def quote_author(self, ctx, author):
        """Short summary."""
        if author not in self.data.users:
            await ctx.send('> No name found <' + author + '>.  Use .names to find all names.')
            return

        # Retrieve quotes by author
        quotes = self.data.find_quotes_name(author)

        if len(quotes) == 0:
            await ctx.send('> Author <' + author + '> does not have any quotes.')
            return

        output = ''
        for q in quotes:
            output = output + '\"' + q['string'] + \
                '\"\n' + author + ' - ' + q['date'] + '\n\n'

        # Send to discord
        await ctx.send('>>> {}'.format(output))

    @commands.command(
        name='quote_id',
        help=' - .quote_id <id:int> : Display a specific quote.'
    )
    async def quote_id(self, ctx, id: int):
        """Short summary."""
        quote = self.data.find_quote_id(id)

        if quote is None:
            await ctx.send('> Quote with id <{}> does not exist.'.format(id))
            return

        output = '\"{}\"\n{} - {}'.format(quote['string'],
                                          quote['name'], quote['date'])

        # Send to discord
        await ctx.send('>>> {}'.format(output))

    @ commands.command(
        name='quotes_all',
        help="- .quotes_all : Display all quotes."
    )
    async def quotes_all(self, ctx):
        """Display names."""
        output = '\n'.join([str(x) for x in self.data.get_quotes()])
        await ctx.send('>>> {}'.format(output))


def setup(bot):
    """Short summary."""
    bot.add_cog(RetreiveCommands(bot))
