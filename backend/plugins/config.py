import discord
from discord.ext import commands

import logging; log = logging.getLogger()
from toolbox import S
from typing import Union

from . import AutoModPlugin
from ..types import Embed, Duration



LOG_OPTIONS = {
    "mod": {
        "db_field": "mod_log",
        "i18n_type": "moderation logs"
    },
    "voice": {
        "db_field": "voice_log",
        "i18n_type": "voice logs"
    },
    "server": {
        "db_field": "server_log",
        "i18n_type": "server logs"
    },
    "messages": {
        "db_field": "message_log",
        "i18n_type": "message logs"
    }
}
class ConfigPlugin(AutoModPlugin):
    """Plugin for all configuration commands"""
    def __init__(self, bot):
        super().__init__(bot)


    def cog_check(self, ctx):
        return ctx.author.guild_permissions.manage_guild


    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def config(self, ctx):
        """config_help"""
        config = S(self.db.configs.get_doc(ctx.guild.id))
        y = self.bot.emotes.get("YES")
        n = self.bot.emotes.get("NO")

        mute_perm = n
        if (ctx.guild.me.guild_permissions.value & 0x10000000000) != 0x10000000000:
            if ctx.guild.me.guild_permissions.administrator == True: mute_perm = y

        e = Embed(
            title=f"Config for {ctx.guild.name}",
        )
        e.set_thumbnail(url=ctx.guild.icon.url)
        e.add_fields([
            {
                "name": "❯ General",
                "value": "> **• Prefix:** {} \n> **• Starboard:** {} \n> **• Can mute:** {} \n> **• Filters:** {}"\
                .format(
                    config.prefix,
                    y if config.starboard == True else n,
                    mute_perm,
                    len(config.filters)
                ),
                "inline": True
            },
            {
                "name": "❯ Logging",
                "value": "> **• Mod Log:** {} \n> **• Message Log:** {}\n> **• Voice Log:** {} \n> **• Server Log:** {}"\
                .format(
                    n if config.mod_log == "" else f"<#{config.mod_log}>",
                    n if config.message_log == "" else f"<#{config.message_log}>",
                    n if config.voice_log == "" else f"<#{config.voice_log}>",
                    n if config.server_log == "" else f"<#{config.server_log}>"
                ),
                "inline": True
            },
            {
                "name": "❯ Automod Rules",
                "value": "> **• Max Mentions:** {} \n> **• Anti @every1:** {} \n> **• Anti Invites:** {} \n> **• Bad Files:** {} \n> **• Max Newlines:** {}"\
                .format(
                    n if not hasattr(config, "mention") else f"{config.mention.threshold} mentions",
                    n if not hasattr(config, "everyone") else f"{config.everyone.warns} warn{'' if config.everyone.warns == 1 else 's'}",
                    n if not hasattr(config, "invites") else f"{config.invites.warns} warn{'' if config.invites.warns == 1 else 's'}",
                    n if not hasattr(config, "files") else f"{config.files.warns} warn{'' if config.files.warns == 1 else 's'}",
                    n if not hasattr(config, "lines") else f"{config.mention.threshold} lines"
                )
            },
            {
                "name": "❯ Punishments",
                "value": "\n".join([
                    f"> **• {x} Warn {'' if x == 1 else ''}:** {y.capitalize() if len(y.split(' ')) == 1 else y.split(' ')[0].capitalize() + ' ' + y.split(' ')[-2] + y.split(' ')[-1]}" \
                    for x, y in config.punishments.items()
                ]) if len(config.punishments.items()) > 0 else n,
                "inline": True
            }
        ])
        await ctx.send(embed=e)


    @commands.command()
    async def punishment(self, ctx, warns: int, action: str, time: Duration = None):
        """punishment_help"""
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
    async def _log(self, ctx, option: str, channel: Union[discord.TextChannel, str]):
        """log_help"""
        option = option.lower()
        if not option in LOG_OPTIONS: 
            return await ctx.send(self.locale.t(ctx.guild, "invalid_log_option", _emote="NO"))
        
        data = S(LOG_OPTIONS[option])
        if isinstance(channel, str):
            if channel.lower() == "off":
                self.db.configs.update(ctx.guild.id, data.db_field, ""); 
                return await ctx.send(self.locale.t(ctx.guild, "log_off", _emote="YES", _type=data.i18n_type))
            else:
                prefix = self.get_prefix(ctx.guild)
                return await ctx.send(self.locale.t(ctx.guild, "invalid_log_channel", _emote="NO", prefix=prefix, option=option))
        else:
            self.db.configs.update(ctx.guild.id, data.db_field, f"{channel.id}")
            await ctx.send(self.locale.t(ctx.guild, "log_on", _emote="YES", _type=data.i18n_type, channel=channel.mention))


    @commands.command()
    async def prefix(self, ctx, prefix: str):
        """prefix_help"""
        if len(prefix) > 20: 
            return await ctx.send(self.locale.t(ctx.guild, "prefix_too_long", _emote="NO"))

        self.db.configs.update(ctx.guild.id, "prefix", prefix)
        await ctx.send(self.locale.t(ctx.guild, "prefix_updated", _emote="YES", prefix=prefix))


def setup(bot): bot.register_plugin(ConfigPlugin(bot))