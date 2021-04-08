import asyncio
import traceback

import discord
from discord import TextChannel
from discord.ext import commands

from i18n import Translator
from Utils import Logging
from Utils.Constants import GREEN_TICK

from Cogs.Base import BaseCog
from Database import Connector, DBUtils


db = Connector.Database()



class GuildConfig(BaseCog):
    def __init__(self, bot):
        super().__init__(bot)

    
    async def cog_check(self, ctx):
        return ctx.author.guild_permissions.administrator


    @commands.guild_only()
    @commands.group(aliases=["configure"])
    async def config(self, ctx):
        "config_help"
        prefix = DBUtils.get(db.configs, "guildId", f"{ctx.guild.id}", "prefix")
        if ctx.subcommand_passed is None:
            await ctx.invoke(self.bot.get_command("help"), query="config")


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


    # TODO: finish building this
    # @config.command()
    # async def max_pings(self, ctx, amount: int):
    #     """max_pings_help"""
    #     if amount < 3 or 50 < amount:
    #         return await ctx.send(Translator.translate(ctx.guild, "max_pings", _emote="NO"))

    #     DBUtils.update(
    #         db.configs,
    #         "guildId",
    #         f"{ctx.guild.id}",
    #         "max_pings",
    #         amount
    #     )
    #     await ctx.send(Translator.translate(ctx.guild, "set_max_pings", _emote="YES", amount=str(amount)))



    @commands.command()
    @commands.guild_only()
    async def action_log(self, ctx, channel: discord.TextChannel):
        """action_log_help"""
        DBUtils.update(db.configs, "guildId", f"{ctx.guild.id}", "memberLogChannel", int(channel.id))
        await ctx.send(Translator.translate(ctx.guild, "log_mod_actions", _emote="YES", channel=channel.mention))

    
    @config.group()
    async def enable(self, ctx):
        """enable_help"""
        if ctx.invoked_subcommand is None:
            await ctx.invoke(self.bot.get_command("help"), query="configuration_add")


    @enable.command()
    async def message_logging(self, ctx, channel: discord.TextChannel):
        DBUtils.update(db.configs, "guildId", f"{ctx.guild.id}", "messageLogChannel", int(channel.id))
        DBUtils.update(db.configs, "guildId", f"{ctx.guild.id}", "messageLogging", True)
        await ctx.send(Translator.translate(ctx.guild, "enabled_module_channel", _emote="YES", module="message_logging", channel=channel.mention))


    @enable.command()
    async def member_logging(self, ctx, channel: discord.TextChannel):
        DBUtils.update(db.configs, "guildId", f"{ctx.guild.id}", "joinLogChannel", int(channel.id))
        DBUtils.update(db.configs, "guildId", f"{ctx.guild.id}", "memberLogging", True)
        await ctx.send(Translator.translate(ctx.guild, "enabled_module_channel", _emote="YES", module="join_leave_logging", channel=channel.mention))

    
    @enable.command()
    async def automod(self, ctx):
        DBUtils.update(db.configs, "guildId", f"{ctx.guild.id}", "automod", True)
        await ctx.send(Translator.translate(ctx.guild, "enabled_module_no_channel", _emote="YES", module="automod"))

    
    @enable.command()
    async def lvlsystem(self, ctx):
        DBUtils.update(db.configs, "guildId", f"{ctx.guild.id}", "lvlsystem", True)
        await ctx.send(Translator.translate(ctx.guild, "enabled_module_no_channel", _emote="YES", module="rank_system"))




    @config.group()
    async def disable(self, ctx):
        """disable_help"""
        if ctx.invoked_subcommand is None:
            await ctx.invoke(self.bot.get_command("help"), query="log_remove")


    @disable.command(name="message_logging")
    async def _message_logging(self, ctx):
        DBUtils.update(db.configs, "guildId", f"{ctx.guild.id}", "messageLogging", False)
        await ctx.send(Translator.translate(ctx.guild, "disabled_module", _emote="YES", module="message_logging"))


    @disable.command(name="member_logging")
    async def _member_logging(self, ctx):
        DBUtils.update(db.configs, "guildId", f"{ctx.guild.id}", "memberLogging", False)
        await ctx.send(Translator.translate(ctx.guild, "disabled_module", _emote="YES", module="join_leave_logging"))    


    @disable.command(name="automod")
    async def _automod(self, ctx):
        DBUtils.update(db.configs, "guildId", f"{ctx.guild.id}", "automod", False)
        await ctx.send(Translator.translate(ctx.guild, "disabled_module", _emote="YES", module="automod"))

    
    @disable.command(name="lvlsystem")
    async def _lvlsystem(self, ctx):
        DBUtils.update(db.configs, "guildId", f"{ctx.guild.id}", "lvlsystem", False)
        await ctx.send(Translator.translate(ctx.guild, "disabled_module", _emote="YES", module="rank_system"))


    @config.group()
    async def ignored_users(self, ctx):
        """ignored_users_help"""
        try:
            if ctx.invoked_subcommand is None:
                ignored_users = []
                for x in DBUtils.get(db.configs, "guildId", f"{ctx.guild.id}", "ignored_users"):
                    ignored_users.append(str(x))
                if len(ignored_users) < 1:
                    ignored_users.append(Translator.translate(ctx.guild, "no_ignored_users"))
                e = discord.Embed(
                    color=discord.Color.blurple(),
                    title=Translator.translate(ctx.guild, "ignored_users", guild_name=ctx.guild.name),
                    description="\n".join(ignored_users)
                )
                e.set_thumbnail(url=ctx.guild.icon_url)
                return await ctx.send(embed=e)
        except Exception:
            pass


    @ignored_users.command(name="add")
    async def _add(self, ctx, member: discord.Member):
        ignored_users = DBUtils.get(db.configs, "guildId", f"{ctx.guild.id}", "ignored_users")
        if member.id in ignored_users:
            return await ctx.send(Translator.translate(ctx.guild, "already_ignored_user", _emote="YES", user=member.name))
        ignored_users.append(int(member.id))
        DBUtils.update(db.configs, "guildId", f"{ctx.guild.id}", "ignored_users", ignored_users)
        await ctx.send(Translator.translate(ctx.guild, "ignored_user_added", _emote="YES", user=member.name))


    @ignored_users.command(name="remove")
    async def _remove(self, ctx, user: discord.User):
        ignored_users = DBUtils.get(db.configs, "guildId", f"{ctx.guild.id}", "ignored_users")
        if not user.id in ignored_users:
            return await ctx.send(Translator.translate(ctx.guild, "not_existing_ignored_user", _emote="NO", user=user.name))
        ignored_users.remove(int(user.id))
        DBUtils.update(db.configs, "guildId", f"{ctx.guild.id}", "ignored_users", ignored_users)
        await ctx.send(Translator.translate(ctx.guild, "ignored_user_removed", _emote="YES", user=user.name))



    @config.command()
    async def show(self, ctx):
        """show_help"""
        try:
            enabled_modules, disabled_modules = DBUtils.get_module_config(ctx.guild.id)
            general, messages, members = DBUtils.get_log_channels(ctx.guild.id)

            e = discord.Embed(
                color=discord.Color.blurple(),
                title="Configuration for {}".format(ctx.guild.name)
            )
            e.set_thumbnail(url=ctx.guild.icon_url)
            e.add_field(
                name=Translator.translate(ctx.guild, "log_channels"),
                value=Translator.translate(ctx.guild, "log_actions", general=general, messages=messages, members=members),
                inline=False
            )
            e.add_field(
                name=Translator.translate(ctx.guild, "enabled_modules"),
                value=", ".join(enabled_modules if len(enabled_modules) > 0 else ["None"]),
                inline=False
            )
            e.add_field(
                name=Translator.translate(ctx.guild, "disabled_modules"),
                value=", ".join(disabled_modules if len(disabled_modules) > 0 else ["None"]),
                inline=False
            )
            await ctx.send(embed=e)
        except Exception:
            pass


    @config.group(aliases=["censor_list"])
    async def black_list(self, ctx):
        """black_list_help"""
        if ctx.invoked_subcommand is None:
            if DBUtils.get(db.configs, "guildId", f"{ctx.guild.id}", "automod") is False:
                return await ctx.send(Translator.translate(ctx.guild, "black_list_disabled", _emote="NO", prefix=ctx.prefix))
            _censor_list = [x.strip().lower() for x in DBUtils.get(db.configs, "guildId", f"{ctx.guild.id}", "censored_words") if x != "--------------"]
            if len(_censor_list) < 1:
                    return ctx.send(Translator.translate(ctx.guild, "black_list_empty", _emote="NO", prefix=ctx.prefix))
            await ctx.send(Translator.translate(ctx.guild, "censor_list", guild_name=ctx.guild.name, words=_censor_list))


    @black_list.command(name="add")
    async def add_to_censor_list(self, ctx, *, text: str):
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