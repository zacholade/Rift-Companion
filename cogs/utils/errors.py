from discord.ext import commands


class NoConnectionFound(commands.errors.CommandError):
    """
    An error which is raised when a certain connection is required
    however cannot be found in the user's connections.
    """
    pass