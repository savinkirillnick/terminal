import sqlite3
import json
from contextlib import closing


class DB:

    @staticmethod
    def query(db_name, query_get, query_post=()):
        with closing(sqlite3.connect(db_name)) as conn:  # auto-closes
            with conn:  # auto-commits
                with closing(conn.cursor()) as cursor:  # auto-closes
                    if query_post:
                        cursor.execute(query_get, query_post)
                    else:
                        cursor.execute(query_get)
                    return cursor.fetchall()

    def __init__(self, app):
        """Класс работы с базой данных SQLite для хранения настроек.
        """
        self.query('settings.db',
                   'CREATE TABLE IF NOT EXISTS init_settings (id INT PRIMARY KEY, shared_key VARCHAR(16))')
        self.query('settings.db',
                   'CREATE TABLE IF NOT EXISTS bot_settings (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, set_num VARCHAR(16), set_desc TEXT)')
        self.query('settings.db',
                   'CREATE TABLE IF NOT EXISTS alarm_settings (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, exchange TEXT, pair TEXT, alarm_desc TEXT)')

        row = self.query('settings.db', 'SELECT * FROM init_settings')
        if not row:
            self.query('settings.db', 'INSERT INTO init_settings (id, shared_key) VALUES (1, "demo")')
        self.app = app

    def save_key(self, shared_key):
        """Сохранение ключа.
        """
        if self.app.user.activation.check():
            self.query('settings.db', 'UPDATE init_settings SET shared_key=? WHERE id=?', (shared_key, 1))
            return 0

    def load_key(self):
        """Загрузка ключа.
        """
        row = self.query('settings.db', 'SELECT * FROM init_settings')
        return row[0][1]

    def get_settings_list(self):
        """Получение списка сохраненных настроек.
        """
        if self.app.user.activation.check():
            row = self.query('settings.db', 'SELECT * FROM bot_settings')
            return sorted([row[i][1] for i in range(len(row))]) if row != [] else list()

    def del_bot_settings(self, num):
        """удаление сета настроек.
        """
        if self.app.user.activation.check():
            self.query('settings.db', 'DELETE FROM bot_settings WHERE set_num = ?', (num,))
            return 0

    def save_bot_settings(self, num, data):
        """Сохранение сета настроек.
        """
        if self.app.user.activation.check():
            data_json = json.dumps(data)
            row = self.query('settings.db', 'SELECT * FROM bot_settings WHERE set_num=?', (num,))
            if row:
                self.query('settings.db', 'UPDATE bot_settings SET set_desc=? WHERE set_num=?', (data_json, num))
            else:
                self.query('settings.db', 'INSERT INTO bot_settings (id, set_num, set_desc) VALUES (null, ?, ?)', (num, data_json))
            return 0

    def load_bot_settings(self, num):
        """Загрузка сета настроек.
        """
        if self.app.user.activation.check():
            row = self.query('settings.db', 'SELECT * FROM bot_settings WHERE set_num = ?', (num,))
            return json.loads(row[0][2]) if row != [] else dict()
