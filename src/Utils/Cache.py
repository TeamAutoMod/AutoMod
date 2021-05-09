import discord
from typing import Union




class CacheType(dict):
    def get_one_or_none(self, guild, key) -> Union[None, discord.Guild, discord.Member, discord.TextChannel, discord.VoiceChannel]:
        try:
            _guild = self.__dict__[guild.id]
            if isinstance(key, int):
                return discord.utils.get(_guild, id=key)
            else:
                return discord.utils.get(_guild, name=key)
        except KeyError:
            return None
    

    def get_multi_or_none(self, guild, _filter) -> Union[None, list]:
        try:
            _guild = self.__dict__[guild.id]
            found = filter(_filter, _guild)
            if len(found) == 0:
                return None
            else:
                return found
        except KeyError:
            return None

    
    def get_all(self, guild):
        try:
            return self.__dict__[guild.id]
        except KeyError:
            return None





class Cache:
    def __init__(self, bot):
        self.bot = bot

        self.guilds = CacheType()
        self.members = CacheType()
        self.text_channels = CacheType()
        self.voice_channels = CacheType()


    def build(self, _return=True):
        for guild in self.bot.guilds:
            self.guilds[guild.id]: discord.Guild = guild
            for cache_type, cache_obj in {x: getattr(self, x) for x in dir(self) if isinstance(x, CacheType)}.items():
                cache_obj[guild.id] = getattr(guild, cache_type)
        
        if _return:
            return self


    def destroy(self):
        for a in [getattr(self, x) for x in dir(self) if isinstance(x, CacheType)]:
            a.clear()