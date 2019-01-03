from . import BaseCog


class RawDataManager(BaseCog):
    def __init__(self, bot):
        super().__init__(bot)

    async def start(self):
        # download assets



def setup(bot):
    n = RawDataManager(bot)
    bot.add_cog(n)
