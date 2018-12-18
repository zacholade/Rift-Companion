from discord.ext import commands

from ..ErrorHandler import (
    NoConnectionFound
)

def has_connection(connection):
    """
    Checks to see if the user has authorized the bot to see a connection
    required for the command to be invoked.
    Raises NoConnectionFound error if this is false and handled in the
    ErrorHandler class.
    """
    def predicate(ctx):
        if ctx.bot.database.get_connection(ctx.author.id, connection) is None:
            raise NoConnectionFound(connection)
        return True

    return commands.check(predicate)

