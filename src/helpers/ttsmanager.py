from .databasemanager import DatabaseManager
from .ttsworker import TTSWorker


class TTSManager():

    def __init__(self, bot, filepath='temp'):
        self.bot = bot
        self.db_manager = DatabaseManager()

        self.ttsworker = TTSWorker(bot, filepath)
        self.ttsworker.set_event_cb(self._tts_callback)

    def _update_database(self):
        pass

    def _tts_callback(self, results):
        if results['error'] is False:
            print(results)
            self.db_manager.add_tts_to_quote(
                results['id'], results['filename'])
        else:
            print(f'Error creating TSS: {results}')

    # Add tts message to be proccessed
    async def quote_to_tts(self, quoteid, quote, filename):
        await self.ttsworker.queue.put({'id': quoteid,
                                        'text': quote,
                                        'filename': filename})
