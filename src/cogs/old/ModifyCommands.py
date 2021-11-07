"""

Commands relating to the modification of quotes.

@author: Oliver Clarke
@date: 10/04/2021

"""
from discord.ext import commands
from helpers import DataHandler
import datetime


class ModifyCommands(commands.Cog):
    """Commands for controlling Hermes Quotes."""

    def __init__(self, bot):
        """Initialize important information."""
        self.bot = bot
        self.data = DataHandler.public_data

    @commands.command(
        name="add_quote",
        help="- .add_quote <name:string> <quote:string> : Add a new quote."
    )
    async def add_quote(self, ctx, name, *, arg):
        """Says hello."""
        if name not in self.data.users:
            await ctx.send('> Users has not been created.  Use .add_users to add them.')
            return

        d = datetime.datetime.now()
        ip = id(arg)

        self.data.add_quote(name, f"{d:%B %d, %Y}", ip, arg)
        await ctx.send('Adding new quote.\n >>> ID: {}\nName: {}\nDate: {}\n{}'.format(ip, name, f"{d:%B %d, %Y}", arg))

    @commands.command(
        name="remove_quote",
        help="- .remove_quote <id:int> : Removes a quote"
    )
    async def remove_quote(self, ctx, id: int):
        """Says hello."""
        result = self.data.remove_quote(id)
        if result is True:
            await ctx.send('> Removed quote')
        else:
            await ctx.send('> Failed to remove quote.  Check if the ID is correct.')

    @commands.command(
        name='add_name',
        help="- .add_name <name:string> : Add a new user to Quotes."
    )
    async def add_name(self, ctx, name):
        """Short summary."""
        if name in self.data.users:
            await ctx.send('> Name "{}" already exists.  Use .names to see all names.'.format(name))
            return

        self.data.add_user(name)
        await ctx.send('> Adding new name - {}'.format(name))


def setup(bot):
    """Short summary."""
    bot.add_cog(ModifyCommands(bot))
