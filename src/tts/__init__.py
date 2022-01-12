from .ttsthread import TTSThread
from .ttsjob import TTSJob
from .ttserror import (TTSError,
                       TTSNetworkError,
                       TTSFileError,
                       TTSDatabaseError)

_TTS_HOLDER = {'tts': None}


def tts_init():
    if _TTS_HOLDER['tts'] is None:
        _TTS_HOLDER['tts'] = TTSThread()

    return _TTS_HOLDER['tts']


def shutdown_worker():
    if _TTS_HOLDER['tts'] is not None:
        _TTS_HOLDER['tts'].is_running = False


__all__ = [
    # Classes
    'TTSJob',
    'TTSError', 'TTSNetworkError',
    'TTSFileError', 'TTSDatabaseError',

    # Methods
    'tts_init', 'shutdown_worker'
]
