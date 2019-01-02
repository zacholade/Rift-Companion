from discord.ext import commands

from ..error_handler import (
    NoConnectionFound
)

def user_has_connection(connection):
    """
    Checks to see if the user has authorized the bot to see a connection
    required for the command to be invoked via oauth2.
    Raises NoConnectionFound error if this is false and handled in the
    ErrorHandler class.
    """
    async def predicate(ctx):
        if not await ctx.bot.database.get_connection(ctx.author.id, connection):
            raise NoConnectionFound(connection)
        return True

    return commands.check(predicate)
