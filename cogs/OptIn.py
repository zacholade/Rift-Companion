import discord
from discord.ext import commands


class OptIn(object):
    def __init__(self, bot):
        self.bot = bot
        self.reaction_emojis = [
            ('\N{INBOX TRAY}', self._optin),
            ('\N{OUTBOX TRAY}', self._optout)
        ]

    async def optinate(self, message, optin=True, optout=False):
        """
        Adds optin and optoutreaction emojis to a message!
        """
        if optin:
            await message.add_reaction(self.reaction_emojis[0][0])
        if optout:
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

        await self._optin(user)
    
    async def _optin(self, ctx=None, user, pregame=True, postgame=True):
        self.bot.users_db.add_opt_in(user.id, pregame=True, postgame=True)
        pregame, postgame = self.bot.users_db.get_opt_in(user.id)

        description = 
        embed = discord.embed(description=description, colour=self.bot.colours.get('green'))
        destination = ctx if ctx else user
        await destination.send(embed)

    
    async def _optout(self, user):
        pass

    @commands.command(aliases=['opt-in','opt','imin','sub','subscribe'])
    async def optin(self, ctx):
        await self._optin(ctx, user=ctx.author)

def setup(bot):
    n = OptIn(bot)
    bot.add_cog(n)