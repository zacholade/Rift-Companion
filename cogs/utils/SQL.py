import datetime
import sqlite3

class ConnectionsDatabase():
    def __init__(self, db):
        self.connection = sqlite3.connect(db)
        self.cursor = self.connection.cursor()
        
        self.cursor.execute("""SELECT name FROM sqlite_master WHERE type='table' AND name='connections'""")
        row = self.cursor.fetchone()
        if not row:
            self.create_tables()

            with self.connection:
                self.cursor.execute("""INSERT INTO schema_history VALUES (?,?)""", (1, datetime.datetime.now(),))

    def create_tables(self):
        # TODO add functionality to be able to pass table_name as a param as well as args
        with self.connection:
            self.cursor.execute(
                """CREATE TABLE IF NOT EXISTS schema_history (
                schema_version UNSIGNED INTEGER PRIMARY KEY NOT NULL,
                ts timestamp
            )""")

        with self.connection:
            self.cursor.execute(
                """CREATE TABLE IF NOT EXISTS connections (
                user_id UNSIGNED INTEGER NOT NULL,
                type TEXT,
                verified BOOLEAN NOT NULL,
                name TEXT,
                show_activity BOOLEAN NOT NULL,
                friend_sync BOOLEAN NOT NULL,
                id TEXT,
                visibility BOOLEAN NOT NULL,
                PRIMARY KEY (user_id, type)
            )""")

    def add_connection(self, user_id, c):
        self.cursor.execute("""SELECT * FROM connections WHERE user_id=? AND type=?""", (user_id, c['type']))
        row = self.cursor.fetchone()
        print(row)
        if not row: # Add new connection
            print('new connection')
            with self.connection:
                self.cursor.execute(
                    """INSERT INTO connections VALUES (?,?,?,?,?,?,?,?)""", (
                        user_id,
                        c['type'],
                        c['verified'],
                        c['name'],
                        c['show_activity'],
                        c['friend_sync'],
                        c['id'],
                        c['visibility']
                    )
                )

        else: # Connection for this user_id and type already exist. Update it with new info.
            print('updating connection')
            with self.connection:
                self.cursor.execute(
                    """UPDATE connections SET verified=?, name=?, show_activity=?, friend_sync=?, id=?, visibility=? WHERE type=? AND user_id=?""",(
                        c['verified'],
                        c['name'],
                        c['show_activity'],
                        c['friend_sync'],
                        c['id'],
                        c['visibility'],
                        c['type'],
                        user_id
                    )
                )

    # TODO Add methods to get specific data.
