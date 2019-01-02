import datetime

class CommandLogger(object):
    def __init__(self, bot):
        self.bot = bot
        self.bot.loop.create_task(self.init_tables())

    async def init_tables(self):
        await self.bot.wait_until_ready()
        async with self.bot.pool.acquire() as connection:
            await connection.execute("""CREATE TABLE IF NOT EXISTS commands (
                qualified_name TEXT PRIMARY KEY NOT NULL,
                total_invokes INTEGER NOT NULL DEFAULT 0
            )""")

    async def on_command(self, ctx):
        command_name = ctx.command.qualified_name
        async with self.bot.pool.acquire() as connection:
            await connection.execute("""INSERT INTO commands (qualified_name, total_invokes)
                                    VALUES ($1, $2)
                                    ON CONFLICT (qualified_name)
                                    DO UPDATE SET total_invokes=commands.total_invokes+1
                                    """, command_name, 0)


def setup(bot):
    n = CommandLogger(bot)
    bot.add_cog(n)