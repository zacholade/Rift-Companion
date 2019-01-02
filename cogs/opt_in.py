from . import BaseCog

from .utils.checks import (
    user_has_connection
)
from .utils.assets import colour, assets

import discord
from discord.ext import commands


class OptIn(BaseCog):
    def __init__(self, bot):
        super().__init__(bot)
        self.reaction_emojis = [
            ('\N{INBOX TRAY}', self._optin),
            ('\N{OUTBOX TRAY}', self._optout)
        ]

    async def optinate(self, message, optin=True, optout=False):
        """
        Adds optin and optout reaction emojis to a message!
        """
        if optin:
            await message.add_reaction(self.reaction_emojis[0][0])
        elif optout:
            await message.add_reaction(self.reaction_emojis[0][0])

    async def on_raw_reaction_add(self, *argv):
        emoji = message_id = channel_id = user_id = None
        if len(argv) == 4:
            emoji, message_id, channel_id, user_id = (argv[0], argv[1], argv[2], argv[3])
        else: # discord.raw_models.RawReactionActionEvent
            p = argv[0]
            emoji, message_id, channel_id, user_id = (p.emoji, p.message_id, p.channel_id, p.user_id)
        await self.handle_reaction_add(emoji, message_id, channel_id, user_id)

    async def handle_reaction_add(self, emoji, message_id, channel_id, user_id):
        def check_is_not_bot_reacting(user_id):
            if user_id == self.bot.user.id:
                return False
            return True

        def check_is_correct_emoji(emoji):
            if emoji.name == self.reaction_emojis[0][0]:
                return True
            return False

        def check_is_dm_channel(channel):
            if isinstance(channel, discord.DMChannel):
                return True
            return False

        def check_is_correct_message(message):
            if not message or not message.embeds:
                return False
            if message.author.id != self.bot.user.id:
                return False
            if 'League Account Linking' not in message.embeds[0].title:
                return False
            return True

        if not check_is_not_bot_reacting(user_id):
            return
        if not check_is_correct_emoji(emoji):
            return

        user = self.bot.get_user(user_id)
        if user is None:
            return

        channel = self.bot.get_channel(channel_id)
        if channel is None: # Must be an unloaded dm channel.
            channel = await user.create_dm()
            if channel is None or channel.id != channel_id:
                return
        if not check_is_dm_channel(channel):
            return

        message = await channel.get_message(message_id)
        if not check_is_correct_message(message):
            return

        await self._optin(channel, user)

    async def _optin(self, invoked_channel, user):
        await self.bot.database.set_opt_in(user.id, opted_in=True)
        description = (':inbox_tray: You are now opted in for **automatic game analysis!**.\n\n'
                       ':video_game: Make sure you are **online** and display your **activity** on discord '
                       'to automatically receive this analysis! *(shown below)*')
        embed = discord.Embed(title="League Game Analysis", description=description, colour=colour.get('green'))
        embed.set_image(url=assets.get('show_game_status'))
        await invoked_channel.send(embed=embed)

    async def _optout(self, user):
        await self.bot.database.set_opt_in(user.id, opted_in=False)

    @user_has_connection('leagueoflegends')
    @commands.command(aliases=['opt-in','opt','imin','sub','subscribe'])
    async def optin(self, ctx):
        await self._optin(ctx, ctx.author)

def setup(bot):
    n = OptIn(bot)
    bot.add_cog(n)