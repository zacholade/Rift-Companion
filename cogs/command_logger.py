import sqlite3
import datetime

class CommandLogger(object):
    def __init__(self, bot):
        self.bot = bot
        self.connection = sqlite3.connect('data/commands.db')
        self.cursor = self.connection.cursor()

        self.cursor.execute("""SELECT name FROM sqlite_master WHERE type='table' AND name='commands'""")
        row = self.cursor.fetchone()
        if not row:
            self.create_tables()

            with self.connection:
                self.cursor.execute("""INSERT INTO schema_history VALUES (?,?)""", (1, datetime.datetime.now(),))

    def create_tables(self):
        with self.connection:
            self.cursor.execute("""CREATE TABLE IF NOT EXISTS commands (
                qualified_name TEXT PRIMARY KEY NOT NULL,
                total_invokes INTEGER NOT NULL DEFAULT 0
            )""")

            self.cursor.execute("""CREATE TABLE IF NOT EXISTS schema_history (
                schema_version UNSIGNED INTEGER PRIMARY KEY NOT NULL,
                ts timestamp
            )""")

    async def on_command(self, ctx):
        name ctx.command.qualified_name
        with self.connection:
            self.cursor.execute("SELECT * FROM commands WHERE qualified_name=?",(name,))
            row = self.cursor.fetchone()
            if not row:
                self.cursor.execute("""INSERT INTO commands VALUES (?,?)""",(name,0))
            else:
                self.cursor.execute("""UPDATE commands 
                                    SET total_invokes = total_invokes + 1 
                                    WHERE qualified_name=?""", (name,))

def setup(bot):
    n = CommandLogger(bot)
    bot.add_cog(n)