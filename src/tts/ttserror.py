class TTSError(Exception):

    def __init__(self, error):
        self.error = error
        self.message = 'Error occured in the TTS job worker.'
        super().__init__(self.message)

    def __str__(self):
        return f'{self.message} -> {self.error}'


class TTSNetworkError(TTSError):
    def __str__(self):
        return f'TTSNetworkError: {self.message} -> {self.error}'


class TTSFileError(TTSError):
    def __str__(self):
        return f'TTSFileError: {self.message} -> {self.error}'


class TTSDatabaseError(TTSError):
    def __str__(self):
        return f'TTSDatabaseError: {self.message} -> {self.error}'
