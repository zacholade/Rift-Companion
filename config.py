# General
debug_mode = True

# Postgresql
postgresql = 'postgresql://rcomp:password@localhost/rcomp'

# API Keys
riot_api_key = '<insert riot api key here>'
championgg_api_key = '<insert championgg key here>'

# Discord
discord_prefix = '!'
discord_token = '<insert token here>'
discord_emoji_pool_guild_ids = [
    528327713438826497,
    528327793843503156,
    528327910017335296,
    528327968838123520,
    528328028095512576,
    528328084227883050,
    528329259035656215,
    528329316124327936,
    528329366250323968,
    528329414275235870,
    528329453550436363,
    528329503790071818,
    528329549956513792,
    528329600842072065,
]

# OAuth2 for requesting access to a users connections
DISCORD_CLIENT_SECRET = ''
DISCORD_REDIRECT_URI = 'http://localhost:5006/callback' # This must be registered to the application
SCOPES = ['identify', 'connections']
OAUTH2_PORT = 5006
