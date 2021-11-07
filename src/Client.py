"""

Class for controlling Hermes Discord Bot.

@author: Oliver Clarke
@date: 10/04/2021

"""
import discord
import os
from discord.ext import commands


class HermesClient(commands.Bot):
    """Short summary."""

    async def on_ready(self):
        """Listen for bot connection."""
        await self.change_presence(status=discord.Status.online, activity=discord.Game("Hermes Bot"))
        self._register_cogs()
        print("Bot is ready!")

    def _register_cogs(self):
        for file in os.listdir('./src/cogs'):
            if file.endswith(".py"):
                extension = file[:-3]
                try:
                    self.load_extension(f"src.cogs.{extension}")
                    print(f"Loaded extension '{extension}'")
                except Exception as e:
                    exception = f"{type(e).__name__}: {e}"
                    print(f"Failed to load extension {extension}\n{exception}")
