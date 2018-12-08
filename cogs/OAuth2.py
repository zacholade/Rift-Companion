import logging
import typing

import discord

from flask import Flask, g, session, redirect, request, url_for, jsonify
from requests_oauthlib import OAuth2Session

import config


API_BASE_URL = 'https://discordapp.com/api'
AUTHORIZATION_BASE_URL = API_BASE_URL + '/oauth2/authorize'
TOKEN_URL = API_BASE_URL + '/oauth2/token'


def oauth2_server(bot, oauth2):
    app = Flask(__name__)

    app.config['SECRET_KEY'] = oauth2.client_secret

    def make_session(token=None, state=None, scope=None):
        return OAuth2Session(
            client_id=bot.user.id,
            token=token,
            state=state,
            scope=scope,
            redirect_uri=oauth2.redirect_url,
            auto_refresh_kwargs={
                'client_id': bot.user.id,
                'client_secret': oauth2.client_secret,
            },
            auto_refresh_url=TOKEN_URL,
            token_updater=token_updater
            )

    def token_updater(self, token):
        oauth2_tokens.append(token)

    @app.route('/')
    def index():
        scope = request.args.get(
            'scope',
            'identify connections')
        discord = make_session(scope=scope.split(' '))
        # Don't pass None here as the state arg and a state will be generated
        # https://github.com/requests/requests-oauthlib/blob/master/requests_oauthlib/oauth2_session.py
        authorization_url, state = discord.authorization_url(AUTHORIZATION_BASE_URL, None)
        # session['oauth2_state'] = state See below for implementation of state...
        return redirect(authorization_url)


    @app.route('/callback')
    def callback():
        if request.values.get('error'):
            return request.values['error']

        code = request.args.get('code')
        # TODO Implement state. Security vulnerability. 
        # https://discordapp.com/developers/docs/topics/oauth2#state-and-security
        # Supply state in args of the oauth2 request eg: &state=15773059ghq9183habn
        # Check to see if the returned state in the callback is equal to the one sent.
        # This state needs to be unique to the user. Issues happen when the user calls
        # the 'iam' command to link. If other users use the same oauth2 link, they will
        # have the wrong state and an error will be thrown.

        discord = make_session() # Would pass state to your session here.
        code = request.args.get('code')
        if not code:
            return redirect('/')
        token = discord.fetch_token(
            TOKEN_URL,
            client_secret=oauth2.client_secret,
            code=code
        )
        user_id = None
        connection = None
        if 'identify' in token['scope']:
            user_id = get_user(token, discord)

        # If identify wasn't in the scope, then we have no idea what account is linked to the connection.
        # Make sure we were able to extract a user id before continuing for caching.
        if 'connections' in token['scope'] and user_id:
            connection = get_connection(user_id, discord)

        print(oauth2.oauth2_tokens)
        print(bot.league_connections)
        bot.loop.create_task(oauth2.new_connection_callback(user_id, connection))
        return redirect('https://discord.gg/SNNaN2a') # TODO Dont hard code invite url.

    def get_user(token, discord):
        user = discord.get(API_BASE_URL + '/users/@me').json()
        user_id = user.get('id')
        if user_id:
            user_id = int(user_id)
        oauth2.oauth2_tokens[user_id] = token
        return user_id


    def get_connection(user_id, discord):
        connections = discord.get(API_BASE_URL + '/users/@me/connections').json()
        connection = None
        for n, connection_type in enumerate(connection['type'] for connection in connections):
            if connection_type == 'leagueoflegends':
                connection = connections[n]
                break
        if connection:
            bot.league_connections[user_id] = connection
        return connection
        

    app.run('0.0.0.0', port=oauth2.port, debug=False, use_reloader=False)


class OAuth2(object):

    client_secret = config.DISCORD_CLIENT_SECRET
    redirect_url = config.DISCORD_REDIRECT_URL
    port = config.OAUTH2_PORT

    def __init__(self, bot):
        self.bot = bot
        self.oauth2_tokens = {}

    async def on_ready(self):
        await self.bot.loop.run_in_executor(None, oauth2_server, self.bot, self)

    async def new_connection_callback(self, user_id, connection):
        user = self.bot.get_user(user_id)
        await user.send('Connected account: ' + connection.get('name'))


def setup(bot):
    n = OAuth2(bot)
    bot.add_cog(n)
