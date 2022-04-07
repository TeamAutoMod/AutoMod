import discord
from discord.ext import commands

import logging; log = logging.getLogger()
from toolbox import S as Object
from typing import Union
import asyncio
import re

from . import AutoModPlugin
from ..types import Embed, Duration



LOG_OPTIONS = {
    "mod": {
        "db_field": "mod_log",
        "i18n_type": "moderation logs"
    },
    "server": {
        "db_field": "server_log",
        "i18n_type": "server logs"
    },
    "messages": {
        "db_field": "message_log",
        "i18n_type": "message logs"
    },
    "joins": {
        "db_field": "join_log",
        "i18n_type": "join logs"
    },
}


class ConfigPlugin(AutoModPlugin):
    """Plugin for all configuration commands"""
    def __init__(self, bot):
        super().__init__(bot)
        self.webhook_queue = []
        self.bot.loop.create_task(self.create_webhooks())


    async def create_webhooks(self):
        while True:
            await asyncio.sleep(1)
            if len(self.webhook_queue) > 0:
                for w in self.webhook_queue:
                    self.webhook_queue.remove(w)
                    await self.create_log_webhook(
                        w["ctx"],
                        w["option"],
                        w["channel"]
                    )


    async def create_log_webhook(self, ctx, option, channel):
        wid = self.bot.db.configs.get(ctx.guild.id, f"{option}_webhook")
        if wid != "":
            try:
                ow = await self.bot.fetch_webhook(int(wid))
            except Exception:
                pass
            else:
                await ow.delete()
            
        if ctx.guild.id in self.bot.webhook_cache:
            if self.bot.webhook_cache[ctx.guild.id][option] != None:
                try:
                    await (self.bot.webhook_cache[ctx.guild.id][option]).delete()
                except Exception:
                    pass
        
        try:
            w = await channel.create_webhook(
                name=ctx.bot.user.name,
                avatar=self.bot.avatar_as_bytes
            )
        except Exception:
            return
        else:
            self.bot.db.configs.update(ctx.guild.id, f"{option}_webhook", f"{w.id}")
            if not ctx.guild.id in self.bot.webhook_cache:
                self.bot.webhook_cache.update({
                    ctx.guild.id: {
                        **{
                            k: None for k in ["mod_log", "server_log", "message_log", "join_log"] if k != option
                        }, 
                        **{
                            option: w
                        }
                    }
                })
            else:
                if self.bot.webhook_cache[ctx.guild.id][option] == None:
                    self.bot.webhook_cache[ctx.guild.id][option] = w
                else:
                    if self.bot.webhook_cache[ctx.guild.id][option] != w.id:
                        self.bot.webhook_cache[ctx.guild.id][option] = w


    async def delete_webhook(self, ctx, option):
        if ctx.guild.id in self.bot.webhook_cache:
            if self.bot.webhook_cache[ctx.guild.id][option] != None:
                try:
                    await (self.bot.webhook_cache[ctx.guild.id][option]).delete()
                except Exception:
                    pass
                else:
                    return
                finally:
                    self.bot.webhook_cache[ctx.guild.id][option] = None

        wid = self.bot.db.configs.get(ctx.guild.id, f"{option}_webhook")
        if wid != "":
            try:
                ow = await self.bot.fetch_webhook(int(wid))
            except Exception:
                pass
            else:
                await ow.delete()


    @commands.command()
    @AutoModPlugin.can("manage_guild")
    async def config(self, ctx):
        """
        config_help
        examples:
        -config
        """
        config = Object(self.db.configs.get_doc(ctx.guild.id))
        rules = config.automod
        y = self.bot.emotes.get("YES")
        n = self.bot.emotes.get("NO")

        mute_perm = n
        if (ctx.guild.me.guild_permissions.value & 0x10000000000) != 0x10000000000:
            if ctx.guild.me.guild_permissions.administrator == True: 
                mute_perm = y
        else:
            mute_perm = y

        e = Embed(
            title=f"Config for {ctx.guild.name}",
        )
        e.add_fields([
            {
                "name": "❯ General",
                "value": "> **• Prefix:** {} \n> **• Can mute:** {} \n> **• Filters:** {} \n> **• Mod Role:** {}"\
                .format(
                    config.prefix,
                    mute_perm,
                    len(config.filters),
                    n if config.mod_role == "" else f"<@&{config.mod_role}>"
                ),
                "inline": True
            },
            {
                "name": "❯ Logging",
                "value": "> **• Mod Log:** {} \n> **• Message Log:** {}\n> **• Server Log:** {}\n> **• Join Log:** {}"\
                .format(
                    n if config.mod_log == "" else f"<#{config.mod_log}>",
                    n if config.message_log == "" else f"<#{config.message_log}>",
                    n if config.server_log == "" else f"<#{config.server_log}>",
                    n if config.join_log == "" else f"<#{config.join_log}>",
                ),
                "inline": True
            },
            e.blank_field(True),
            {
                "name": "❯ Automod Rules",
                "value": "> **• Max Mentions:** {} \n> **• Links:** {} \n> **• Invites:** {} \n> **• Bad Files:** {} \n> **• Zalgo:** {}"\
                .format(
                    n if not hasattr(rules, "mentions") else f"{rules.mentions.threshold}",
                    n if not hasattr(rules, "links") else f"{rules.links.warns} warn{'' if rules.links.warns == 1 else 's'}" if rules.links.warns > 0 else "delete message",
                    n if not hasattr(rules, "invites") else f"{rules.invites.warns} warn{'' if rules.invites.warns == 1 else 's'}" if rules.invites.warns > 0 else "delete message",
                    n if not hasattr(rules, "files") else f"{rules.files.warns} warn{'' if rules.files.warns == 1 else 's'}" if rules.files.warns > 0 else "delete message",
                    n if not hasattr(rules, "zalgo") else f"{rules.zalgo.warns} warn{'' if rules.zalgo.warns == 1 else 's'}" if rules.zalgo.warns > 0 else "delete message",
                ),
                "inline": True
            },
            {
                "name": "❯ Punishments",
                "value": "\n".join([
                    f"> **• {x} Warn{'' if int(x) == 1 else 's'}:** {y.capitalize() if len(y.split(' ')) == 1 else y.split(' ')[0].capitalize() + ' ' + y.split(' ')[-2] + y.split(' ')[-1]}" \
                    for x, y in config.punishments.items()
                ]) if len(config.punishments.items()) > 0 else n,
                "inline": True
            },
            e.blank_field(True)
        ])
        await ctx.send(embed=e)


    @commands.command()
    @AutoModPlugin.can("manage_guild")
    async def punishment(self, ctx, warns: int, action: str, time: Duration = None):
        """
        punishment_help
        examples:
        -punishment 3 kick
        -punishment 4 ban
        -punishment 2 mute 10m
        -punishment 5 none
        """
        action = action.lower()
        if not action in ["kick", "ban", "mute", "none"]: return await ctx.send(self.locale.t(ctx.guild, "invalid_action", _emote="NO"))

        if warns < 1: return await ctx.send(self.locale.t(ctx.guild, "min_warns", _emote="NO"))
        if warns > 100: return await ctx.send(self.locale.t(ctx.guild, "max_warns", _emote="NO"))

        current = self.db.configs.get(ctx.guild.id, "punishments")
        prefix = self.get_prefix(ctx.guild)
        text = ""

        if action == "none":
            current = {k: v for k, v in current.items() if str(k) != str(warns)}
            text = self.locale.t(ctx.guild, "set_none", _emote="YES", warns=warns, prefix=prefix)

        elif action != "mute":
            current.update({
                str(warns): action
            })
            text = self.locale.t(ctx.guild, f"set_{action}", _emote="YES", warns=warns, prefix=prefix)

        else:
            if time == None: return await ctx.send(self.locale.t(ctx.guild, "time_needed", _emote="NO"))

            sec = time.to_seconds(ctx)
            if sec > 0: 
                length, unit = time.length, time.unit
                current.update({
                    str(warns): f"mute {sec} {length} {unit}"
                })
                text = self.locale.t(ctx.guild, "set_mute", _emote="YES", warns=warns, length=length, unit=unit, prefix=prefix)
        
            else:
                raise commands.BadArgument("number_too_small")
        
        self.db.configs.update(ctx.guild.id, "punishments", current)
        await ctx.send(text)


    @commands.command(name="log")
    @AutoModPlugin.can("manage_guild")
    async def _log(self, ctx, option: str, channel: Union[discord.TextChannel, str]):
        """
        log_help
        examples:
        -log mod #mod-log
        -log joins 960832535867306044
        -log server off
        """
        option = option.lower()
        if not option in LOG_OPTIONS: 
            return await ctx.send(self.locale.t(ctx.guild, "invalid_log_option", _emote="NO"))
        
        data = Object(LOG_OPTIONS[option])
        if isinstance(channel, str):
            if channel.lower() == "off":
                self.db.configs.update(ctx.guild.id, data.db_field, "")
                await self.delete_webhook(
                    ctx,
                    data.db_field
                )

                return await ctx.send(self.locale.t(ctx.guild, "log_off", _emote="YES", _type=data.i18n_type))
            else:
                prefix = self.get_prefix(ctx.guild)
                return await ctx.send(self.locale.t(ctx.guild, "invalid_log_channel", _emote="NO", prefix=prefix, option=option))

        else:
            self.db.configs.update(ctx.guild.id, data.db_field, f"{channel.id}")
            self.webhook_queue.append({
                "ctx": ctx,
                "option": data.db_field,
                "channel": channel
            })

            await ctx.send(self.locale.t(ctx.guild, "log_on", _emote="YES", _type=data.i18n_type, channel=channel.mention))


    @commands.command()
    @AutoModPlugin.can("manage_guild")
    async def prefix(self, ctx, prefix: str):
        """
        prefix_help
        examples:
        -prefix !
        """
        if len(prefix) > 20: 
            return await ctx.send(self.locale.t(ctx.guild, "prefix_too_long", _emote="NO"))

        self.db.configs.update(ctx.guild.id, "prefix", prefix)
        await ctx.send(self.locale.t(ctx.guild, "prefix_updated", _emote="YES", prefix=prefix))


    @commands.command(aliases=["restrict"])
    @AutoModPlugin.can("manage_guild")
    async def disable(self, ctx, *, commands: str = None):
        """
        disable_help
        examples:
        -disable ping
        -disable ping help about
        """
        _disabled = self.db.configs.get(ctx.guild.id, "disabled_commands")

        if commands == None:
            if len(_disabled) < 1:
                return await ctx.send(self.locale.t(ctx.guild, "no_disabled_commands", _emote="NO"))
            else:
                e = Embed(
                    title="Disabled commands (mod-only)",
                    description=", ".join([f"``{x}``" for x in _disabled])
                )
                return await ctx.send(embed=e)

        commands = commands.split(" ")
        enabled = []
        disabled = []
        failed = []
        for cmd in commands:
            cmd = cmd.lower()
            if cmd in self.bot.all_commands:
                if not cmd in _disabled:
                    if len((self.bot.get_command(cmd)).checks) < 1:
                        _disabled.append(cmd); disabled.append(cmd)
                    else:
                        failed.append(cmd)
                else:
                    enabled.append(cmd)
                    _disabled.remove(cmd)
            else:
                failed.append(cmd)
        
        if (len(enabled) + len(disabled)) < 1: 
            return await ctx.send(self.locale.t(ctx.guild, "no_changes", _emote="NO"))
        
        self.db.configs.update(ctx.guild.id, "disabled_commands", disabled)
        e = Embed(
            title="Command config changes"
        )
        if len(disabled) > 0:
            e.add_field(
                name="❯ Disabled the following commands", 
                value=", ".join([f"``{x}``" for x in disabled])
            )
        if len(enabled) > 0:
            e.add_field(
                name="❯ Re-enabled the following commands",
                value=", ".join([f"``{x}``" for x in enabled]),
            )
        if len(failed) > 0:
            e.add_field(
                name="❯ Following commands are unknown or mod-commands",
                value=", ".join([f"``{x}``" for x in failed]),
            )
        
        await ctx.send(embed=e)


    @commands.command()
    @AutoModPlugin.can("manage_guild")
    async def mod_role(self, ctx, role: Union[discord.Role, str]):
        """
        mod_role_help
        examples:
        -mod_role Moderators
        -mod_role @Moderators
        -mod_role 793880854367043614
        """
        if isinstance(role, str):
            if role.lower() == "off":
                self.db.configs.update(ctx.guild.id, "mod_role", "")
                return await ctx.send(self.locale.t(ctx.guild, "mod_role_off", _emote="YES"))
            else:
                prefix = self.get_prefix(ctx.guild)
                return await ctx.send(self.locale.t(ctx.guild, "invalid_mod_role", _emote="NO", prefix=prefix))

        else:
            self.db.configs.update(ctx.guild.id, "mod_role", f"{role.id}")
            await ctx.send(self.locale.t(ctx.guild, "mod_role_on", _emote="YES", role=role.name))
            

async def setup(bot): await bot.register_plugin(ConfigPlugin(bot))