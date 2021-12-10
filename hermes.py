'''
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
'''
from discord import Intents
from dotenv import load_dotenv


import src
import os


def Main():

    # Load env variables
    load_dotenv()
    token = os.getenv('DISCORD_TOKEN')

    # Create the client
    bot = src.HermesClient(command_prefix='.', intents=Intents.default())

    # Load our cogs
    bot.register_cogs()

    # Start the bot
    bot.run(token)


if __name__ == "__main__":
    Main()
