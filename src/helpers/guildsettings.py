from ..database import hermes_database


class GuildSettings:

    def __init__(self, svolume=None, qvolume=None, playlist=None):

        # Define default guild settings
        self._svolume = .05 if not svolume else svolume
        self._qvolume = 0.2 if not qvolume else qvolume
        self._playlist = playlist

    @classmethod
    async def save_music_volume(self, guildid, volume):
        db = hermes_database()
        await db.save_song_volume(guildid, volume)

    @classmethod
    async def save_quote_volume(self, guildid, volume):
        db = hermes_database()
        await db.save_quote_volume(guildid, volume)

    @classmethod
    async def save_playlist(self, guildid, playlist):
        db = hermes_database()
        await db.save_playlist(guildid, playlist)

    def get_music_volume(self):
        return self._svolume

    def get_quote_volume(self):
        return self._qvolume

    def get_playlist(self):
        return self._playlist
