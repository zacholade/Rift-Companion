import datetime
import time
import aiohttp


API_BASE_URL = 'https://discordapp.com/api'
AUTHORIZATION_BASE_URL = API_BASE_URL + '/oauth2/authorize'
TOKEN_URL = API_BASE_URL + '/oauth2/token'

 access_token, token_type, refresh_token, token_url,
                 session=None, revoke_url=None,
                 expires_in=None, expires_at=None):


class TokenInvalidError(Exception):
    """
    Raised if a request is attempted to be made against a token which is invalid.
    """
    pass


class DiscordOAuth2Token(object):
    """
    Token object for OAuth 2.0.
    """

    def __init__(self, access_token, client_id, client_secret, token_type,
                 refresh_token, scope, token_url, revoke_url=None, identifier=None, 
                 session=None, expires_in=None, expires_at=None, cache=None):
        """
        Create an instance of DiscordOAuth2Token.

        Args:
            access_token: string, access token.
            client_id: string, client identifier.
            client_secret: string, client secret.
            token_type: string, the type of token this is. (Bearer)
            scope: string, the scopes this token grants access to.
            refresh_token: string, refresh token.
            token_url: string, URL of token endpoint.
            revoke_url: string, URL for revoke endpoint. Defaults to None; a
                        token can't be revoked if this is None.
            identifier: integer, the id of the user which this corresponds to.
            session: aiohttp.ClientSession, The session to make http requests.
                     It is highly recommended you pass this to speed
                     up performence. See the following link for info on this.
                     https://aiohttp.readthedocs.io/en/stable/client_quickstart.html#make-a-request
            expires_in: int, seconds until the access_token expires
            expires_at: datetime, when the access_token expires.
            database: class, the class which represents your database.
                      Must have a function called 'add_oauth_token'
        """
        self.access_token = access_token
        self.client_id = client_id
        self.client_secret = client_secret
        self.token_type = token_type
        self.refresh_token = refresh_token
        self._scope = scope

        self.token_url = token_url
        self.revoke_url = revoke_url
        
        self.identifier = identifier

        self._session = session if session else aiohttp.ClientSession()

        if not expires_in and expires_at:
            raise ValueError('Must provide one of either expires_in or expires_at')

        self.expires_at = expires_at if expires_at else datetime.datetime.now() + datetime.timedelta(seconds=expires_in)

        # True if the token has been revoked and can't be refreshed.
        self.invalid = False

        self.database = database
        if self.database:
            self.database.add_oauth_token(self)

    @property
    def scope(self):
        return " ".join(self._scope)

    @scope.setter
    def scope(self, scope):
        if isinstance(scope, str):
            self._scope = scope.split(' ')

        elif isinstance(scope, list):
            self._scope = scope

        else:
            raise ValueError('Scope must be a list of strings (scopes) or string split by a space.')

    @property
    def expires_in(self):
        """
        Returns the seconds until the access token expires.
        If the token has expired, returns how long the token 
        has been expired (negative)
        """
        return datetime.datetime.now() - self.expires_at
    
    @expires_in.setter
    def expires_in(self, expires_in):
        """
        Sets how long until the token expires.
        expires_in is stored as a datetime accessible via the expires_at attribute.
        expires_in is just calculated from the expires_at attribute.
        """
        self.expires_at = datetime.datetime.now() + datetime.timedelta(seconds=expires_in)

    @property
    def expired(self):
        """
        Returns True if the token has expired and False if it hasn't.
        If the token is invalid, also returns True.
        """
        if self.invalid:
            return True

        return True if self.expires_at < datetime.datetime.now() else False

    @property
    def request_headers(self):
        """
        Returns the headers used to make an api request against the token_url
        """
        return {'Authorization': self.token_type + ' ' + self.access_token}

    @property
    def session(self):
        """
        Returns the session which the token uses to make http requests
        """
        return self._session

    @session.setter
    def session(self, session):
        """
        Sets the ClientSession which is used for making http requests
        Returns the session which was passed to it.
        """
        if not isinstance(session, aiohttp.ClientSession):
            raise ValueError('session must be an instance of aiohttp.ClientSession')

        self._session = session

    def _construct_data(self, grant_type):
        return {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': grant_type,
            'refresh_token': self.refresh_token,
            'redirect_uri': self.redirect_uri,
            'scope': self.scope
        }

    async def revoke(self):
        """
        Revokes the access token and invalidates the refresh token.
        This action is irreversable. Token is invalid after calling.
        """
        if self.invalid:
            return
        
        # TODO

    async def make_request(self, endpoint):
        """
        Called to make an api request against the token.
        Args:
            endpoint: string, the endpoint to call eg: '/users/@me/connections'
        
        Returns:
            response: dict, the json response from the api
        
        Raises:
            TokenInvalidError: error, if a request is made against the token
                               and it is invalid.
        """
        if self.invalid:
            raise TokenInvalidError("Token has been invalidated and cannot be refreshed")

        if self.expired:
            await self.refresh()

        if not endpoint.startswith('http'):
            endpoint = self.token_url + endpoint

        return await self.get(endpoint, headers=self.request_headers)

    async def refresh(self):
        """
        Refreshes the OAuth2 token. This method should not usually be called.
        It is automatically called if the token has expired when you make
        a request.
        """
        data = self._construct_data('refresh_token')

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        new_token = await self.post(self.token_url, headers=headers, data=data)

        # Update the token with the new token
        self.access_token = new_token['access_token']
        self.refresh_token = new_token['refresh_token']
        self.expires_in = new_token['expires_in']
        self.scope = new_token['scope']
        self.token_type = new_token['token_type']

        if self.database:
            await self.database.

    async def revoke(self):
        """
        Revokes the token and marks it as invalid
        """
        raise NotImplementedError # TODO

    async def get(self, endpoint, headers=None, params=None):
        return await self.request('GET', endpoint, headers=headers, params=params)

    async def post(self, endpoint, headers=None, data=None):
        return await self.request('POST', endpoint, headers=headers, data=data)

    async def request(self, method, endpoint, headers=None, params=None, data=None):
        async with self._session.request(method, endpoint, headers=headers, params=params, data=data) as response:
            response.raise_for_status()
            return await response.json()


