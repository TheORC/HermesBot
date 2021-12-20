from discord.ext import commands
from ..helpers import QuoteManager
from ..utils import smart_print


class QuoteController(commands.Cog):

    def __init__(self, bot):
        """Initialize important information."""
        self.bot = bot
        self.qm = QuoteManager(self.bot)

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        """
        This method is called when a reaction changes on a message.
        This is used to check if a user has requested another page
        on a `multipage` embed message.
        """

        # Check for user emotes.  The bot does not count.
        if not user.bot:
            await self.qm.on_emote_update(reaction, user)

    @commands.command(
        name="users",
        help="- optional [(add | remove) <name:string>]"
    )
    async def user_commands(self, ctx, command=None, *, args=None):

        # What are we doing with this command?
        if command is None:
            return await self.qm.get_guild_users(ctx)

        # Handle user commands
        command = command.lower()

        # We have a command
        if command == 'add':
            return await self.qm.add_user(ctx, args)
        elif command == 'remove':
            return await self.qm.remove_user(ctx, args)
        else:
            return await smart_print(ctx, 'Unknown command. Check .help for command usage.')  # noqa

    @commands.command(
        name="add",
        help="- <name:string> <quote:string> : Add a new quote."
    )
    async def add_quote(self, ctx, name, *, args):
        await self.qm.add_user_quote(ctx, name, args)

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
            return await self.qm.get_user_quotes(ctx, args)
        elif command == 'id':
            if not args:
                return await smart_print(ctx, 'Unknown command. Check .help for command usage.')  # noqa
            return await self.qm.get_quote_from_id(ctx, args)
        elif command == 'all':
            return await self.qm.get_all_guild_quotes(ctx)
        else:
            return await smart_print(ctx, 'Unknown command. Check .help for command usage.')  # noqa

    @commands.command(
        name="remove",
        help="- <id:int> Removes the quote with the provided id."
    )
    async def remove_quote(self, ctx, id: int):
        if(not id):
            return await smart_print(ctx, 'Unknown command. Check .help for command usage.')  # noqa
        await self.qm.remove_user_quote(ctx, id)


def setup(bot):
    bot.add_cog(QuoteController(bot))
