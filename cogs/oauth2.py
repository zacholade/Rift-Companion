from . import BaseCog

from .utils.errors import (
    NoConnectionFound
)
from .utils.utils import new_authorization_url
from .utils.assets import colour, assets

import typing
import time
import asyncio
from aiohttp import web
import discord
from discord.ext import commands

API_BASE_URL = 'https://discordapp.com/api'
AUTHORIZATION_URL = API_BASE_URL + '/oauth2/authorize'
TOKEN_URL = API_BASE_URL + '/oauth2/token'
REVOKE_URL = API_BASE_URL + 'oauth2/token/revoke'


class OAuth2(BaseCog):
    def __init__(self, bot):
        super().__init__(bot)
        self.app = web.Application()
        self.app.router.add_get('/', self.handle_index)
        self.app.router.add_get('/oauth/discord', self.handle_oauth_discord)
        self.runner = None

        self.states = {} # Dict of key: hashed state and value.

    def new_authorization_url(self, state=None):
        """
        Generates a new authorization url
        Returns an authorization url with parameters specific for the scope of this oauth2 cog.
        """
        url, state = new_authorization_url(AUTHORIZATION_URL, self.bot.user.id, response_type='code',
                                           redirect_uri=self.config.DISCORD_REDIRECT_URI, scope=self.scope, state=state)

        if state not in self.states:
            self.states[state] = 0

        return url

    async def start(self):
        """
        Starts the oauth2 server asynchronously.
        """
        self.runner = web.AppRunner(self.app)
        await self.runner.setup()
        site = web.TCPSite(self.runner, 'localhost', self.config.OAUTH2_PORT)
        await site.start()
    
    async def stop(self):
        """
        Stops the oauth2 server.
        """
        await self.runner.cleanup()
        self.runner = None

    async def handle_index(self, request):
        """
        Called when route "/" is called.
        """
        return web.HTTPFound(self.new_authorization_url())

    async def handle_oauth_discord(self, request):
        """
        Called when route "/oauth/discord" is called
        """
        code = request.rel_url.query.get('code')
        state = request.rel_url.query.get('state')

        if not code or not state:
            # Code or state is not provided. They must go through code grant again.
            self.logger.info('Received request at /oauth/discord but got no code or state.')
            return web.HTTPFound(self.new_authorization_url())

        if state not in self.states or self.states.get(state) > 3:
            # True if state is not valid or state has been used > 3 times.
            return web.HTTPFound(self.new_authorization_url())

        code = DiscordOAuth2Code(code, self._scopes, session=self.bot.session)
        token = code.exchange_for_token()

        if not token:
            # Code wasnt valid? Discord down?
            return web.HTTPFound(self.new_authorization_url())

        if not all(scope in token['scope'].split(' ') for scope in self.config.scopes):
            # If both 'identify' and 'connections' not in the token's scope, it's useless..
            return web.HTTPFound(self.new_authoriation_url())

        self.states[state] += 1

        # Handles new token concurrently to redirecting the user to the landing page
        # for making a valid authorization with valid scope.
        asyncio.ensure_future(self.handle_new_token(token))

        return web.HTTPFound('https://discord.gg/SNNaN2a')

    async def handle_new_token(self, token):
        """
        Called when a new token is aqcuired from the oauth2 flow.
        """
        identity = await self.make_api_request(token, '/users/@me')
        connections = await self.make_api_request(token, '/users/@me/connections')

        user_id = int(identity.get('id'))
        connection = None
        for n, connection_type in enumerate(connection['type'] for connection in connections):
            if connection_type == 'leagueoflegends':
                connection = connections[n]
                break

        if user_id and not connection:
            user = self.bot.get_user(user_id)

            if not user:
                user = await self.bot.get_user_info(user_id)

            # TODO just raise NoConnectionFound('leagueoflegends') here instead..
            # However this is out of a command and calls the exception_handler func.
            # It's impossible to get ctx in exception_handler...
            content = (f"**Hey {user.display_name}!** I couldn't find a League account connected to your Discord profile?\n\n"
                       "**To link an account;**\n"
                       "    `1.` Open and login to your __League Client__.\n"
                       "    `2.` __On Discord__; head over to *User Settings > Connections.*\n"
                       "    `3.` Click on the League Icon and click Enable. *(shown below)*")
            description = f"""Once you have done this; [follow the authorization link again!]({self.new_authorization_url()})\n
            For anymore help, [join our support server.](https://discord.gg/SNNaN2a)"""
            embed = discord.Embed(title="League Account Linking", description=description, colour=colour.get('yellow'), url=self.new_authorization_url())
            embed.set_image(url=assets.get('connect_league_to_discord'))
            await user.send(content=content, embed=embed)

        elif user_id and connection:
            await self.bot.database.add_oauth_token(user_id, token)
            for connection in connections:
                await self.bot.database.add_connection(user_id, connection)

            user = self.bot.get_user(user_id)

            if not user:
                user = await self.bot.get_user_info(user_id)

            description = (f":link: Your League account, **{connection.get('name')}** has been linked successfully!\n\n"
                           ":inbox_tray: You can now `opt-in` and receive **automatic** pre/post-game analysis. "
                           "Alternatively, you can **manually** invoke the `!live` command.") # TODO dont hardcore prefix
            embed = discord.Embed(title="League Account Linking", description=description, colour=colour.get('green'), url=self.new_authorization_url())
            embed.set_thumbnail(url=assets.get('l_icon'))
            embed.set_footer(text='You can opt-out at anytime...')
            # TODO Get summoner icon of the users league account.
            message = await user.send(embed=embed)
            await self.bot.get_cog('OptIn').optinate(message)
        # It would only get to here if the user used an oauth link and
        # 'identify' wasn't in the scope. Therefore, this code is
        # useless as we could get the connections but wouldn't know
        # who's discord account's they are...

    async def exchange_code_for_token(self, code):
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
        }

        data = {
            'client_id': self.bot.user.id,
            'client_secret': self.client_secret,
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': self.redirect_uri,
            'scope': self.scope
        }

        async with self.bot.session.post(TOKEN_URL, data=data, headers=headers) as response:
            response.raise_for_status()

            await response.json()

    async def make_api_request(self, token, endpoint):
        user_id = None
        connection = None
        headers = {'Authorization': token['token_type'] + ' ' + token['access_token']}
        async with self.bot.session.get(API_BASE_URL + endpoint, headers=headers) as response:
            response.raise_for_status()
            return await response.json()

    @commands.command(aliases=['iam', 'add'])
    async def link(self, ctx):
        # Provide oauth2 link to allow access to view users connections and identify.
        # If a connection can be found, finish here and allow callback to handle rest... 
        # Otherwise, tell user how to add a connection and tell them to reuse this command when they have it added.
        authorization_url = self.new_authorization_url()

        description = (":unlock: Unlock **exclusive features** by [linking your League account to me here.]({authorization_url})\n\n"
        "*Ensure your league account is connected to discord first.*")
        embed = discord.Embed(title="League Account Linking", description=description, colour=colour.get('yellow'), url=authorization_url)
        embed.set_image(url=assets.get('connections'))
        await ctx.send(embed=embed)


def setup(bot):
    n = OAuth2(bot)
    bot.add_cog(n)
