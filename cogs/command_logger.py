from . import BaseCog

import datetime


class CommandLogger(BaseCog):
    def __init__(self, bot):
        super().__init__(bot)

    async def start(self):
        async with self.bot.pool.acquire() as connection:
            await connection.execute("""CREATE TABLE IF NOT EXISTS commands (
                qualified_name TEXT PRIMARY KEY NOT NULL,
                total_invokes INTEGER NOT NULL DEFAULT 0
            )""")

    async def on_command(self, ctx):
        command_name = ctx.command.qualified_name
        await self.bot.database.execute("""INSERT INTO commands (qualified_name, total_invokes)
                                VALUES ($1, $2)
                                ON CONFLICT (qualified_name)
                                DO UPDATE SET total_invokes=commands.total_invokes+1
                                """, command_name, 0)


def setup(bot):
    n = CommandLogger(bot)
    bot.add_cog(n)