import youtube_dl
from enum import Enum


class State(Enum):
    RUNNING = 1
    STOPPED = 2


class DownloadManager:
    def __init__(self):

        ydl_opts = {
            'format': 'bestaudio/best',
            'noplaylist': True,
            'continue_dl': True,
            'progress_hooks': [self.progress_hook],
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192', }]
        }

        self.url_list = []        # List of current
        self.current_download_url = ""  # Stores the current download
        self.state = State.STOPPED
        self.youtube_dl_manager = youtube_dl.YoutubeDL(ydl_opts)

    def queue_song(self, url):
        self.url_list.append(url)
        if(self.state == State.STOPPED):
            self.start_download_process()

    def start_download_process(self):
        self.state = State.RUNNING

        try:
            with self.youtube_dl_manager as youtube_dl_manager:
                youtube_dl_manager.cache.remove()
                self.current_download_url = self.url_list.pop()
                youtube_dl_manager.download([self.current_download_url])
        except Exception as e:
            print(e)

    def continue_download_process(self):
        with self.youtube_dl_manager as youtube_dl_manager:
            self.current_download_url = self.url_list.pop()
            youtube_dl_manager.download([self.current_download_url])

    def progress_hook(self, response):
        if response["status"] == "finished":
            file_name = response["filename"]

            print("Downloaded " + file_name)

            # You can do something with self.current_download_url and file_name here
            self.onSongLoad(self.current_download_url)

            if len(self.url_list) != 0:
                self.continue_download_process()
            else:
                self.currently_downloading = False
                self.state = State.STOPPED
                self.state = State.STOPPED
