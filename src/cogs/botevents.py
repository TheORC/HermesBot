from discord.ext import commands


class BotEvents(commands.Cog):

    def __init__(self, bot):
        """Initialize important information."""
        self.bot = bot


def setup(bot):
    bot.add_cog(BotEvents(bot))
