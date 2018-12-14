class Champion(object):
    def __init__(self, bot):
        self.bot = bot

    # TODO


def setup(bot):
    n = Champion(bot)
    bot.add_cog(n)