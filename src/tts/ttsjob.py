from .ttserror import TTSNetworkError, TTSFileError, TTSDatabaseError
from gtts import gTTS


class TTSJob():
    """
    This class handles the creation of tts objects.
    """

    def __init__(self, quoteid, text, filename):
        self.id = quoteid
        self.text = text
        self.filename = filename
        self.full_name = f'tts_files/{self.filename}.mp3'

    def __str__(self):
        return f'Job: {self.id}-{self.filename} -> "{self.text}"'

    def _create_engine(self):
        """
        Create the TTS object
        """
        try:
            tts = gTTS(self.text, lang='en', tld='com')
        except Exception as e:
            raise TTSNetworkError(e)
        return tts

    def _save_file(self, tts):
        """
        This method saves a TTS object as a file
        """
        try:
            tts.save(self.full_name)
        except Exception as e:
            raise TTSFileError(e)

    async def _store_in_database(self, database):

        await database.add_tts_file(self.id, self.filename)
        try:
            pass
        except Exception as e:
            raise TTSDatabaseError(e)

    async def task(self, database):

        # Create the engine
        tts = self._create_engine()

        # Store the file
        self._save_file(tts)

        # Store the file in the database
        await self._store_in_database(database)
