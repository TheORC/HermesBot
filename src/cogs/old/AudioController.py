from discord.ext import commands
# REEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE
from .helpers import AudioManager


class AudioController(commands.Cog):

    def __init__(self, bot):
        """Initialize important information."""
        self.bot = bot
        self.audio_manager = AudioManager()

    @commands.command(
        name="play",
        help="- .play <url:string> : Play a song from the URL."
    )
    async def play_song(self, ctx, url):

        if url is None:
            await ctx.send('> Audio URL not specified.')
            return

        print(ctx.author.voice.channel)

        channel = ctx.author.voice.channel
        if(channel is None):
            await ctx.send('> Can not find audio channel to join.\n> Make sure you are in a voice channel when typing this command.')
            return

        # Connect to channel
        voice = await channel.connect()

        self.audio_manager.loadaudio(url)
        self.audio_manager.playaudio(voice)

        await ctx.send('Playing Song.\n >>> URL: {}'.format(url))

    @commands.command(
        name="stop",
        help="- .stop : Stop songs playing."
    )
    async def stop_song(self, ctx):
        self.audio_manager.stopaudio()
        await ctx.send('Stoping soungs.')


def setup(bot):
    """Short summary."""
    bot.add_cog(AudioController(bot))  # Fuck
