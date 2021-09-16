import discord

from typing import Union
import itertools



class CacheType(dict):

    def get_one_or_none(self, guild, key) -> Union[None, discord.Guild, discord.Member, discord.TextChannel, discord.VoiceChannel, discord.Role]:
        try:
            _guild = self[guild.id]
            return discord.utils.get(_guild, id=int(key))
        except KeyError:
            return None
    

    def get_multi_or_none(self, guild, _filter) -> Union[None, list]:
        try:
            _guild = self[guild.id]
            found = filter(_filter, _guild)
            if len(found) == 0:
                return None
            else:
                return found
        except KeyError:
            return None


    def get_all(self, guild):
        try:
            return self[guild.id]
        except KeyError:
            return None


    def get(self, guild, key):
        return self.get_one_or_none(guild, key)


class UserCache:
    def __init__(self, user_list):
        self.l = user_list

    def get(self, _id):
        return discord.utils.get(self.l, id=int(_id))

    def clear(self):
        self.l.clear()

    def add_to_cache(self, guild):
        for m in guild.members:
            if not m in self.l:
                self.l.append(m)

    def __repr__(self):
        return self.l




class Cache:
    def __init__(self, bot):
        self.bot = bot

        self.guilds = CacheType()
        self.members = CacheType()
        self.roles = CacheType()
        self.text_channels = CacheType()
        self.voice_channels = CacheType()

        self.users = UserCache([])


    def build(self, _return=True):
        self.users = UserCache(list(set(list(itertools.chain(*[x.members for x in self.bot.guilds])))))
        for guild in self.bot.guilds:
            self.guilds[guild.id] = guild
            self.members[guild.id] = guild.members
            self.roles[guild.id] = guild.roles
            self.text_channels[guild.id] = guild.text_channels
            self.voice_channels[guild.id] = guild.voice_channels
        
        if _return:
            return self


    def build_for_guild(self, guild):
        self.guilds[guild.id] = guild
        self.members[guild.id] = guild.members
        self.roles[guild.id] = guild.roles
        self.text_channels[guild.id] = guild.text_channels
        self.voice_channels[guild.id] = guild.voice_channels


    def destroy(self, guild_id=None):
        if guild_id is None:
            self.guilds.clear()
            self.members.clear()
            self.roles.clear()
            self.text_channels.clear()
            self.voice_channels.clear()
        else:
            if guild_id in self.guilds:
                del self.guilds[guild_id]
                del self.members[guild_id]
                del self.roles[guild_id]
                del self.text_channels[guild_id]
                del self.voice_channels[guild_id]


    def build_for_guild(self, guild):
        if not guild.id in self.guilds:
            self.users.add_to_cache(guild)
            self.guilds[guild.id] = guild
            self.members[guild.id] = guild.members
            self.roles[guild.id] = guild.roles
            self.text_channels[guild.id] = guild.text_channels
            self.voice_channels[guild.id] = guild.voice_channels