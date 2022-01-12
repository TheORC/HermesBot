class TTSError(Exception):

    def __init__(self, error):
        self.error = error
        self.message = 'Error occured in the TTS job worker.'
        super().__init__(self.message)

    def __str__(self):
        return f'{self.message} -> {self.error}'


class TTSNetworkError(TTSError):
    pass


class TTSFileError(TTSError):
    pass


class TTSDatabaseError(TTSError):
    pass
