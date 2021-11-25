from gtts import gTTS
import os


class GTTSWorker:

    def __init__(self, save_directory='temp', lang='en', tld='com.au'):
        self.lang = lang
        self.tld = tld

        self.save_directory = save_directory

        if(os.path.isdir(self.save_directory) is False):
            os.mkdir(self.save_directory)

    def convert_text(self, tts_data, cb=None):

        tts_data['error'] = False
        filepath = f'{self.save_directory}/{tts_data["filename"]}.mp3'

        # Check in case there was a database crash
        if(os.path.exists(filepath)):
            print('A TSS file already exists.  But we want it again?')
            cb(tts_data)
            return

        # Create the engine
        try:
            tts = gTTS(tts_data['text'], lang=self.lang, tld=self.tld)
        except Exception as e:
            tts_data['error'] = e

        # Save the TTS file
        try:
            tts.save(filepath)
        except Exception as e:
            tts_data['error'] = e

        # Call our callback
        if(cb is not None):
            cb(tts_data)
