from os import stat
import discord
from discord.ext import commands



class AutoModPlugin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db
        self.config = bot.config
        self.locale = bot.locale


    def get_prefix(self, guild):
        p = self.db.configs.get(guild.id, "prefix")
        return p if p != None else "+"


    @staticmethod
    def can(perm):
        def predicate(ctx):
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
                    raise commands.MissingPermissions([perm])
                else:
                    raise commands.MissingPermissions([perm])
            else:
                return True
        
        return commands.check(predicate)