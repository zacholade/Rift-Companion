## What am I?

Rift Companion is an intelligent Discord bot which provides you with vital information right as you need it!

It has well developed discord integrations to link your **Verified** League account to the bot, thus extending its functionality. No need to write out a complicated command; just opt-in and receive automatic pre and post game analysis to help you improve faster!

[Invite the bot today!](https://discordapp.com/api/oauth2/authorize?client_id=521163284418789376&permissions=0&scope=bot)

## Setup

Developed using Python 3.6.7

**2) Install dependencies**

`python3 -m pip install -r requirements.txt`

**3) Create database**

Using the psql tool.
`sudo -u postgres psql postgres`
```sql
CREATE ROLE rcomp WITH LOGIN PASSWORD 'yourpw';
CREATE DATABASE rcomp OWNER rcomp;
CREATE EXTENSION pg_trgm;
```

**4) Update config file**

Inside `config.py`, update the postgresql information.
```py
postgresql = 'postgresql://user:password@host/database' # your postgresql info from above
```
