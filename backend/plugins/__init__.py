import discord
from discord.ext import commands as _commands

from typing import Union

from ..bot import ShardedBotInstance



class AutoModPlugin(_commands.Cog):
    #commands: list
    def __init__(self, bot: ShardedBotInstance):
        self.bot = bot
        self.db = bot.db
        self.config = bot.config
        self.locale = bot.locale
        #self.register_commands()
    

    # def register_commands(self):
    #     for cmd in self.commands:
    #         self.bot.add_command(cmd)


    def get_prefix(self, guild: discord.Guild) -> str:
        p = self.db.configs.get(guild.id, "prefix")
        return p if p != None else self.bot.config.default_prefix


    @staticmethod
    def can(perm: str):
        def predicate(ctx: _commands.Context) -> Union[bool, _commands.MissingPermissions]:
            if getattr(
                ctx.author.guild_permissions,
                perm
            ) == False:
                if perm not in ["administrator", "manage_guild"]:
                    rid = ctx.bot.db.configs.get(ctx.guild.id, "mod_role")
                    if rid != "":
                        r = ctx.guild.get_role(int(rid))
                        if r != None:
                            if r in ctx.author.roles:
                                return True
                    raise _commands.MissingPermissions([perm])
                else:
                    raise _commands.MissingPermissions([perm])
            else:
                return True
        
        return _commands.check(predicate)


    def before_load(self, *args, **kwargs) -> None:
        super().cog_load(*args, **kwargs)

    
    def after_load(self, *args, **kwargs) -> None:
        super().cog_unload(*args, **kwargs)