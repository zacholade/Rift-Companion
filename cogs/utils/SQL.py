import datetime
import sqlite3
import atexit

class UsersDatabase():
    """
    Used for handling creating/adding/removing a user's third party discord
    connections in a database aquired from discord's api.
    """
    def __init__(self, db):
        self.connection = sqlite3.connect(db)
        self.cursor = self.connection.cursor()
        atexit.register(UsersDatabase._shutdownhook, cursor=self.cursor, connection=self.connection)
        
        self.cursor.execute("""SELECT name FROM sqlite_master WHERE type='table' AND name='connections'""")
        row = self.cursor.fetchone()
        if not row:
            print('oof')
            self.create_tables()

            with self.connection:
                self.cursor.execute("""INSERT INTO schema_history VALUES (?,?)""", (1, datetime.datetime.now(),))

    @staticmethod
    def _shutdownhook(cursor, connection):
        # cant use self here
        cursor.close()
        connection.close()

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

        with self.connection:
            self.cursor.execute(
                """CREATE TABLE IF NOT EXISTS opt_in (
                    user_id UNSUGNED INTEGER PRIMARY KEY NOT NULL,
                    pregame BOOLEAN NOT NULL,
                    postgame BOOLEAN NOT NULL
                )""")
        return

    def _get_current_database_schema_version(self):
        self.cursor.execute("""SELECT * FROM schema_history ORDER BY schema_version DESC LIMIT 1""")
        return self.cursor.fetchone()

    def add_connection(self, user_id, c):
        self.cursor.execute("""SELECT * FROM connections WHERE user_id=? AND type=?""", (user_id, c['type']))
        row = self.cursor.fetchone()
        if not row: # Add new connection
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
                    ))

    def get_connection(self, user_id, c_type):
        self.cursor.execute("""SELECT * FROM connections WHERE user_id=? AND type=?""", (user_id, c_type))
        row = self.cursor.fetchone()
        row_dict = dict()
        if row:
            row_dict = dict(zip([c[0] for c in self.cursor.description], row))
        return row_dict

    def get_opt_in(self, user_id):
        self.cursor.execute("""SELECT * FROM opt_in WHERE user_id=?""", (user_id,))
        row = self.cursor.fetchone()
        if row:
            # (pregame, postgame)
            return (bool(row[1]), bool(row[2]))
        return (False, False)

    def add_opt_in(self, user_id, pregame=False, postgame=False):
        self.cursor.execute("""SELECT * FROM opt_in WHERE user_id=?""", (user_id,))
        row = self.cursor.fetchone()
        if not row:
            with self.connection:
                self.cursor.execute("""INSERT INTO opt_in VALUES (?,?,?)""", (user_id, pregame, postgame))
        else:
            with self.connection:
                self.cursor.execute("""UPDATE opt_in SET pregame=?, postgame=? WHERE user_id=?""",(
                    pregame,
                    postgame,
                    user_id
                ))


