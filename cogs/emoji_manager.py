from . import BaseCog


class EmojiManager(BaseCog):
    def __init__(self, bot):
        super().__init__(bot)
        self._emoji_guild_pool = None

    async def start(self):
        emoji_guild_pool = []
        for guild_id in self.config.discord_emoji_pool_guild_ids:
            guild = self.bot.get_guild(guild_id)
            if guild:
                emoji_guild_pool.append(guild)
            else:
                self.logger.warn('guild with id: {} in discord_emoji_pool_guild_ids was not found'.format(guild_id))
        self._emoji_guild_pool = emoji_guild_pool


def setup(bot):
    n = EmojiManager(bot)
    bot.add_cog(n)