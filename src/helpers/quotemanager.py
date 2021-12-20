from ..database import hermes_database
from ..utils import smart_print, PageEmbedManager

import discord


class QuoteManager:

    def __init__(self, bot):

        self.bot = bot
        self.db = hermes_database()
        self.em = PageEmbedManager()

    def _contains_user(self, list, username):
        """
        Method for checking if a list contains a username.
        This is useful for checking if the database
        contains a user.
        :return: `user`
        """
        for user in list:
            if user[2].lower() == username.lower():
                return user
        return None

    async def get_guild_users(self, ctx):
        """
        Method for displaying all the users in a guild.
        """
        users = await self.db.get_guild_users(ctx.guild.id)

        fmt = '\n'.join(f'**{_[2]}**' for _ in users)
        embed = discord.Embed(
                title='Users', color=discord.Colour.dark_teal(),
                description=fmt)
        return await ctx.send(embed=embed)

    async def add_user(self, ctx, username):
        """
        Method for adding a new user to a guilds quote library.
        """

        if(not username):
            return await smart_print(ctx, 'Command missing arguments. Use .help for additional information.')  # noqa

        # Lets see if the name already exists
        users = await self.db.get_guild_users(ctx.guild.id)
        user = self._contains_user(users, username)

        # This name does exist!  Oh no
        if(user):
            return await smart_print(ctx, 'This name has already been added.')

        await self.db.add_guild_user(ctx.guild.id, username)
        return await smart_print(ctx, 'Added user **%s** to the database.',
                                 data=[username])

    async def remove_user(self, ctx, username):
        """
        Method for removing a user from a guild library.
        """

        if(not username):
            return await smart_print(ctx, 'Command missing arguments. Use .help for additional information.')  # noqa

        # Lets see if the name already exists
        users = await self.db.get_guild_users(ctx.guild.id)

        user = self._contains_user(users, username)
        if(not user):
            # This name does exist!  Oh no
            return await smart_print(ctx, 'This name is not in the database.')

        # What do you do here!
        await self.db.remove_guild_user(ctx.guild.id, user[0])
        await smart_print(ctx, 'The user **%s** has been deleted.',
                          data=[user[2]])

    async def add_user_quote(self, ctx, name, args):
        """
        Method for adding a new user quote.
        """
        users = await self.db.get_guild_users(ctx.guild.id)
        user = self._contains_user(users, name)

        # We only add a quote if the user exsists
        if(not user):
            return await smart_print(ctx,
                                     'User **%s** is not in the database. '
                                     'Add them before creating a quote.',
                                     data=[name])

        try:
            # Send the quote to the database
            await self.db.add_user_quote(ctx.guild.id, user[0], args)
            await smart_print(ctx, 'Added quote for the user **%s**.',  # noqa
                              data=[user[2]])
        except Exception:
            await smart_print(ctx, 'Unable to create due to an unknown error.')

    async def remove_user_quote(self, ctx, quoteid):

        quote = await self.db.get_quote_from_id(ctx.guild.id, quoteid)

        if len(quote) == 0:
            return await smart_print(ctx, 'Quote with id **%s** not found.',
                                     data=[quoteid])

        await self.db.remove_user_quote(ctx.guild.id, quoteid)
        await smart_print(ctx, 'Quote removed successfully.')

    async def get_user_quotes(self, ctx, username):
        """
        Method for retreiving all quotes a user in a guild has said.
        """

        # First, we need to get all the users

        users = await self.db.get_guild_users(ctx.guild.id)

        user = self._contains_user(users, username)
        if(not user):
            return await smart_print(ctx, 'The user **%s** is not in the database.',  # noqa
                                     data=[username])

        user_quotes = await self.db.get_user_quotes(ctx.guild.id, username)

        if len(user_quotes) == 0:
            return await smart_print(ctx, 'The user **%s** has no quotes.')

        quotes = []

        for quote in user_quotes:
            quotes.append([quote[0], quote[4]])

        embed = self.em.CreateEmbed(
            title=f"{username}'s quotes",
            description=f'There is a total of **{len(quotes)}** quotes',
            inline=False
        )
        embed.add_items(quotes)
        await self.em.send(ctx, embed)

    async def get_quote_from_id(self, ctx, quote_id):
        """
        Method for retreiving a quote from a guild usings the quote's id.
        """
        quotes = await self.db.get_quote_from_id(ctx.guild.id, quote_id)

        if len(quotes) == 0:
            return await smart_print(ctx, 'The quote with id **%s**` does not exist',  # noqa
                                     data=[id])

        quote = quotes[0]

        embed = discord.Embed(
            title=f"{quote[2]}'s Quote",
            color=discord.Colour.dark_teal(),
            description=quote[4]
            )
        await ctx.send(embed=embed)

    async def get_all_guild_quotes(self, ctx):
        """
        Method for retreving all the quotes in a guild.
        """
        # First, we need to get all the users
        all_quotes = await self.db.get_guild_quotes(ctx.guild.id)

        if len(all_quotes) == 0:
            return await smart_print(ctx, 'There are currently **0** quotes.')

        quotes = []
        for q in all_quotes:
            quotes.append([f'{q[2]} - {q[0]}', q[4]])

        embed = self.em.CreateEmbed(
            title='All Quotes',
            description=f'There is a total of **{len(quotes)}** quotes',
            color=discord.Colour.dark_teal(),
            inline=False
            )
        embed.add_items(quotes)
        await self.em.send(ctx, embed)

    async def on_emote_update(self, reaction, user):
        """
        Method called when an user reacts to a message.  This handles
        the `multi-page` embeds.
        """
        # Get the embedable
        embedable = await self.em.check(reaction.message.id,
                                        reaction.emoji)
        # Does it exist?
        if embedable:
            # Remove the user interaction
            await reaction.remove(user)
            await reaction.message.edit(embed=embedable)
