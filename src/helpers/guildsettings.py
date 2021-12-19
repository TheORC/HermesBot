from .databasemanager import DatabaseManager


class GuildSettings:

    def __init__(self, guildid):

        self.guildid = guildid

        # Define default guild settings
        self._svolume = .05
        self._qvolume = 0.2
        self._playlist = None
        self.db_manager = DatabaseManager()

        # self._load_settings()

    def _load_settings(self):

        results = self.db_manager.get_guild_settings(self.guildid)

        if len(results) > 0:
            results = results[0]
            self._svolume = results[1]
            self._qvolume = results[2]
            self._playlist = results[3]

        self._save_settings()

    def _save_settings(self):
        self.db_manager.save_guild_settings(self.guildid, self._svolume,
                                            self._qvolume, self._playlist)

    def get_music_volume(self):
        return self._svolume

    def get_quote_volume(self):
        return self._qvolume

    def get_playlist(self):
        return self._playlist

    def save_music_volume(self, volume):
        self._svolume = volume
        self._save_settings()

    def save_quote_volume(self, volume):
        self._qvolume = volume
        self._save_settings()

    def save_playlist(self, playlist):
        self._playlist = playlist
        self._save_settings()
