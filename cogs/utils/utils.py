from oauthlib.oauth2.rfc6749.parameters import prepare_grant_uri

import secrets

def new_authorization_url(uri, client_id, response_type=None,
                          redirect_uri=None, scope=None, state=None):
    """
    Makes an authorization url with the provided parameters.
    Returns:
        :str:`authorization_url`
        :str:`state`
    """
    if not state:
        state = secrets.token_urlsafe(32)

    return prepare_grant_uri(uri=uri, client_id=client_id, response_type=response_type,
                             redirect_uri=redirect_uri, scope=scope, state=state), state