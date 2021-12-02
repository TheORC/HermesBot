# https://gist.github.com/Ristellise/ea025eb01e4542e0f91c7ecab9fb704f

import discord
from discord import Colour


class ChunkIterator:

    def __init__(self, chunk):
        self._chunk = chunk
        self._index = 0

    def __next__(self):
        if self._index < len(self._chunk.items):
            result = self._chunk.items[self._index]
            self._index += 1
            return result
        raise StopIteration


class Chunk:

    def __init__(self, items: list):
        self.items = items

    def __iter__(self):
        return ChunkIterator(self)

    @classmethod
    def GetChunkcs(chunk, items, chunk_size):

        chunks = []

        for i in range(0, len(items), chunk_size):
            temp_chunk = Chunk(items[i:i+chunk_size])
            chunks.append(temp_chunk)

        return chunks


class PageEmbedManager:

    def __init__(self, item_per_page=10):

        self._reactdefaults = ["◀", "⬅", "❎", "➡", "▶"]

        self.active_embeds = []  # {id=id, embed=embed}
        self.item_per_page = item_per_page

    def CreateEmbed(self,
                    title,
                    description=None,
                    footer=None,
                    inline=True,
                    color=Colour.dark_teal()):
        embed = MultiPageEmbed(title,
                               items_per_page=self.item_per_page,
                               description=description,
                               footer=footer,
                               inline=inline,
                               color=color
                               )
        return embed

    async def check(self, messageid, emoji):
        for item in self.active_embeds:
            if item['id'] == messageid:

                embed = item['embed']

                if emoji == embed.emojis[0]:
                    print('First page.')
                    embed.first_page()
                elif emoji == embed.emojis[1]:
                    print('Previouse page.')
                    embed.prev_page()
                elif emoji == embed.emojis[2]:
                    print('Not deleting yet.')
                    pass  # delete
                elif emoji == embed.emojis[3]:
                    print('Next page.')
                    embed.next_page()
                elif emoji == embed.emojis[4]:
                    print('Last page.')
                    embed.last_page()
                return embed
        return False

    async def send(self, ctx, embed):
        msg = await ctx.send(embed=embed)
        self.active_embeds.append(
            {'id': msg.id,
             'message': msg,
             'embed': embed})
        await self.add_emotes(msg)

    async def add_emotes(self, message):
        for i in range(0, len(self._reactdefaults)):
            await message.add_reaction(self._reactdefaults[i])


class MultiPageEmbed (discord.Embed):

    def __init__(self, title, items_per_page=10, description=None,
                 footer=None,
                 inline=True,
                 color=Colour.dark_teal()):
        super().__init__()

        self.title = title
        self.description = description
        self.inline = inline
        self.color = color
        self.emojis = ["◀", "⬅", "❎", "➡", "▶"]

        self.items_per_page = items_per_page
        self.listitems = None

        self.page = 0
        self.maxpages = None
        self.chunked = []
        self.embed_page = None
        self.current_chunck = None

    def _init_pages(self):
        self.chunked = Chunk.GetChunkcs(self.listitems, self.items_per_page)
        self.maxpages = len(self.chunked) - 1

    def add_items(self, items: list):
        self.listitems = items
        self._init_pages()
        self.set_chunk()

    def set_chunk(self):
        self.current_chunck = self.chunked[self.page]

        self.clear_fields()

        for x in self.current_chunck:
            self.add_field(name=x[0], value=x[1], inline=self.inline)

        self.set_footer(text=f'Page {self.page+1} of {self.maxpages+1}')

    def next_page(self):
        if self.page == self.maxpages:
            pass
        else:
            self.page += 1
            self.set_chunk()

    def prev_page(self):
        if self.page == 0:
            pass
        else:
            self.page -= 1
            self.set_chunk()

    def first_page(self):
        self.page = 0
        self.set_chunk()

    def last_page(self):
        self.page = self.maxpages
        self.set_chunk()
