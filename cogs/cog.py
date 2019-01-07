from bot import LoggingMixin, ConfigMixin

import asyncio


class BaseCog(LoggingMixin, ConfigMixin):
    def __init__(self, bot):
        self.bot = bot
        self._is_ready = asyncio.Event(loop=self.bot.loop)
        self.bot.loop.create_task(self.__start())

    @property
    def is_ready(self):
        """
        Returns True is the cog has finished starting up and is ready.
        """
        return self._is_ready.is_set()

    def handle_ready(self):
        """
        Called when the cog has finished starting up. Sets is_ready to True.
        """
        self._is_ready.set()

    async def wait_until_ready(self):
        """
        This coroutine waits until the cog is all ready.
        """
        await self._is_ready.wait()

    async def close(self):
        """
        Marks the cog as not ready.
        """
        if not self.is_ready:
            return

        self._is_ready.clear()

    async def __start(self):
        """
        This method wraps the start function.
        It waits for the bot to be ready before calling the start logic
        and sets the cog as is_ready once completed
        """
        await self.bot.wait_until_ready()
        await self.start()
        self.handle_ready()

    async def start(self):
        """
        Overwrite this function in the child class.
        Include any initialization logic inside of it.
        """
        pass