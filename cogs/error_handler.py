from . import BaseCog

from .utils.errors import *
from .utils.assets import colour, assets

import discord
from discord.ext import commands

import traceback


class CommandErrorHandler(BaseCog):
    def __init__(self, bot):
        super().__init__(bot)
        self.oauth2 = self.bot.get_cog('OAuth2')
        self.bot.loop.set_exception_handler(self.exception_handler)

    async def on_command_error(self, ctx, error):
        if isinstance(error, NoConnectionFound):
            content = (":raised_hand: I couldn't do this because I couldn't "
                       "find a League account connected to your Discord profile?\n\n"
                       ":link: **To link an account;**\n"
                       "    `1.` Open and login to your __League Client__.\n"
                       "    `2.` __On Discord__; head over to *User Settings > Connections.*\n"
                       "    `3.` Click on the League Icon and click Enable. *(shown below)*")
            description = f""":point_right: Once you have done this; [follow the authorization link again!]({self.oauth2.new_authorization_url()})\n
            :two_hearts: For anymore help, [join our support server.](https://discord.gg/SNNaN2a)"""
            embed = discord.Embed(title="League Account Linking", description=description, colour=colour.get('yellow'), url=self.oauth2.new_authorization_url())
            embed.set_image(url=assets.get('connect_league_to_discord'))
            await ctx.author.send(content=content, embed=embed)
            
        elif isinstance(error, discord.ext.commands.CommandOnCooldown):
            error = str(error)
            desc = "This command is on cooldown. Retry in: `" + str(error[34:]) + '`.'
            await ctx.send(desc)

    async def on_error(self, event_method, *args, **kwargs):
        """
        get's invoked when there is an error outside a command
        """
        self.logger.exception(event_method)

    def exception_handler(self, loop, context):
        """
        get's invoked when there is an error inside asyncio
        """
        error_message = context['message']
        exception = None
        if 'exception' in context:
            exception = context['exception']

        if exception:
            tb_lines = traceback.format_exception(exception.__class__, exception, exception.__traceback__)
            self.logger.error("%s\n%s", error_message, ''.join(tb_lines))
        else:
            if 'Task was destroyed but it is pending!' not in error_message:
                self.logger.error(error_message)

def setup(bot):
    n = CommandErrorHandler(bot)
    bot.add_cog(n)