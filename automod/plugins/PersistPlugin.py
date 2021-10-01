import discord
from discord.ext import commands

import traceback

from .PluginBlueprint import PluginBlueprint



class PersistPlugin(PluginBlueprint):
    def __init__(self, bot):
        super().__init__(bot)


    @commands.Cog.listener()
    async def on_member_remove(
        self,
        member
    ):
        guild = member.guild
        if guild is None:
            return
        
        if self.db.configs.get(guild.id, "persist") is False:
            return

        if self.db.persists.exists(f"{guild.id}-{member.id}"):
            return
        
        old_roles = [x.id for x in member.roles if x != guild.default_role and x < member.guild.me.top_role]
        old_nick = member.nick if member.nick is not None else ""

        if len(old_roles) < 1 and old_nick == "":
            return

        self.db.persists.insert(self.schemas.Persist(guild.id, member.id, old_roles, old_nick))


    @commands.Cog.listener()
    async def on_member_join(
        self,
        member
    ):
        guild = member.guild
        if guild is None:
            return
        
        if self.db.configs.get(guild.id, "persist") is False:
            return

        _id = f"{guild.id}-{member.id}"
        if not self.db.persists.exists(_id):
            return

        roles = self.db.persists.get(_id, "roles")
        nick = self.db.persists.get(_id, "nick")

        can_add = []
        for x in roles:
            role_obj = await self.bot.utils.getRole(guild, x)
            if role_obj is None:
                pass
            elif role_obj >= guild.me.top_role:
                pass
            elif role_obj in member.roles:
                pass
            else:
                can_add.append(role_obj)

        try:
            await member.edit(nick=nick)
        except Exception:
            pass
        finally:
            try:
                await member.add_roles(*can_add)
            except Exception:
                pass
            self.db.persists.delete(_id) 



def setup(bot):
    bot.add_cog(PersistPlugin(bot))