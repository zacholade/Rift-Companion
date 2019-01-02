from . import BaseCog

import datetime

class SqlManager(BaseCog):
    def __init__(self, bot):
        super().__init__(bot)
        self.bot.database = self

    async def start(self):
        async with self.bot.pool.acquire() as connection:
            async with connection.transaction():
                await connection.execute(
                    """CREATE TABLE IF NOT EXISTS users (
                        user_id BIGINT PRIMARY KEY NOT NULL,
                        opted_in BOOLEAN NOT NULL DEFAULT FALSE
                    )""")

                await connection.execute(
                    """CREATE TABLE IF NOT EXISTS connections (
                        user_id BIGINT NOT NULL,
                        type TEXT,
                        name TEXT,
                        id TEXT,
                        PRIMARY KEY (user_id, type)
                    )""")

                await connection.execute(
                    """CREATE TABLE IF NOT EXISTS oauth_tokens (
                        user_id BIGINT PRIMARY KEY NOT NULL,
                        access_token TEXT NOT NULL,
                        token_type TEXT NOT NULL,
                        expires_in timestamp,
                        refresh_token TEXT NOT NULL,
                        scope TEXT NOT NULL
                    )""")

    async def _create_table(self, query, *args):
        pass # TODO

    async def execute(self, query, *args):
        async with self.bot.pool.acquire() as connection:
            await connection.execute(query, *args)
    
    async def fetchrow(self, query, *args):
        async with self.bot.pool.acquire() as connection:
            return await connection.fetchrow(query, *args)
    
    async def fetchall(self, query, *args):
        async with self.bot.pool.acquire() as connetion:
            return await connection.fetch(query, *args)

    async def add_connection(self, user_id, c):
        query = """INSERT INTO connections (user_id, type, name, id)
                   VALUES ($1,$2,$3,$4)
                   ON CONFLICT (user_id, type) DO UPDATE SET name=$3, id=$4"""
        args = (user_id, c['type'], c['name'], c['id'])
        return await self.execute(query, *args)

    async def get_connection(self, user_id, c_type):
        query = "SELECT * FROM connections WHERE user_id=$1 AND type=$2"
        args = (user_id, c_type)
        return await self.fetchrow(query, *args) # TODO Transform data to object

    async def add_oauth_token(self, user_id, token):
        query = """INSERT INTO oauth_tokens (user_id, access_token, token_type, expires_in, refresh_token, scope)
                   VALUES ($1,$2,$3,$4,$5,$6) ON CONFLICT (user_id) DO UPDATE
                   SET access_token=$2, token_type=$3, expires_in=$4, refresh_token=$5, scope=$6"""
        expires_at = datetime.datetime.now() + datetime.timedelta(seconds=token['expires_in'])
        args = (user_id, token['access_token'], token['token_type'], expires_at, token['refresh_token'], token['scope'])
        await self.execute(query, *args)

    async def get_oauth_token(self, user_id):
        query = "SELECT * FROM oauth_tokens WHERE user_id=$1"
        args = (user_id)
        row = await self.fetchrow(query, args)
        if row:
            return {'access_token': row[1], 'token_type': row[2], 'expires_in': row[3],
                    'refresh_token': row[4], 'scope': row[5]}
        return None

    async def set_opt_in(self, user_id, opted_in=True):
        query = """INSERT INTO users (user_id, opted_in)
                   VALUES ($1,$2) ON CONFLICT (user_id) DO UPDATE
                   SET opted_in=$2"""
        args = (user_id, opted_in)
        await self.execute(query, *args)

    async def get_opt_in(self, user_id):
        query = "SELECT * FROM users WHERE user_id=?"
        args = (user_id)
        return await self.fetchrow(query, args)


def setup(bot):
    n = SqlManager(bot)
    bot.add_cog(n)