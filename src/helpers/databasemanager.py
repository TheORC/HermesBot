from mysql.connector.errors import ProgrammingError, InterfaceError
from dotenv import load_dotenv

import mysql.connector
import os


class DatabaseManager:

    def __init__(self, host=None, dbname=None, port=None):

        self.port = port
        self._import_login_details(host, dbname)

    def __del__(self):
        self._disconnect()

    def _import_login_details(self, host, dbname):

        load_dotenv()

        self.host = host
        self.dbName = dbname

        if host is None:
            self.host = os.getenv('DB_HOST')

        if dbname is None:
            self.dbName = os.getenv('DB_NAME')

        self.user = os.getenv('DB_USER')
        self.passw = os.getenv('DB_PASS')

    def _disconnect(self):

        try:
            self.conn.commit()  # Save changes
        except Exception:
            pass

        try:
            self.cursor.close()
            self.conn.close()
        except Exception:
            pass

    def _connect(self):

        self.conn = mysql.connector.connect(
            user=self.user,
            password=self.passw,
            host=self.host,
            database=self.dbName,
            autocommit=True)

        try:
            self.cursor = self.conn.cursor()
            print(f'Connected to database: {self.dbName}')

        except ProgrammingError as e:
            print(f'Database Error: {e}')

    def _sql_execute(self, query, data=None):
        self._connect()
        self.cursor.execute(query, data)

        try:
            results = self.cursor.fetchall()
        except InterfaceError:
            results = self.cursor.lastrowid

        self._disconnect()
        return results

    def get_guild_settings(self, guildid):
        sql = 'SELECT * FROM guild_settings WHERE idguild=%s'
        data = (guildid,)
        return self._sql_execute(sql, data=data)

    def save_guild_settings(self, guildid, mvolume, qvolume, playlist):
        sql = 'REPLACE INTO guild_settings (idguild, volumem, volumeq, playlist) VALUES (%s, %s, %s, %s)'  # noqa
        data = (guildid, mvolume, qvolume, playlist,)
        self._sql_execute(sql, data=data)

    def get_users(self, guildid):
        sql = 'SELECT * FROM users WHERE idguild=%s'
        data = (guildid,)
        return self._sql_execute(sql, data=data)

    def get_user_quote(self, guildid, name):
        sql = 'SELECT * FROM user_quotes WHERE username=%s AND idguild=%s ORDER BY idquote'  # noqa
        data = (name, guildid)
        return self._sql_execute(sql, data=data)

    def get_id_quote(self, guildid, id):
        sql = 'SELECT * FROM quotes WHERE idquote=%s AND idguild=%s'  # noqa
        data = (id, guildid)
        return self._sql_execute(sql, data=data)

    def add_user(self, guildid, name):
        sql = 'INSERT INTO users (idguild, username) VALUES (%s, %s)'
        data = (guildid, name)
        return self._sql_execute(sql, data)

    def remove_user(self, guildid, userid):
        sql_update = 'UPDATE quotes SET iduser=-1 WHERE idguild=%s AND iduser=%s'  # noqa
        sql_delete = 'DELETE FROM users WHERE idguild=%s AND iduser=%s'  # noqa
        data = (guildid, userid)

        self._sql_execute(sql_update, data)
        self._sql_execute(sql_delete, data)

    def add_user_quote(self, userid, guildid, userquote):
        sql = 'INSERT INTO quotes (iduser, idguild, quote_data, quote_date) VALUES (%s, %s, %s, %s)'  # noqa
        data = (userid, guildid, userquote, '2016-05-26')
        return self._sql_execute(sql, data)

    def remove_quote(self, guildid, quoteid):
        sql_delete = 'DELETE FROM quotes WHERE idguild=%s AND idquote=%s'  # noqa
        data = (guildid, quoteid)
        self._sql_execute(sql_delete, data)

    def get_missing_tts(self, guildid):
        sql = 'SELECT * FROM quotes WHERE quote_tts IS NULL AND idguild=%s'
        data = (guildid,)
        return self._sql_execute(sql, data=data)

    def get_all_quotes(self, guildid):
        sql = 'SELECT * FROM quotes WHERE idguild=%s'
        data = (guildid,)
        return self._sql_execute(sql, data=data)

    def get_number_quotes(self, guildid):
        sql = 'SELECT COUNT(*) from quotes WHERE idguild=%s'
        data = (guildid,)
        return self._sql_execute(sql, data=data)[0][0]

    def get_quote_tts(self, quoteid):
        sql = 'SELECT * FROM quotes WHERE idquote=%s'
        data = (quoteid,)
        return self._sql_execute(sql, data=data)

    def add_tts_to_quote(self, quoteid, ttsname):
        sql = 'UPDATE quotes SET quote_tts=%s WHERE idquote=%s'
        data = (ttsname, quoteid)
        self._sql_execute(sql, data=data)
