from dotenv import load_dotenv
from functools import partial

from mysql.connector import pooling
from mysql.connector.errors import InterfaceError
import os
import datetime


class DatabaseQuery:

    SELECT_GUILD_SETTINGS = 'SELECT * FROM guild_settings WHERE idguild=%s'
    SELECT_GUILD_USERS = 'SELECT * FROM users WHERE idguild=%s'

    SELECT_QUOTES_GUILD = 'SELECT * FROM user_quotes WHERE idguild=%s ORDER BY idquote'  # noqa
    SELECT_QUOTE_USER = 'SELECT * FROM user_quotes WHERE idguild=%s AND username=%s'  # noqa
    SELECT_QUOTE_ID = 'SELECT * FROM user_quotes WHERE idguild=%s AND idquote=%s'  # noqa

    SELECT_GUILD_TTS = 'SELECT idquote, file_name FROM quotes as q INNER JOIN tts_file_references as t ON q.idquote = t.quote_id WHERE q.idguild = %s'  # noqa
    SELECT_ID_TTS = 'SELECT * FROM tts_file_references WHERE quote_id=%s'

    SELECT_NULL_TTS = 'SELECT * FROM quotes WHERE quote_tts IS NULL AND idguild=%s'  # noqa
    SELECT_QUOTE_COUNT = 'SELECT COUNT(*) from quotes WHERE idguild=%s'


class DatabaseUpdate:

    REPLACE_GUILD_SETTINGS_SONG_VOLUME = 'INSERT INTO guild_settings (idguild, volumem, volumeq, playlist) VALUES(%s, %s, 1, "")    ON DUPLICATE KEY UPDATE idguild=%s, volumem=%s'  # noqa
    REPLACE_GUILD_SETTINGS_QUOTE_VOLUME = 'INSERT INTO guild_settings (idguild, volumem, volumeq, playlist) VALUES(%s, 0.05, %s, "") ON DUPLICATE KEY UPDATE idguild=%s, volumeq=%s'  # noqa
    REPLACE_GUILD_SETTINGS_PLAYLIST = 'INSERT INTO guild_settings (idguild, volumem, volumeq, playlist) VALUES(%s, 0.05, 1, %s)  ON DUPLICATE KEY UPDATE idguild=%s, playlist=%s'  # noqa

    INSERT_GUILD_USER = 'INSERT INTO users (idguild, username) VALUES (%s, %s)'
    INSERT_GUILD_QUOTE = 'INSERT INTO quotes (idguild, iduser, quote_data, quote_date) VALUES (%s, %s, %s, %s)'  # noqa
    INSERT_TTS_FILE = 'INSERT INTO tts_file_references (quote_id, file_name) VALUES (%s, %s)'  # noqa

    DELETE_GUILD_QUOTE = 'DELETE FROM quotes WHERE idguild=%s AND idquote=%s'  # noqa

    REMOVE_QUOTE_USER = 'UPDATE quotes SET iduser=-1 WHERE idguild=%s AND iduser=%s'  # noqa
    DELETE_GUILD_USER = 'DELETE FROM users WHERE idguild=%s AND iduser=%s'


