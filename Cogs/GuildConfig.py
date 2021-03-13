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
    async def prefix(self, ctx, new_prefix: str = None):
        """prefix_help"""
        if new_prefix is None:
            await ctx.send(Translator.translate(ctx.guild, "current_prefix", prefix=DBUtils.get(db.configs, "guildId", f"{ctx.guild.id}", "prefix")))
        elif len(new_prefix) > 15:
            await ctx.send(Translator.translate(ctx.guild, "prefix_too_long"))
        else:
            DBUtils.update(db.configs, "guildId", f"{ctx.guild.id}", "prefix", f"{new_prefix}")
            await ctx.send(Translator.translate(ctx.guild, "prefix_updated", prefix=new_prefix))
    

    @config.command()
    async def mute_role(self, ctx, role: discord.Role):
        """mute_role_help"""
        if role == ctx.guild.default_role:
            return await ctx.send(Translator.translate(ctx.guild, "default_role_forbidden"))
        guild: discord.Guild = ctx.guild
        perms = guild.me.guild_permissions
        if not perms.manage_roles:
            return await ctx.send(Translator.translate(ctx.guild, "mute_missing_perm"))
        if not guild.me.top_role > role:
            return await ctx.send(Translator.translate(ctx.guild, "role_too_high"))
        DBUtils.update(db.configs, "guildId", f"{guild.id}", "muteRole", int(role.id))
        await ctx.send(Translator.translate(ctx.guild, "updated_mute_role", role=role.mention))


    @commands.command()
    @commands.guild_only()
    async def action_log(self, ctx, channel: discord.TextChannel):
        """action_log_help"""
        DBUtils.update(db.configs, "guildId", f"{ctx.guild.id}", "memberLogChannel", int(channel.id))
        await ctx.send(Translator.translate(ctx.guild, "log_mod_actions", channel=channel.mention))

    
    @config.group()
    async def enable(self, ctx):
        """enable_help"""
        if ctx.invoked_subcommand is None:
            await ctx.invoke(self.bot.get_command("help"), query="configuration_add")


    @enable.command()
    async def message_logging(self, ctx, channel: discord.TextChannel):
        DBUtils.update(db.configs, "guildId", f"{ctx.guild.id}", "messageLogChannel", int(channel.id))
        DBUtils.update(db.configs, "guildId", f"{ctx.guild.id}", "messageLogging", True)
        await ctx.send(Translator.translate(ctx.guild, "enabled_module_channel", module="message_logging", channel=channel.mention))


    @enable.command()
    async def member_logging(self, ctx, channel: discord.TextChannel):
        DBUtils.update(db.configs, "guildId", f"{ctx.guild.id}", "joinLogChannel", int(channel.id))
        DBUtils.update(db.configs, "guildId", f"{ctx.guild.id}", "memberLogging", True)
        await ctx.send(Translator.translate(ctx.guild, "enabled_module_channel", module="join_leave_logging", channel=channel.mention))

    
    @enable.command()
    async def automod(self, ctx):
        DBUtils.update(db.configs, "guildId", f"{ctx.guild.id}", "automod", True)
        await ctx.send(Translator.translate(ctx.guild, "enabled_module_no_channel", module="automod"))

    
    @enable.command()
    async def lvlsystem(self, ctx):
        DBUtils.update(db.configs, "guildId", f"{ctx.guild.id}", "lvlsystem", True)
        await ctx.send(Translator.translate(ctx.guild, "enabled_module_no_channel", module="rank_system"))




    @config.group()
    async def disable(self, ctx):
        """disable_help"""
        if ctx.invoked_subcommand is None:
            await ctx.invoke(self.bot.get_command("help"), query="log_remove")


    @disable.command(name="message_logging")
    async def _message_logging(self, ctx):
        DBUtils.update(db.configs, "guildId", f"{ctx.guild.id}", "messageLogging", False)
        await ctx.send(Translator.translate(ctx.guild, "disabled_module", module="message_logging"))


    @disable.command(name="member_logging")
    async def _member_logging(self, ctx):
        DBUtils.update(db.configs, "guildId", f"{ctx.guild.id}", "memberLogging", False)
        await ctx.send(Translator.translate(ctx.guild, "disabled_module", module="join_leave_logging"))    


    @disable.command(name="automod")
    async def _automod(self, ctx):
        DBUtils.update(db.configs, "guildId", f"{ctx.guild.id}", "automod", False)
        await ctx.send(Translator.translate(ctx.guild, "disabled_module", module="automod"))

    
    @disable.command(name="lvlsystem")
    async def _lvlsystem(self, ctx):
        DBUtils.update(db.configs, "guildId", f"{ctx.guild.id}", "lvlsystem", False)
        await ctx.send(Translator.translate(ctx.guild, "disabled_module", module="rank_system"))


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
                    title=Translator.translate(ctx.guild, "ignored_users", guild=ctx.guild.name),
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
            return await ctx.send(Translator.translate(ctx.guild, "already_ignored_user", user=member.name))
        ignored_users.append(int(member.id))
        DBUtils.update(db.configs, "guildId", f"{ctx.guild.id}", "ignored_users", ignored_users)
        await ctx.send(Translator.translate(ctx.guild, "ignored_user_added", user=member.name))


    @ignored_users.command(name="remove")
    async def _remove(self, ctx, user: discord.User):
        ignored_users = DBUtils.get(db.configs, "guildId", f"{ctx.guild.id}", "ignored_users")
        if not user.id in ignored_users:
            return await ctx.send(Translator.translate(ctx.guild, "not_existing_ignored_user", user=user.name))
        ignored_users.remove(int(user.id))
        DBUtils.update(db.configs, "guildId", f"{ctx.guild.id}", "ignored_users", ignored_users)
        await ctx.send(Translator.translate(ctx.guild, "ignored_user_removed", user=user.name))



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
                return await ctx.send(Translator.translate(ctx.guild, "black_list_disabled", prefix=ctx.prefix))
            _censor_list = [x.strip().lower() for x in DBUtils.get(db.configs, "guildId", f"{ctx.guild.id}", "censored_words") if x != "--------------"]
            if len(_censor_list) < 1:
                    return ctx.send(Translator.translate(ctx.guild, "black_list_empty", prefix=ctx.prefix))
            await ctx.send(Translator.translate(ctx.guild, "censor_list", guild=ctx.guild.name, words=_censor_list))


    @black_list.command(name="add")
    async def add_to_censor_list(self, ctx, *, text: str):
        if DBUtils.get(db.configs, "guildId", f"{ctx.guild.id}", "automod") is False:
            return await ctx.send(Translator.translate(ctx.guild, "black_list_disabled", prefix=ctx.prefix))
        _censor_list = [x for x in DBUtils.get(db.configs, "guildId", f"{ctx.guild.id}", "censored_words") if x != "--------------"]
        if text.lower() in [x.strip().lower() for x in DBUtils.get(db.configs, "guildId", f"{ctx.guild.id}", "censored_words") if x != "--------------"]:
            return await ctx.send(Translator.translate(ctx.guild, "already_on_black_list", word=text))
        _censor_list.append(str(text))
        DBUtils.update(db.configs, "guildId", f"{ctx.guild.id}", "censored_words", _censor_list)
        await ctx.send(Translator.translate(ctx.guild, "added_to_black_list", word=text))


    @black_list.command(name="remove")
    async def remove_from_censor_list(self, ctx, *, text: str):
        if DBUtils.get(db.configs, "guildId", f"{ctx.guild.id}", "automod") is False:
            return await ctx.send(Translator.translate(ctx.guild, "black_list_disabled", prefix=ctx.prefix))
        
        lower = [x.lower() for x in DBUtils.get(db.configs, "guildId", f"{ctx.guild.id}", "censored_words") if x != "--------------"]
        if len(lower) < 1:
            return await ctx.send(Translator.translate(ctx.guild, "black_list_empty", prefix=ctx.prefix))

        _censor_list = [x.strip().lower() for x in DBUtils.get(db.configs, "guildId", f"{ctx.guild.id}", "censored_words")]
        if not text.lower() in _censor_list:
            return await ctx.send(Translator.translate(ctx.guild, "not_on_black_list", word=text))
        _censor_list.remove(str(text.lower()))
        DBUtils.update(db.configs, "guildId", f"{ctx.guild.id}", "censored_words", _censor_list)
        await ctx.send(Translator.translate(ctx.guild, "removed_from_black_list", word=text))



def setup(bot):
    bot.add_cog(GuildConfig(bot))