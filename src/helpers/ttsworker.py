from ..utils import CustomQueue, GTTSWorker


class TTSWorker:

    def __init__(self, bot, filepath):
        self.bot = bot

        self.tts = GTTSWorker(save_directory=filepath)

        self.queue = CustomQueue()
        self.event_cb = None

        self.tts_worker = self.bot.loop.create_task(self._tts_loop())

    def __del__(self):
        self.tts_worker.cancel()

    async def _tts_loop(self):

        await self.bot.wait_until_ready()

        while not self.bot.is_closed():
            tts_data = await self.queue.get()
            self.tts.convert_text(tts_data, cb=self.event_cb)

    def set_event_cb(self, cb):
        self.event_cb = cb
