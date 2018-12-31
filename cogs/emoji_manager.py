import logging

from .utils.utils import calc_checksum

logger = logging.getLogger('root')


class EmojiManager(object):
    def __init__(self, bot):
        self.bot = bot
        self._emoji_guild_pool = None
        self.bot.loop.create_task(self.start())

    async def start(self):
        await self.bot.wait_until_ready()
        emoji_guild_pool = []
        for guild_id in self.bot.config.discord_emoji_pool_guild_ids:
            guild = self.bot.get_guild(guild_id)
            if guild:
                emoji_guild_pool.append(guild)
            else:
                logger.warn('guild with id: {} in discord_emoji_pool_guild_ids was not found'.format(guild_id))
        self._emoji_guild_pool = emoji_guild_pool

    





def setup(bot):
    n = EmojiManager(bot)
    bot.add_cog(n)