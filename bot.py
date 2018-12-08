
# Normal Imports
import os
import aiohttp
import asyncio
import datetime
import importlib

# Dependencies
import discord
from discord.ext import commands
import cassiopeia as riot

# Local Imports
import config

# Logging
import logging
from logging.handlers import TimedRotatingFileHandler
import traceback

logger = logging.getLogger('root')
logging.basicConfig(format="[%(asctime)s %(levelname)-8s %(filename)-15s:%(lineno)3s - %(funcName)-20s ] %(message)s")
if config.debug_mode:
    logger.setLevel(logging.DEBUG)
else:
    logger.setLevel(logging.INFO)

description = '''
A discord bot designed to enhance league of legends.
Made by Ghostal#0001 and snooozer#0642.

Made possible with:
    - discord.py - https://github.com/Rapptz/discord.py
    - casseopeia - https://github.com/meraki-analytics/cassiopeia
'''

extensions = [
    'cogs.OAuth2'
]

class RiftCompanion(commands.AutoShardedBot):
    def __init__(self):
        super().__init__(
            command_prefix=commands.when_mentioned_or(config.discord_prefix), 
            description=description, case_insensitive=True, fetch_offline_members=True,
        ) 
        super().remove_command('help')
        self.running = False
        self.debug_mode = config.debug_mode
        self.session = aiohttp.ClientSession(loop=self.loop)

        self.league_connections = {}

        self.riot = riot
        self.riot.set_riot_api_key(config.riot_api_key)
        self.riot.set_default_region("EUW")

        try:
            for extension in extensions:
                self.load_extension(extension)
            #extension = self.load_extension(error_handler)
        except Exception as e:
            exc = '{}: {}'.format(type(e).__name__, e)
            print('Failed to load extension {}\n{}'.format(extension, exc))
            logger.error(traceback.format_exc())

    def run(self):
        super().run(config.discord_token, reconnect=True)

    def load_extension(self, name):
        '''
        Overriding the discord.py load_extension function.
        Instead of passing an instance of 'bot' to the setup function;
        pass an instance of 'self' so we have access to custom attributes
        inside of our cogs.
        '''
        if name in self.extensions:
            return

        lib = importlib.import_module(name)
        if not hasattr(lib, 'setup'):
            del lib
            del sys.modules[name]
            raise discord.ClientException('extension does not have a setup function')

        lib.setup(self)
        self.extensions[name] = lib

    @property
    def config(self):
        return __import__('config')

    async def on_ready(self):
        if not hasattr(self, 'uptime'):
            self.uptime = datetime.datetime.utcnow()

        print('Ready: {0} (ID: {1})'.format(self.user, self.user.id))
        print('Discord Version: {0}'.format(discord.__version__))
        print('-----------------------')

        game = discord.Game('Testing...')
        try:
            await bot.change_presence(status=discord.Status.online, game=game)
        except TypeError: # Backwards compatability
            await bot.change_presence(status=discord.Status.online, activity=game)
    

    async def restart(self, extension):
        """
        Used to reload an extension.
        """
        print(bot.extensions)

    async def on_member_update(self, before, after):
        pass

bot = RiftCompanion()
bot.run()