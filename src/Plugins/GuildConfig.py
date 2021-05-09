import asyncio
import traceback

import discord
from discord import TextChannel
from discord.ext import commands

from i18n import Translator
from Utils import Logging
from Utils.Constants import GREEN_TICK

from Plugins.Base import BasePlugin
from Database import Connector, DBUtils


db = Connector.Database()



class GuildConfig(BasePlugin):
    def __init__(self, bot):
        super().__init__(bot)

    
    async def cog_check(self, ctx):
        return ctx.author.guild_permissions.administrator


    @commands.guild_only()
    @commands.group(aliases=["configure"])
    async def config(self, ctx):
        "config_help"
        if ctx.subcommand_passed is None:
            enabled_modules, disabled_modules = DBUtils.get_module_config(ctx.guild.id)
            general, messages, members = await DBUtils.get_log_channels(self.bot, ctx.guild.id)
            welcome_channel, welcome_msg = await DBUtils.get_welcome_config(self.bot, ctx.guild.id)
            mute_role_id = DBUtils.get(db.configs, "guildId", f"{ctx.guild.id}", "muteRole")

            e = discord.Embed(
                color=discord.Color.blurple(),
                title="Server Config"
            )
            e.set_thumbnail(url=ctx.guild.icon_url)
            e.add_field(
                name=Translator.translate(ctx.guild, "log_channels"),
                value="```\n• Mod Actions: {} \n• Messages: {} \n• Join/Leave: {} \n```"\
                .format(general, messages, members),
                inline=False
            )
            e.add_field(
                name=Translator.translate(ctx.guild, "enabled_modules"),
                value="```\n{}\n```".format("\n".join(enabled_modules) if len(enabled_modules) > 0 else "None"),
                inline=False
            )
            e.add_field(
                name=Translator.translate(ctx.guild, "disabled_modules"),
                value="```\n{}\n```".format("\n".join(disabled_modules) if len(disabled_modules) > 0 else "None"),
                inline=False
            )
            e.add_field(
                name="Welcome System",
                value="```\n• Channel: {} \n• Message: {}\n```".format(welcome_channel, welcome_msg),
                inline=False
            )
            e.add_field(
                name="Mute Role",
                value="```\n{}\n```".format("@" + (discord.utils.get(ctx.guild.roles, id=int(mute_role_id))).name + f" ({mute_role_id})" if mute_role_id != "" else "Not set yet"),
                inline=False
            )
            await ctx.send(embed=e)


    @config.command()
    async def prefix(self, ctx, new_prefix: str = None):
        """prefix_help"""
        if new_prefix is None:
            await ctx.send(Translator.translate(ctx.guild, "current_prefix", prefix=DBUtils.get(db.configs, "guildId", f"{ctx.guild.id}", "prefix")))
        elif len(new_prefix) > 15:
            await ctx.send(Translator.translate(ctx.guild, "prefix_too_long", _emote="NO"))
        else:
            DBUtils.update(db.configs, "guildId", f"{ctx.guild.id}", "prefix", f"{new_prefix}")
            await ctx.send(Translator.translate(ctx.guild, "prefix_updated", _emote="YES", prefix=new_prefix))


    @config.command()
    async def mute_role(self, ctx, role: discord.Role):
        """mute_role_help"""
        if role == ctx.guild.default_role:
            return await ctx.send(Translator.translate(ctx.guild, "default_role_forbidden", _emote="NO"))
        guild: discord.Guild = ctx.guild
        perms = guild.me.guild_permissions
        if not perms.manage_roles:
            return await ctx.send(Translator.translate(ctx.guild, "mute_missing_perm", _emote="NO"))
        if not guild.me.top_role > role:
            return await ctx.send(Translator.translate(ctx.guild, "role_too_high"))
        DBUtils.update(db.configs, "guildId", f"{guild.id}", "muteRole", int(role.id))
        await ctx.send(Translator.translate(ctx.guild, "updated_mute_role", _emote="YES", role=role.mention))


    @commands.command()
    @commands.guild_only()
    async def action_log(self, ctx, channel: discord.TextChannel):
        """action_log_help"""
        DBUtils.update(db.configs, "guildId", f"{ctx.guild.id}", "memberLogChannel", int(channel.id))
        await ctx.send(Translator.translate(ctx.guild, "log_mod_actions", _emote="YES", channel=channel.mention))

    
    @config.command()
    async def dm_on_actions(self, ctx):
        """dm_on_actions_help"""
        state = DBUtils.get(db.configs, "guildId", f"{ctx.guild.id}", "dm_on_actions")
        state = not state
        if state is False:
            return Translator.translate(ctx.guild, "dm_on_actions_false", _emote="YES")
        else:
            return Translator.translate(ctx.guild, "dm_on_actions_true", _emote="YES")


    @config.group()
    async def allowed_invites(self, ctx):
        """allowed_invites_help"""
        if ctx.invoked_subcommand is None:
            allowed = [x.strip().lower() for x in DBUtils.get(db.configs, "guildId", f"{ctx.guild.id}", "whitelisted_invites")]
            prefix = DBUtils.get(db.configs, "guildId", f"{ctx.guild.id}", "prefix")
            if len(allowed) < 1:
                return await ctx.send(
                    embed=discord.Embed(
                        color=discord.Color.blurple(), 
                        title="Censor List", 
                        description="Currently all invites are blacklisted \n• Whitelist one by using ``{}config allowed_invites add <server>``".format(prefix)
                    )
                )
            else:
                e = discord.Embed(
                    color=discord.Color.blurple(),
                    title="Censor List",
                    description="Currently ``{}`` invites are whitelisted \n• Whitelist another one by using ``{}config allowed_invites add <server>``".format(len(allowed), prefix)
                )
                e.add_field(
                    name="Whitelisted Servers (By ID)",
                    value="```\n{}\n```".format("\n".join(allowed))
                )
                await ctx.send(embed=e)
    


    @allowed_invites.command(name="add")
    async def add_invite(self, ctx, server: int):
        """allowed_invites_add_help"""
        allowed = [str(x).strip().lower() for x in DBUtils.get(db.configs, "guildId", f"{ctx.guild.id}", "whitelisted_invites")]
        if str(server) in allowed:
            return await ctx.send(Translator.translate(ctx.guild, "already_whitelisted", _emote="NO", server=server))
        allowed.append(str(server))
        DBUtils.update(db.configs, "guildId", f"{ctx.guild.id}", "whitelisted_invites", allowed)
        await ctx.send(Translator.translate(ctx.guild, "added_invite", _emote="YES", server=server))

    
    @allowed_invites.command(name="remove")
    async def remove_invite(self, ctx, server: int):
        """allowed_invites_remove_help"""
        allowed = [str(x).strip().lower() for x in DBUtils.get(db.configs, "guildId", f"{ctx.guild.id}", "whitelisted_invites")]
        if str(server) not in allowed:
            return await ctx.send(Translator.translate(ctx.guild, "not_whitelisted", _emote="NO", server=server))
        allowed.remove(str(server))
        DBUtils.update(db.configs, "guildId", f"{ctx.guild.id}", "whitelisted_invites", allowed)
        await ctx.send(Translator.translate(ctx.guild, "removed_invite", _emote="YES", server=server))


    @config.command()
    async def welcome_msg(self, ctx, *, msg: str):
        """welcome_msg_help"""
        if len(msg) > 1500:
            return await ctx.send(Translator.translate(ctx.guild, "msg_too_long"))
        DBUtils.update(
            db.configs,
            "guildId",
            f"{ctx.guild.id}",
            "welcomeMessage",
            f"{msg}"
        )
        await ctx.send(Translator.translate(ctx.guild, "msg_success", _emote="YES"))


    @config.command()
    async def welcome_channel(self, ctx, channel: discord.TextChannel):
        """welcome_channel_help"""
        DBUtils.update(
            db.configs,
            "guildId",
            f"{ctx.guild.id}",
            "welcomeChannel",
            channel.id
        )
        await ctx.send(Translator.translate(ctx.guild, "channel_success", _emote="YES", channel=channel.mention))

    @config.command()
    async def welcome_off(self, ctx):
        """welcome_off_help"""
        DBUtils.update(
            db.configs,
            "guildId",
            f"{ctx.guild.id}",
            "welcomeChannel",
            ""
        )
        DBUtils.update(
            db.configs,
            "guildId",
            f"{ctx.guild.id}",
            "welcomeMessage",
            ""
        )
        await ctx.send(Translator.translate(ctx.guild, "off_success", _emote="YES"))



    
    @config.group()
    async def enable(self, ctx):
        """enable_help"""
        if ctx.invoked_subcommand is None:
            normal = [f'{ctx.prefix}config enable {x}' for x in ["automod", "lvlsystem", "antispam"]]
            with_arg = [f'{ctx.prefix}config enable {x} <channel>' for x in ["message_logging", "member_logging"]]
            to_send = [*normal, *with_arg]
            await ctx.send("**Valid modules** \n```\n{}\n```".format("\n".join(to_send)))


    @enable.command()
    async def message_logging(self, ctx, channel: discord.TextChannel):
        """message_logging_help"""
        DBUtils.update(db.configs, "guildId", f"{ctx.guild.id}", "messageLogChannel", int(channel.id))
        DBUtils.update(db.configs, "guildId", f"{ctx.guild.id}", "messageLogging", True)
        await ctx.send(Translator.translate(ctx.guild, "enabled_module_channel", _emote="YES", module="message_logging", channel=channel.mention))


    @enable.command()
    async def member_logging(self, ctx, channel: discord.TextChannel):
        """member_logging_help"""
        DBUtils.update(db.configs, "guildId", f"{ctx.guild.id}", "joinLogChannel", int(channel.id))
        DBUtils.update(db.configs, "guildId", f"{ctx.guild.id}", "memberLogging", True)
        await ctx.send(Translator.translate(ctx.guild, "enabled_module_channel", _emote="YES", module="join_leave_logging", channel=channel.mention))

    
    @enable.command()
    async def automod(self, ctx):
        """automod_help"""
        DBUtils.update(db.configs, "guildId", f"{ctx.guild.id}", "automod", True)
        await ctx.send(Translator.translate(ctx.guild, "enabled_module_no_channel", _emote="YES", module="automod"))


    @enable.command()
    async def antispam(self, ctx):
        """antispam_help"""
        DBUtils.update(db.configs, "guildId", f"{ctx.guild.id}", "antispam", True)
        await ctx.send(Translator.translate(ctx.guild, "enabled_module_no_channel", _emote="YES", module="antispam"))

    
    @enable.command()
    async def lvlsystem(self, ctx):
        """lvlsystem_help"""
        DBUtils.update(db.configs, "guildId", f"{ctx.guild.id}", "lvlsystem", True)
        await ctx.send(Translator.translate(ctx.guild, "enabled_module_no_channel", _emote="YES", module="rank_system"))




    @config.group()
    async def disable(self, ctx):
        """disable_help"""
        if ctx.invoked_subcommand is None:
            modules = [f'{ctx.prefix}config disable {x}' for x in ["automod", "lvlsystem", "message_logging", "member_logging"]]
            await ctx.send("**Valid Modules** \n```\n{}\n```".format("\n".join(modules)))


    @disable.command(name="message_logging")
    async def _message_logging(self, ctx):
        """message_logging_help"""
        DBUtils.update(db.configs, "guildId", f"{ctx.guild.id}", "messageLogging", False)
        await ctx.send(Translator.translate(ctx.guild, "disabled_module", _emote="YES", module="message_logging"))


    @disable.command(name="member_logging")
    async def _member_logging(self, ctx):
        """member_logging_help"""
        DBUtils.update(db.configs, "guildId", f"{ctx.guild.id}", "memberLogging", False)
        await ctx.send(Translator.translate(ctx.guild, "disabled_module", _emote="YES", module="join_leave_logging"))    


    @disable.command(name="automod")
    async def _automod(self, ctx):
        """automod_help"""
        DBUtils.update(db.configs, "guildId", f"{ctx.guild.id}", "automod", False)
        await ctx.send(Translator.translate(ctx.guild, "disabled_module", _emote="YES", module="automod"))

    
    @disable.command(name="antispam")
    async def _antispam(self, ctx):
        """antispam_help"""
        DBUtils.update(db.configs, "guildId", f"{ctx.guild.id}", "antispam", False)
        await ctx.send(Translator.translate(ctx.guild, "disabled_module", _emote="YES", module="antispam"))

    
    @disable.command(name="lvlsystem")
    async def _lvlsystem(self, ctx):
        """lvlsystem_help"""
        DBUtils.update(db.configs, "guildId", f"{ctx.guild.id}", "lvlsystem", False)
        await ctx.send(Translator.translate(ctx.guild, "disabled_module", _emote="YES", module="rank_system"))


    @config.group()
    async def ignored_users(self, ctx):
        """ignored_users_help"""
        if ctx.invoked_subcommand is None:
            ignored_users = []
            for x in DBUtils.get(db.configs, "guildId", f"{ctx.guild.id}", "ignored_users"):
                ignored_users.append(str(x))
            ignored_users = [f"• {x}" for x in ignored_users]
            if len(ignored_users) < 1:
                ignored_users.append(Translator.translate(ctx.guild, "no_ignored_users"))
            e = discord.Embed(
                color=discord.Color.blurple(),
                title=Translator.translate(ctx.guild, "ignored_users"),
                description="```\n{}\n```".format("\n".join(ignored_users))
            )
            await ctx.send(embed=e)


    @ignored_users.command(name="add")
    async def _add(self, ctx, member: discord.Member):
        """ignored_users_add_help"""
        ignored_users = DBUtils.get(db.configs, "guildId", f"{ctx.guild.id}", "ignored_users")
        if member.id in ignored_users:
            return await ctx.send(Translator.translate(ctx.guild, "already_ignored_user", _emote="YES", user=member.name))
        ignored_users.append(int(member.id))
        DBUtils.update(db.configs, "guildId", f"{ctx.guild.id}", "ignored_users", ignored_users)
        await ctx.send(Translator.translate(ctx.guild, "ignored_user_added", _emote="YES", user=member.name))


    @ignored_users.command(name="remove")
    async def _remove(self, ctx, user: discord.User):
        """ignored_users_remove_help"""
        ignored_users = DBUtils.get(db.configs, "guildId", f"{ctx.guild.id}", "ignored_users")
        if not user.id in ignored_users:
            return await ctx.send(Translator.translate(ctx.guild, "not_existing_ignored_user", _emote="NO", user=user.name))
        ignored_users.remove(int(user.id))
        DBUtils.update(db.configs, "guildId", f"{ctx.guild.id}", "ignored_users", ignored_users)
        await ctx.send(Translator.translate(ctx.guild, "ignored_user_removed", _emote="YES", user=user.name))



    @config.group(aliases=["censor_list"])
    async def black_list(self, ctx):
        """black_list_help"""
        if ctx.invoked_subcommand is None:
            if DBUtils.get(db.configs, "guildId", f"{ctx.guild.id}", "automod") is False:
                return await ctx.send(Translator.translate(ctx.guild, "black_list_disabled", _emote="NO", prefix=ctx.prefix))
            _censor_list = [x.strip().lower() for x in DBUtils.get(db.configs, "guildId", f"{ctx.guild.id}", "censored_words") if x != "--------------"]
            if len(_censor_list) < 1:
                    return ctx.send(Translator.translate(ctx.guild, "black_list_empty", _emote="NO", prefix=ctx.prefix))
            words = "\n".join(_censor_list)
            e = discord.Embed(color=discord.Color.blurple(), title="Censor List", description="• Add a phrase: ``{}config black_list add <phrase>`` \n• Remove a phrase: ``{}config black_list remove <phrase>``".format(ctx.prefix, ctx.prefix))
            e.add_field(
                name="Phrases",
                value="```\n{}\n```".format(words),
                inline=False
            )
            await ctx.send(embed=e)


    @black_list.command(name="add")
    async def add_to_censor_list(self, ctx, *, text: str):
        """black_list_add_help"""
        if DBUtils.get(db.configs, "guildId", f"{ctx.guild.id}", "automod") is False:
            return await ctx.send(Translator.translate(ctx.guild, "black_list_disabled", _emote="NO", prefix=ctx.prefix))
        _censor_list = [x for x in DBUtils.get(db.configs, "guildId", f"{ctx.guild.id}", "censored_words") if x != "--------------"]
        if text.lower() in [x.strip().lower() for x in DBUtils.get(db.configs, "guildId", f"{ctx.guild.id}", "censored_words") if x != "--------------"]:
            return await ctx.send(Translator.translate(ctx.guild, "already_on_black_list", _emote="NO", word=text))
        _censor_list.append(str(text))
        DBUtils.update(db.configs, "guildId", f"{ctx.guild.id}", "censored_words", _censor_list)
        await ctx.send(Translator.translate(ctx.guild, "added_to_black_list", _emote="YES", word=text))


    @black_list.command(name="remove")
    async def remove_from_censor_list(self, ctx, *, text: str):
        """black_list_remove_help"""
        if DBUtils.get(db.configs, "guildId", f"{ctx.guild.id}", "automod") is False:
            return await ctx.send(Translator.translate(ctx.guild, "black_list_disabled", _emote="NO", prefix=ctx.prefix))
        
        lower = [x.lower() for x in DBUtils.get(db.configs, "guildId", f"{ctx.guild.id}", "censored_words") if x != "--------------"]
        if len(lower) < 1:
            return await ctx.send(Translator.translate(ctx.guild, "black_list_empty", _emote="NO", prefix=ctx.prefix))

        _censor_list = [x.strip().lower() for x in DBUtils.get(db.configs, "guildId", f"{ctx.guild.id}", "censored_words")]
        if not text.lower() in _censor_list:
            return await ctx.send(Translator.translate(ctx.guild, "not_on_black_list", _emote="NO", word=text))
        _censor_list.remove(str(text.lower()))
        DBUtils.update(db.configs, "guildId", f"{ctx.guild.id}", "censored_words", _censor_list)
        await ctx.send(Translator.translate(ctx.guild, "removed_from_black_list", _emote="YES", word=text))



def setup(bot):
    bot.add_cog(GuildConfig(bot))