class DatabaseManager:

    def __init__(self, loop):  # noqa

        # Load environment details
        load_dotenv()

        # Set connections details
        self.host = os.getenv('DB_HOST')
        self.dbName = os.getenv('DB_NAME')
        self.user = os.getenv('DB_USER')
        self.passw = os.getenv('DB_PASS')

        self.loop = loop

        # Create the connection pool
        self._create_pool()

    def _create_pool(self):

        # Database login details
        temp = {
            'host': self.host,
            'database': self.dbName,
            'user': self.user,
            'password': self.passw,
            'autocommit': True
        }

        # Create the pool
        self.pool = pooling.MySQLConnectionPool(pool_name='hermers_pool',  # noqa
                                                                pool_size=5,
                                                                **temp)

    def _get_connection(self):
        """
        Returns a connection from the connections
        pool.
        :return: `mysql.connection`
        """
        return self.pool.get_connection()

    def _perform_execute(self, cursor, query, data):
        """
        Performs an execute action on the database.
        """
        cursor.execute(query, data)

    # Async call to the database
    async def _execute(self, query, data=None):
        """
        Method called to perform an async fetch of information
        from the database.

        :return: `[(data), (data)]`
        """

        # Get a connection from the pool
        connection = await self.loop.run_in_executor(None, self._get_connection)  # noqa
        cursor = connection.cursor()

        # Perform the query to the database
        to_run = partial(self._perform_execute, cursor, query, data)
        await self.loop.run_in_executor(None, to_run)

        # Get values
        try:
            values = cursor.fetchall()
        except InterfaceError:
            values = cursor.lastrowid

        # Release the connection back to the pool
        cursor.close()
        connection.close()

        # Return the results
        return values

    async def get_guild_users(self, guildid):
        return await self._execute(
            DatabaseQuery.SELECT_GUILD_USERS,
            data=(guildid,)
        )

    async def add_guild_user(self, guildid, username):
        await self._execute(
            DatabaseUpdate.INSERT_GUILD_USER,
            data=(guildid, username,)
        )

    async def remove_guild_user(self, guildid, username):
        await self._execute(
            DatabaseUpdate.DELETE_GUILD_USER,
            data=(guildid, username,)
        )

    async def add_user_quote(self, guildid, userid, quote):
        """idguild, iduser, quote_data, quote_date"""

        now = datetime.datetime.utcnow()
        formated = now.strftime('%Y-%m-%d %H:%M:%S')

        return await self._execute(
            DatabaseUpdate.INSERT_GUILD_QUOTE,
            data=(guildid, userid, quote, formated,)
        )

    async def remove_user_quote(self, guildid, quoteid):
        await self._execute(
            DatabaseUpdate.DELETE_GUILD_QUOTE,
            data=(guildid, quoteid,)
        )

    async def add_tts_file(self, quoteid, filename):

        print(quoteid)
        print(filename)

        return await self._execute(
            DatabaseUpdate.INSERT_TTS_FILE,
            data=(quoteid, filename,)
        )

    async def get_user_quotes(self, guildid, username):
        return await self._execute(
            DatabaseQuery.SELECT_QUOTE_USER,
            data=(guildid, username,)
        )

    async def get_quote_from_id(self, guildid, quoteid):
        return await self._execute(
            DatabaseQuery.SELECT_QUOTE_ID,
            data=(guildid, quoteid,)
        )

    async def get_guild_quotes(self, guildid):
        return await self._execute(
            DatabaseQuery.SELECT_QUOTES_GUILD,
            data=(guildid,)
        )

    async def get_guild_tts(self, guildid):
        return await self._execute(
            DatabaseQuery.SELECT_GUILD_TTS,
            data=(guildid,)
        )

    async def get_id_tts(self, quoteid):
        return await self._execute(
            DatabaseQuery.SELECT_ID_TTS,
            data=(quoteid,)
        )

    async def get_guild_settings(self, guilid):
        return await self._execute(
            DatabaseQuery.SELECT_GUILD_SETTINGS,
            data=(guilid,)
        )

    async def save_song_volume(self, guildid, svol):
        """idguild, volumem, volumeq, playlist"""
        await self._execute(
            DatabaseUpdate.REPLACE_GUILD_SETTINGS_SONG_VOLUME,
            data=(guildid, svol, guildid, svol,)
        )

    async def save_quote_volume(self, guildid, qvol):
        """idguild, volumem, volumeq, playlist"""
        await self._execute(
            DatabaseUpdate.REPLACE_GUILD_SETTINGS_QUOTE_VOLUME,
            data=(guildid, qvol, guildid, qvol,)
        )

    async def save_playlist(self, guildid, playlist):
        """idguild, volumem, volumeq, playlist"""
        await self._execute(
            DatabaseUpdate.REPLACE_GUILD_SETTINGS_PLAYLIST,
            data=(guildid, playlist, guildid, playlist,)
        )
