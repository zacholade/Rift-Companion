import os
import asyncio
import asyncpg
import contextlib

import config
from bot import RiftCompanion

# Logging
import logging
from logging.handlers import TimedRotatingFileHandler
import traceback


@contextlib.contextmanager
def setup_logging():
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    try:
        DEFAULT_LOGGING_FORMAT = "[%(asctime)s %(levelname)-8s %(filename)-15s:%(lineno)3s - %(funcName)-20s ] %(message)s"

        # logging.getLogger('discord')
        # logging.getLogger('discord.http')

        logger = logging.getLogger('root')

        logging.basicConfig(format=DEFAULT_LOGGING_FORMAT)
        if config.debug_mode:
            logger.setLevel(logging.DEBUG)
        else:
            logger.setLevel(logging.INFO)

        loggerFileHandler = TimedRotatingFileHandler('logs/rcomp.log', when='midnight', backupCount=1000)
        loggerFileHandler.setFormatter(logging.Formatter(DEFAULT_LOGGING_FORMAT))
        loggerFileHandler.doRollover()

        logger.addHandler(loggerFileHandler)

        yield
    finally:
        # __exit__
        handlers = logger.handlers[:]
        for hdlr in handlers:
            hdlr.close()
            logger.removeHandler(hdlr)

def run_bot():
    loop = asyncio.get_event_loop()
    logger = logging.getLogger(__name__)

    try:
        pool = loop.run_until_complete(asyncpg.create_pool(config.postgresql, command_timeout=60))
    except Exception as e:
        logger.exception('Could not set up PostgreSQL. Exiting.')
        return

    bot = RiftCompanion()
    bot.pool = pool
    bot.run() 

def main():
    with setup_logging():
        run_bot()

if __name__ == "__main__":
    main()