

# Normal Imports
import os
import json
from requests import HTTPError

# Dependencies
from riotwatcher import RiotWatcher

# Local Imports
import config
from objects import Region, Summoner

# Logging
import logging
logger = logging.getLogger('root')
logging.basicConfig(format="[%(asctime)s %(levelname)-8s %(filename)-15s:%(lineno)3s - %(funcName)-20s ] %(message)s")
if config.debug_mode:
    logger.setLevel(logging.DEBUG)
else:
    logger.setLevel(logging.INFO)


class RiotClient(RiotWatcher):
    """
    Extends RiotWatcher to save data between sessions.
    """
    def __init__(self, config):
        RiotWatcher.__init__(self, config.riot_api_key)
        self.debug_mode = config.debug_mode

        self.champions = []
        self.regions = {}


    def _reload_data(self):
        # Ensure file paths exist.
        if not os.path.isdir('data'):
            logger.info('No directory called "data" found. Making directory.')
            os.makedirs('data')

        if not os.path.isdir('data/regions'):
            logger.info('No directory called "data/regions" found. Making directory.')
            os.makedirs('data/regions')

        for region_name in ['br1', 'eun1', 'euw1', 'jp1', 'kr', 'la1', 'la2', 'na', 'na1', 'oc1', 'tr1', 'ru', 'pbe1']:
            if not os.path.isdir('data/regions/%s.json' % region_name):
                logger.info('No directory called "data/regions/%s" found. Making directory.' % region_name)
                with open("data/regions/%s.json" % region_name, 'w') as f:
                    json.dump({}, f, indent=4)

                self.regions[region_name] = (Region(region_name))
            else:
                # Reload data
                # region_data = json.load(f)
                # for account_id, data in region_data.keys()
                pass

    def get_summoner(self, region, name):
        try:
            summoner = Summoner(self.summoner.by_name(region, name))
            if not self.regions[region].summoners.get(summoner.account_id):
                self.regions[region].summoners[summoner.account_id] = summoner
            

        except HTTPError as e:
            if e.resgponse.status_code == 429:
                print('We should retry in {} seconds.'.format(e.headers['Retry-After']))
                print('this retry-after is handled by default by the RiotWatcher library')
                print('future requests wait until the retry-after time passes')
            elif e.response.status_code == 404:
                print('Summoner with that ridiculous name not found.')
            else:
                raise

def as_complex(d):
    for k, v in d:
        return Region()


        
client = RiotClient(config)
client._reload_data()
users = ['SirGhostal', 'Bob', 'Simon']
for user in users:
    client.get_summoner('euw1', user)
print(client.regions)
