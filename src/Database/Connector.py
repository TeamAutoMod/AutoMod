import os
import json
from pymongo import MongoClient



def get_db_host() -> str:
    with open("./Config/config.json", "r", encoding="utf8") as f:
        i = json.load(f)
        return i["DB_HOST"]

db_host = get_db_host() # somehow we can't fetch this from config.json without breaking everything (circular import stuff)

class Database(MongoClient):
    def __init__(self, host=db_host, port=None, **kwargs):
        super().__init__(host=host, port=port, **kwargs)


    @property
    def configs(self):
        cluster = self.webdashboard
        return cluster.guildconfigs


    @property
    def ranks(self):
        cluster = self.webdashboard
        return cluster.lvl


    @property
    def commands(self):
        cluster = self.webdashboard
        return cluster.cmds


    @property
    def warns(self):
        cluster = self.webdashboard
        return cluster.warns


    @property
    def counts(self):
        cluster = self.webdashboard
        return cluster.counts


    @property
    def levels(self):
        cluster = self.webdashboard
        return cluster.lvl

    
    @property
    def mutes(self):
        cluster = self.webdashboard
        return cluster.mutes

    
    @property
    def inf(self):
        cluster = self.webdashboard
        return cluster.infractions