import logging
import typing
import time
import asyncio
import aiohttp

import discord
from discord.ext import commands

from flask import Flask, redirect, request
from oauthlib.oauth2.rfc6749.parameters import prepare_grant_uri
from oauthlib.common import generate_token

import config

from .utils.errors import (
    NoConnectionFound
)
from .utils.assets import colour, assets

API_BASE_URL = 'https://discordapp.com/api'
AUTHORIZATION_BASE_URL = API_BASE_URL + '/oauth2/authorize'
TOKEN_URL = API_BASE_URL + '/oauth2/token'


def extract_region_from_connection(connection):
    pass


def oauth2_server(bot, oauth2):
    app = Flask(__name__)

    @app.route('/')
    def index():
        return redirect(oauth2.authorization_url)

    @app.route('/callback')
    def callback():
        if request.values.get('error'):
            return request.values['error']
        # TODO Implement state. Security vulnerability. 
        # https://discordapp.com/developers/docs/topics/oauth2#state-and-security
        # Supply state in args of the oauth2 request eg: &state=15773059ghq9183habn
        # Check to see if the returned state in the callback is equal to the one sent.
        # This state needs to be unique to the user. Issues happen when the user calls
        # the 'iam' command to link. If other users use the same oauth2 link, they will
        # have the wrong state and an error will be thrown.
        code = request.args.get('code')
        if not code:
            return redirect('/')

        bot.loop.create_task(oauth2.handle_callback(code))
        return redirect('https://discord.gg/SNNaN2a') # TODO Dont hard code invite url.

    app.run('0.0.0.0', port=oauth2.port, debug=False, use_reloader=False)


class OAuth2(object):
    def __init__(self, bot):
        self.bot = bot

        self.client_secret = config.DISCORD_CLIENT_SECRET
        self.redirect_uri = config.DISCORD_REDIRECT_URI
        self.port = config.OAUTH2_PORT
        self.scope = 'identify connections'

        self.bot.loop.create_task(self.start_server())

    @property
    def authorization_url(self):
        """
        Returns an authorization url with no state and parameters specific for the scope of this oauth2 cog.
        """
        return self.make_authorization_url(client_id=self.bot.user.id, response_type='code',
                                           redirect_uri=self.redirect_uri, scope=self.scope)[0]

    def make_authorization_url(self, uri=AUTHORIZATION_BASE_URL, client_id=None, response_type=None,
                               redirect_uri=None, scope=None, state=None):
        """
        Makes an authorization url with the provided parameters.
        Returns:
            :str:`authorization_url`
            :str:`state`
        """
        return prepare_grant_uri(uri=uri, client_id=client_id, response_type=response_type,
                                 redirect_uri=redirect_uri, scope=scope, state=state), state

    async def start_server(self):
        await self.bot.wait_until_ready()
        await self.bot.loop.run_in_executor(None, oauth2_server, self.bot, self)

    async def handle_callback(self, code):
        token = await self.exchange_code_for_token(code)
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
            # TODO just raise NoConnectionFound('leagueoflegends') here instead..
            # However this is out of a command and calls the exception_handler func.
            # It's impossible to get ctx in exception_handler...
            content = ("**Hey {0}!** I couldn't find a League account connected to your Discord profile?\n\n"
                       "**To link an account;**\n"
                       "    `1.` Open and login to your __League Client__.\n"
                       "    `2.` __On Discord__; head over to *User Settings > Connections.*\n"
                       "    `3.` Click on the League Icon and click Enable. *(shown below)*".format(user.display_name))
            description = """Once you have done this; [follow the authorization link again!]({1})\n
            For anymore help, [join our support server.](https://discord.gg/SNNaN2a)""".format(user.display_name, self.authorization_url)
            embed = discord.Embed(title="League Account Linking", description=description, colour=colour.get('yellow'), url=self.authorization_url)
            embed.set_image(url=assets.get('connect_league_to_discord'))
            await user.send(content=content, embed=embed)

        elif user_id and connection:
            self.bot.database.add_oauth_token(user_id, token)
            for connection in connections:
                self.bot.database.add_connection(user_id, connection)

            user = self.bot.get_user(user_id)
            description = (":link: Your League account, **{0}** has been linked successfully!\n\n"
                           ":inbox_tray: You can now `opt-in` and receive **automatic** pre/post-game analysis."
                           "Alternatively, you can **manually** invoke the `!live` command.").format(connection.get('name'))
            embed = discord.Embed(title="League Account Linking", description=description, colour=colour.get('green'), url=self.authorization_url)
            embed.set_thumbnail(url=assets.get('l_icon'))
            embed.set_footer(text='You can opt-out at anytime...')
            # TODO Get summoner icon of the users league account.
            message = await user.send(embed=embed)
            await self.bot.get_cog('OptIn').optinate(message)
        # It would only get to here if the user used an oauth link and
        # 'identify' wasn't in the scope. Therefore, this code is
        # useless as we could get the connections but wouldn't know
        # who's discord account's they are...
        return

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
            return await response.json()

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
        description = (":unlock: Unlock **exclusive features** by [linking your League account to me here.]({})\n\n"
        "*Ensure your league account is connected to discord first.*".format(self.authorization_url))
        embed = discord.Embed(title="League Account Linking", description=description, colour=colour.get('yellow'), url=self.authorization_url)
        embed.set_image(url=assets.get('connections'))
        await ctx.send(embed=embed)
        print(self.bot.database.get_connection(ctx.author.id, 'leagueoflegends'))


def setup(bot):
    n = OAuth2(bot)
    bot.add_cog(n)
