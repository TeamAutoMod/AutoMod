from typing import Union
import discord
from discord.ext import commands

import re

from .PluginBlueprint import PluginBlueprint
from .Automod.events import (
    OnMemberJoin
)
from .Automod.sub.CheckMessage import checkMessage
from .Automod.sub.ShouldPerformAutomod import shouldPerformAutomod
from .Types import Reason, Embed
from utils.Raid import enableRaidMode, disableRaidMode


class AutomodPlugin(PluginBlueprint):
    def __init__(self, bot):
        super().__init__(bot)
        self.last_joiners = {}
        self.raids = {}


    async def cog_check(self, ctx):
        return ctx.author.guild_permissions.administrator


    @commands.Cog.listener()
    async def on_automod_event(
        self, 
        message
    ):
        if not shouldPerformAutomod(self, message):
            return
        if message.guild is None or not isinstance(message.guild, discord.Guild):
            return
        if not self.db.configs.exists(message.guild.id):
            return
        if len(self.db.configs.get(message.guild.id, "automod")) < 1:
            return

        await checkMessage(self, message)

    
    @commands.Cog.listener()
    async def on_message_edit(
        self, 
        before, 
        after
    ):
        if not shouldPerformAutomod(self, after):
            return
        if after.guild is None:
            return
        if not self.db.configs.get(after.guild.id, "automod"):
            return
        
        if before.content != after.content and after.content == None:
            return
        
        await checkMessage(self, after)


    @commands.Cog.listener()
    async def on_member_join(
        self,
        member
    ):
        await OnMemberJoin.run(self, member)


    @commands.group()
    async def automod(
        self,
        ctx
    ): 
        """automod_help"""
        if ctx.invoked_subcommand is None:
            prefix = self.bot.get_guild_prefix(ctx.guild)
            e = Embed(
                title=self.i18next.t(ctx.guild, "automod_title"),
                description=self.i18next.t(ctx.guild, "automod_description", prefix=prefix)
            )
            e.add_field(
                name="❯ Commands",
                value=self.i18next.t(ctx.guild, "automod_commands", prefix=prefix)
            )
            await ctx.send(embed=e)


    @automod.command()
    async def invite(
        self, 
        ctx,
        warns: str
    ):
        """invite_help"""
        warns = warns.lower()
        if warns == "off":
            automod = self.db.configs.get(ctx.guild.id, "automod")
            if "invites" in automod:
                del automod["invites"]
            self.db.configs.update(ctx.guild.id, "automod", automod)

            await ctx.send(self.i18next.t(ctx.guild, "automod_feature_disabled", _emote="YES", what="anti-invites"))
        else:
            try:
                warns = int(warns)
            except ValueError:
                e = Embed(
                    title="Invalid paramater",
                    description=self.i18next.t(ctx.guild, "invalid_automod_feature_param", prefix=self.bot.get_guild_prefix(ctx.guild), command="invite <warns>", off_command="invite off")
                )
                await ctx.send(embed=e)
            else:
                if warns < 1:
                    return await ctx.send(self.i18next.t(ctx.guild, "min_warns", _emote="NO"))

                if warns > 100:
                    return await ctx.send(self.i18next.t(ctx.guild, "max_warns", _emote="NO"))

                automod = self.db.configs.get(ctx.guild.id, "automod")
                automod.update({
                    "invites": {"warns": warns}
                })
                self.db.configs.update(ctx.guild.id, "automod", automod)

                await ctx.send(self.i18next.t(ctx.guild, "warns_set", _emote="YES", warns=warns, what="they send Discord invites"))


    @automod.command()
    async def everyone(
        self, 
        ctx,
        warns: str
    ):
        """everyone_help"""
        warns = warns.lower()
        if warns == "off":
            automod = self.db.configs.get(ctx.guild.id, "automod")
            if "everyone" in automod:
                del automod["everyone"]
            self.db.configs.update(ctx.guild.id, "automod", automod)

            await ctx.send(self.i18next.t(ctx.guild, "automod_feature_disabled", _emote="YES", what="anti-everyone"))
        else:
            try:
                warns = int(warns)
            except ValueError:
                e = Embed(
                    title="Invalid paramater",
                    description=self.i18next.t(ctx.guild, "invalid_automod_feature_param", prefix=self.bot.get_guild_prefix(ctx.guild), command="everyone <warns>", off_command="everyone off")
                )
                await ctx.send(embed=e)
            else:
                if warns < 1:
                    return await ctx.send(self.i18next.t(ctx.guild, "min_warns", _emote="NO"))

                if warns > 100:
                    return await ctx.send(self.i18next.t(ctx.guild, "max_warns", _emote="NO"))

                automod = self.db.configs.get(ctx.guild.id, "automod")
                automod.update({
                    "everyone": {"warns": warns}
                })
                self.db.configs.update(ctx.guild.id, "automod", automod)

                await ctx.send(self.i18next.t(ctx.guild, "warns_set", _emote="YES", warns=warns, what="they attempt to mention @everyone/here"))


    # @automod.command()
    # async def caps(
    #     self, 
    #     ctx,
    #     warns: str
    # ):
    #     """caps_help"""
    #     warns = warns.lower()
    #     if warns == "off":
    #         automod = self.db.configs.get(ctx.guild.id, "automod")
    #         if "caps" in automod:
    #             del automod["caps"]
    #         self.db.configs.update(ctx.guild.id, "automod", automod)
            
    #         await ctx.send(self.i18next.t(ctx.guild, "automod_feature_disabled", _emote="YES", what="anti-caps"))
    #     else:
    #         try:
    #             warns = int(warns)
    #         except ValueError:
    #             e = Embed(
    #                 title="Invalid paramater",
    #                 description=self.i18next.t(ctx.guild, "invalid_automod_feature_param", prefix=self.bot.get_guild_prefix(ctx.guild), command="caps <warns>", off_command="caps off")
    #             )
    #             await ctx.send(embed=e)
    #         else:
    #             if warns < 1:
    #                 return await ctx.send(self.i18next.t(ctx.guild, "min_warns", _emote="NO"))

    #             if warns > 100:
    #                 return await ctx.send(self.i18next.t(ctx.guild, "max_warns", _emote="NO"))

    #             automod = self.db.configs.get(ctx.guild.id, "automod")
    #             automod.update({
    #                 "caps": {"warns": warns}
    #             })
    #             self.db.configs.update(ctx.guild.id, "automod", automod)

    #             await ctx.send(self.i18next.t(ctx.guild, "warns_set", _emote="YES", warns=warns, what="there message consists of more than 75% capital letters"))


    @automod.command()
    async def files(
        self, 
        ctx,
        warns: str
    ):
        """files_help"""
        warns = warns.lower()
        if warns == "off":
            automod = self.db.configs.get(ctx.guild.id, "automod")
            if "files" in automod:
                del automod["files"]
            self.db.configs.update(ctx.guild.id, "automod", automod)

            await ctx.send(self.i18next.t(ctx.guild, "automod_feature_disabled", _emote="YES", what="anti-files"))
        else:
            try:
                warns = int(warns)
            except ValueError:
                e = Embed(
                    title="Invalid paramater",
                    description=self.i18next.t(ctx.guild, "invalid_automod_feature_param", prefix=self.bot.get_guild_prefix(ctx.guild), command="files <warns>", off_command="files off")
                )
                await ctx.send(embed=e)
            else:
                if warns < 1:
                    return await ctx.send(self.i18next.t(ctx.guild, "min_warns", _emote="NO"))

                if warns > 100:
                    return await ctx.send(self.i18next.t(ctx.guild, "max_warns", _emote="NO"))

                automod = self.db.configs.get(ctx.guild.id, "automod")
                automod.update({
                    "files": {"warns": warns}
                })
                self.db.configs.update(ctx.guild.id, "automod", automod)

                await ctx.send(self.i18next.t(ctx.guild, "warns_set", _emote="YES", warns=warns, what="they send forbidden/uncommon attachment types"))


    # @automod.command()
    # async def zalgo(
    #     self, 
    #     ctx,
    #     warns: str
    # ):
    #     """zalgo_help"""
    #     warns = warns.lower()
    #     if warns == "off":
    #         automod = self.db.configs.get(ctx.guild.id, "automod")
    #         if "zalgo" in automod:
    #             del automod["zalgo"]
    #         self.db.configs.update(ctx.guild.id, "automod", automod)
            
    #         await ctx.send(self.i18next.t(ctx.guild, "automod_feature_disabled", _emote="YES", what="anti-zalgo"))
    #     else:
    #         try:
    #             warns = int(warns)
    #         except ValueError:
    #             e = Embed(
    #                 title="Invalid paramater",
    #                 description=self.i18next.t(ctx.guild, "invalid_automod_feature_param", prefix=self.bot.get_guild_prefix(ctx.guild), command="zalgo <warns>", off_command="zalgo off")
    #             )
    #             await ctx.send(embed=e)
    #         else:
    #             if warns < 1:
    #                 return await ctx.send(self.i18next.t(ctx.guild, "min_warns", _emote="NO"))

    #             if warns > 100:
    #                 return await ctx.send(self.i18next.t(ctx.guild, "max_warns", _emote="NO"))

    #             automod = self.db.configs.get(ctx.guild.id, "automod")
    #             automod.update({
    #                 "zalgo": {"warns": warns}
    #             })
    #             self.db.configs.update(ctx.guild.id, "automod", automod)

    #             await ctx.send(self.i18next.t(ctx.guild, "warns_set", _emote="YES", warns=warns, what="there message contains zalgo letters."))


    @automod.command()
    async def mentions(
        self, 
        ctx,
        mentions: str
    ):
        """mentions_help"""
        mentions = mentions.lower()
        if mentions == "off":
            automod = self.db.configs.get(ctx.guild.id, "automod")
            if "mention" in automod:
                del automod["mention"]
            self.db.configs.update(ctx.guild.id, "automod", automod)
            
            await ctx.send(self.i18next.t(ctx.guild, "automod_feature_disabled", _emote="YES", what="max-mentions"))
        else:
            try:
                mentions = int(mentions)
            except ValueError:
                e = Embed(
                    title="Invalid paramater",
                    description=self.i18next.t(ctx.guild, "invalid_automod_feature_param", prefix=self.bot.get_guild_prefix(ctx.guild), command="mentions <mentions>", off_command="mentions off")
                )
                await ctx.send(embed=e)
            else:
                if mentions < 4:
                    return await ctx.send(self.i18next.t(ctx.guild, "min_mentions", _emote="NO"))

                if mentions > 100:
                    return await ctx.send(self.i18next.t(ctx.guild, "max_mentions", _emote="NO"))

                automod = self.db.configs.get(ctx.guild.id, "automod")
                automod.update({
                    "mention": {"threshold": mentions}
                })
                self.db.configs.update(ctx.guild.id, "automod", automod)

                await ctx.send(self.i18next.t(ctx.guild, "mentions_set", _emote="YES", mentions=mentions))


    @automod.command()
    async def lines(
        self, 
        ctx,
        lines: str
    ):
        """lines_help"""
        lines = lines.lower()
        if lines == "off":
            automod = self.db.configs.get(ctx.guild.id, "automod")
            if "lines" in automod:
                del automod["lines"]
            self.db.configs.update(ctx.guild.id, "automod", automod)

            await ctx.send(self.i18next.t(ctx.guild, "automod_feature_disabled", _emote="YES", what="max-lines"))
        else:
            try:
                lines = int(lines)
            except ValueError:
                e = Embed(
                    title="Invalid paramater",
                    description=self.i18next.t(ctx.guild, "invalid_automod_feature_param", prefix=self.bot.get_guild_prefix(ctx.guild), command="lines <lines>", off_command="lines off")
                )
                await ctx.send(embed=e)
            else:
                if lines < 6:
                    return await ctx.send(self.i18next.t(ctx.guild, "min_lines", _emote="NO"))

                if lines > 150:
                    return await ctx.send(self.i18next.t(ctx.guild, "max_lines", _emote="NO"))

                automod = self.db.configs.get(ctx.guild.id, "automod")
                automod.update({
                    "lines": {"threshold": lines}
                })
                self.db.configs.update(ctx.guild.id, "automod", automod)

                await ctx.send(self.i18next.t(ctx.guild, "lines_set", _emote="YES", lines=lines))


    @automod.command()
    async def raid(
        self, 
        ctx,
        threshold: str
    ):
        """raid_help"""
        threshold = threshold.lower()
        automod = self.db.configs.get(ctx.guild.id, "automod")
        
        if threshold == "off":
            automod.update({
                "raid": {"status": False, "threshold": automod["raid"]["threshold"] if "raid" in automod else "100/100"}
            })
            self.db.configs.update(ctx.guild.id, "automod", automod)

            return await ctx.send(self.i18next.t(ctx.guild, "raid_off", _emote="YES"))
        
        elif len(threshold.split("/")) == 2 and re.match(r"^[-+]?[0-9]+$", threshold.split("/")[0]) is not None and re.match(r"^[-+]?[0-9]+$", threshold.split("/")[1]) is not None:
            if int(threshold.split("/")[0]) < 5 or int(threshold.split("/")[1]) < 5:
                return await ctx.send(self.i18next.t(ctx.guild, "threshold_too_low", _emote="NO"))

            automod.update({
                "raid": {"status": True, "threshold": f"{threshold}"}
            })
            self.db.configs.update(ctx.guild.id, "automod", automod)

            return await ctx.send(self.i18next.t(ctx.guild, "raid_on", _emote="YES", users=threshold.split("/")[0], seconds=threshold.split("/")[1]))

        else:
            prefix = self.bot.get_guild_prefix(ctx.guild)
            return await ctx.send(self.i18next.t(ctx.guild, "raid_help_2", _emote="BULB", prefix=prefix)) 


    # @automod.command()
    # async def spam(
    #     self, 
    #     ctx,
    #     warns: str
    # ):
    #     """spam_help"""
    #     warns = warns.lower()
    #     automod = self.db.configs.get(ctx.guild.id, "automod")
    #     if warns == "off":
    #         automod.update({
    #             "spam": {"status": False, "warns": 0}
    #         })
    #         self.db.configs.update(ctx.guild.id, "automod", automod)

    #         return await ctx.send(self.i18next.t(ctx.guild, "spam_off", _emote="YES"))

    #     elif warns.isnumeric():
    #         warns = int(warns)
    #         if warns < 1:
    #             return await ctx.send(self.i18next.t(ctx.guild, "min_warns", _emote="NO"))

    #         if warns > 100:
    #             return await ctx.send(self.i18next.t(ctx.guild, "max_warns", _emote="NO"))

    #         automod.update({
    #             "spam": {"status": True, "warns": warns}
    #         })
    #         self.db.configs.update(ctx.guild.id, "automod", automod)

    #         await ctx.send(self.i18next.t(ctx.guild, "warns_set", _emote="YES", warns=warns, what="they spam more than 10 messages within the last 10 seconds"))

    #     else:
    #         prefix = self.bot.get_guild_prefix(ctx.guild)
    #         return await ctx.send(self.i18next.t(ctx.guild, "spam_help_2", _emote="BULB", prefix=prefix))

    
    @commands.command()
    async def ignore(
        self, 
        ctx,
        role_or_channel: Union[discord.Role, discord.TextChannel] = None
    ):
        """ignore_help"""
        roles = self.db.configs.get(ctx.guild.id, "ignored_roles")
        channels = self.db.configs.get(ctx.guild.id, "ignored_channels")
        if role_or_channel is None:
            e = Embed()
            e.add_field(
                name="❯ Ignored Roles",
                value="\n".join(set([*[f"<@&{x.id}>" for x in sorted(ctx.guild.roles, key=lambda l: l.position) if x.position >= ctx.guild.me.top_role.position or x.permissions.ban_members]]))
            )
            
            channels = [f"<#{x}>" for x in sorted(channels)]
            if len(channels) > 0:
                e.add_field(
                    name="❯ Ignored Channels", 
                    value="\n".join(channels)
                )
            
            return await ctx.send(embed=e)

        cu = role_or_channel
        if cu.id in roles:
            return await ctx.send(self.db.configs.get(ctx.guild.id, "role_already_ignored", _emote="WARN"))

        if cu.id in channels:
            return await ctx.send(self.db.configs.get(ctx.guild.id, "channel_already_ignored", _emote="WARN"))
        
        if isinstance(cu, discord.Role):
            roles.append(cu.id)
            self.db.configs.update(ctx.guild.id, "ignored_roles", roles)
            return await ctx.send(self.i18next.t(ctx.guild, "role_ignored", _emote="YES", role=cu.name))
        elif isinstance(cu, discord.TextChannel):
            channels.append(cu.id)
            self.db.configs.update(ctx.guild.id, "ignored_channels", channels)
            return await ctx.send(self.i18next.t(ctx.guild, "channel_ignored", _emote="YES", channel=cu.name))


    @commands.command()
    async def unignore(
        self, 
        ctx,
        role_or_channel: Union[discord.Role, discord.TextChannel]
    ):
        """unignore_help"""
        cu = role_or_channel
        roles = self.db.configs.get(ctx.guild.id, "ignored_roles")
        channels = self.db.configs.get(ctx.guild.id, "ignored_channels")
        
        if isinstance(cu, discord.Role):
            if cu.id not in roles:
                return await ctx.send(self.i18next.t(ctx.guild, "role_not_ignored", _emote="NO"))
            roles.remove(cu.id)
            self.db.configs.update(ctx.guild.id, "ignored_roles", roles)
            return await ctx.send(self.i18next.t(ctx.guild, "role_unignored", _emote="YES", role=cu.name))
        elif isinstance(cu, discord.TextChannel):
            if cu.id not in channels:
                return await ctx.send(self.i18next.t(ctx.guild, "channel_not_ignored", _emote="NO"))
            channels.remove(cu.id)
            self.db.configs.update(ctx.guild.id, "ignored_channels", channels)
            return await ctx.send(self.i18next.t(ctx.guild, "channel_unignored", _emote="YES", channel=cu.name))

    
    @commands.command()
    async def raidmode(
        self,
        ctx,
        state,
        *,
        reason: Reason = None
    ):
        """raidmode_help"""
        state = state.lower()
        if state == "off":
            if ctx.guild.id not in self.raids:
                return await ctx.send(self.i18next.t(ctx.guild, "no_raid", _emote="NO"))
            else:
                await disableRaidMode(self, ctx.guild, ctx.author, reason)
                await ctx.send(self.i18next.t(ctx.guild, "disabled_raid", _emote="YES"))
        elif state == "on":
            if ctx.guild.id in self.raids:
                return await ctx.send(self.i18next.t(ctx.guild, "already_raid", _emote="NO"))
            else:
                await enableRaidMode(self, ctx.guild, ctx.author, reason)
                await ctx.send(self.i18next.t(ctx.guild, "enabled_raid", _emote="YES"))
        else:
            await ctx.send(self.i18next.t(ctx.guild, "invalid_raid_opt", _emote="WARN"))


    @commands.group()
    async def allowed_invites(
        self,
        ctx
    ):
        """allowed_invites_help"""
        if ctx.subcommand_passed is None:
            allowed = [x.strip().lower() for x in self.db.configs.get(ctx.guild.id, "whitelisted_invites")]
            prefix = self.bot.get_guild_prefix(ctx.guild)
            if len(allowed) < 1:
                return await ctx.send(self.i18next.t(ctx.guild, "no_whitelisted", _emote="NO", prefix=prefix))
            else:
                e = Embed()
                e.add_field(
                    name="❯ Allowed invites (by server ID)", 
                    value=" | ".join([f"``{x}``" for x in allowed])
                )
                await ctx.send(embed=e)

    
    @allowed_invites.command()
    async def add(
        self,
        ctx,
        guild_id: int
    ):
        """allowed_invites_add_help"""    
        allowed = [x.strip().lower() for x in self.db.configs.get(ctx.guild.id, "whitelisted_invites")]

        if str(guild_id) in allowed:
            return await ctx.send(self.i18next.t(ctx.guild, "already_whitelisted", _emote="WARN", server=guild_id))

        allowed.append(str(guild_id))
        self.db.configs.update(ctx.guild.id, "whitelisted_invites", allowed)

        await ctx.send(self.i18next.t(ctx.guild, "added_invite", _emote="YES", server=guild_id))


    @allowed_invites.command()
    async def remove(
        self,
        ctx,
        guild_id: int
    ): 
        """allowed_invites_remove_help"""
        allowed = [x.strip().lower() for x in self.db.configs.get(ctx.guild.id, "whitelisted_invites")]

        if str(guild_id) not in allowed:
            return await ctx.send(self.i18next.t(ctx.guild, "not_whitelisted", _emote="NO", server=guild_id))

        allowed.remove(str(guild_id))
        self.db.configs.update(ctx.guild.id, "whitelisted_invites", allowed)
        
        await ctx.send(self.i18next.t(ctx.guild, "removed_invite", _emote="YES", server=guild_id))



def setup(bot):
    bot.add_cog(AutomodPlugin(bot))