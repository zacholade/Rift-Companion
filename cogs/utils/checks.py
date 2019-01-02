from discord.ext import commands

from .errors import (
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

def cog_is_ready(cog=None):
    """
    Checks to see if the cog is ready to run.
    If a cog name is not provided, ctx.cog is used.
    """
    async def predicate(ctx):
        cog = ctx.bot.get_cog(cog) if cog else ctx.cog
        if not cog.is_ready:
            raise CogNotReady(ctx)
        return True
    
    return commands.check(predicate)