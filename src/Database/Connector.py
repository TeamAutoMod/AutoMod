import os
from pymongo import MongoClient



db_host = "mongodb+srv://automod:secret1337@webdb.iktex.mongodb.net/" # somehow we can't fetch this from master.json without breaking everything (circular import stuff)

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