import json
import os


class ComplexEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Serializable):
            return obj.to_json()
        # Let the base class default method raise the TypeError
        return json.JSONEncoder.default(self, obj)


class Serializable(object):
    """
    Base class which objects can inherit to be serialized to json.
    """
    def from_json(self, d):
        for k, v in d.items():
            setattr(self, k, v)
        return self

    def to_json(self):
        return self.__dict__

    def __repr__(self):
        return str(self.__dict__)


class Summoner(Serializable):
    def __init__(self, summoner=None):
        self.id = summoner['id'] if summoner else None
        self.account_id = summoner['accountId'] if summoner else None
        self.name = summoner['name'] if summoner else None
        self.profile_icon_id = summoner['profileIconId'] if summoner else None
        self.revision_date = summoner['revisionDate'] if summoner else None
        self.summoner_level = summoner['summonerLevel'] if summoner else None


class Region(Serializable):
    def __init__(self, name):
        self.name = name
        self.summoners = {}
