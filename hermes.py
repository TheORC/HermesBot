# @Date: 07/03/2021
# @author: Oliver Clarke
from dotenv import load_dotenv
from src import HermesClient

import os


def Main():

    # Load Discord variables
    load_dotenv()
    token = os.getenv('DISCORD_TOKEN')

    # Luanch Discord bot
    client = HermesClient(command_prefix=".")
    client.run(token)


if __name__ == "__main__":
    Main()
