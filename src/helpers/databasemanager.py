from mysql.connector.errors import ProgrammingError
from dotenv import load_dotenv

import mysql.connector
import os


class DatabaseManager:

    def __init__(self, host, dbname, port=None):
        self.host = host
        self.dbName = dbname
        self.port = port
        self.user, self.passw = self._import_login_details()

    def __del__(self):
        try:
            self.cursor.close()
            self.conn.close()
        except Exception:
            pass

    def _import_login_details(self):
        load_dotenv()
        username = os.getenv('DB_USER')
        password = os.getenv('DB_PASS')
        return username, password

    def connect(self):

        self.conn = mysql.connector.connect(
            user=self.user,
            password=self.passw,
            host=self.host,
            database=self.dbName)

        try:
            self.cursor = self.conn.cursor()
            print('Connected to database: {}'.format(self.dbName))

        except ProgrammingError as e:
            print('Database Error: {}'.format(e))

    def _sql_get(self, query, data=None):

        if data is None:
            self.cursor.execute(query)
        else:
            self.cursor.execute(query, data)

        return self.cursor.fetchall()

    def _sql_insert(self, query, data):
        self.cursor.execute(query, data)
        self.conn.commit()
        return self.cursor.lastrowid

    def get_users(self, guildid):
        sql = 'SELECT * FROM users WHERE idguild = %s'
        data = (guildid,)
        return self._sql_get(sql, data=data)

    def get_user_quote(self, guildid, name):
        sql = 'SELECT * FROM user_quotes WHERE username=%s AND idguild=%s'  # noqa
        data = (name, guildid)
        return self._sql_get(sql, data=data)

    def get_id_quote(self, guildid, id):
        sql = 'SELECT * FROM user_quotes WHERE idquote=%s AND idguild=%s'  # noqa
        data = (id, guildid)
        return self._sql_get(sql, data=data)

    def add_user(self, guildid, name):
        sql = 'INSERT INTO users (idguild, username) VALUES (%s, %s)'
        data = (guildid, name)
        user = self._sql_insert(sql, data)
        return user

    def remove_user(self, guildid, userid):
        sql_update = 'UPDATE quotes SET iduser=-1 WHERE idguild=%s AND iduser=%s'  # noqa
        sql_delete = 'DELETE FROM users WHERE idguild=%s AND iduser=%s'  # noqa
        data = (guildid, userid)

        self.cursor.execute(sql_update, data)
        self.conn.commit()
        self.cursor.execute(sql_delete, data)
        self.conn.commit()

    def add_user_quote(self, userid, guildid, userquote):
        sql = 'INSERT INTO quotes (iduser, idguild, quote_data, quote_date) VALUES (%s, %s, %s, %s)'  # noqa
        data = (userid, guildid, userquote, '2016-05-26')
        return self._sql_insert(sql, data)

    def remove_quote(self, guildid, quoteid):
        sql_delete = 'DELETE FROM quotes WHERE idguild=%s AND idquote=%s'  # noqa
        data = (guildid, quoteid)
        self.cursor.execute(sql_delete, data)
        self.conn.commit()

    def get_missing_tts(self, guildid):
        sql = 'SELECT * FROM quotes WHERE quote_tts IS NULL AND idguild=%s'
        data = (guildid,)
        return self._sql_get(sql, data=data)

    def get_all_quotes(self, guildid):
        sql = 'SELECT * FROM quotes WHERE idguild=%s'
        data = (guildid,)
        return self._sql_get(sql, data=data)

    def get_number_quotes(self, guildid):
        sql = 'SELECT COUNT(*) from quotes WHERE idguild=%s'
        data = (guildid,)
        return self._sql_get(sql, data=data)[0][0]

    def get_quote_tts(self, quoteid):
        sql = 'SELECT * FROM quotes WHERE idquote=%s'
        data = (quoteid,)
        return self._sql_get(sql, data=data)

    def add_tts_to_quote(self, quoteid, ttsname):
        sql = 'UPDATE quotes SET quote_tts=%s WHERE idquote=%s'
        data = (ttsname, quoteid)
        self.cursor.execute(sql, data)
        self.conn.commit()
