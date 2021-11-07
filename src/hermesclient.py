# -*- coding: utf-8 -*-
"""
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
"""

from discord.ext import commands
import discord
import os


class HermesClient(commands.Bot):
    """
    Discord bot controller.

    This class is responsible for loading required bot cogs.
    """

    async def on_ready(self):
        """Called when the bot connects."""
        await self.change_presence(status=discord.Status.online,
                                   activity=discord.Game("Hermes Bot"))
        self._register_cogs()
        print("Bot is ready!")

    def _register_cogs(self):
        """Register the discord bot cogs"""
        for file in os.listdir('./src/cogs'):
            if file.endswith(".py"):
                extension = file[:-3]
                try:
                    self.load_extension(f"src.cogs.{extension}")
                    print(f"Loaded extension '{extension}'")
                except Exception as e:
                    exception = f"{type(e).__name__}: {e}"
                    print(f"Failed to load extension {extension}\n{exception}")  # noqa
