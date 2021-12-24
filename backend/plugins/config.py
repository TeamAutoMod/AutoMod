import discord
from discord.ext import commands

import logging; log = logging.getLogger()
from toolbox import S

from . import AutoModPlugin
from ..types import Embed, Duration



class ConfigPlugin(AutoModPlugin):
    """Plugin for all configuration commands"""
    def __init__(self, bot):
        super().__init__(bot)


    def cog_check(self, ctx):
        return ctx.author.guild_permissions.manage_guild


    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def config(self, ctx):
        config = S(self.db.configs.get_doc(ctx.guild.id))
        y = self.bot.emotes.get("YES")
        n = self.bot.emotes.get("NO")

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
                    y if ctx.guild.me.guild_permissions.timeout_members == True else n,
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
                ]) if len(config.punishments.items()) > 0 else n
            }
        ])
        await ctx.send(embed=e)


    @commands.command()
    async def punishment(self, ctx, warns: int, action: str, time: Duration = None):
        """punishment_help"""
        action = action.lower(); 
        if not action in [""]: return await ctx.send(self.locale.t(ctx.guild, "invalid_action", _emote="NO"))

        if warns < 1: return await ctx.send(self.locale.t(ctx.guild, "min_warns", _emote="NO"))
        if warns > 100: return await ctx.send(self.locale.t(ctx.guild, "max_warns", _emote="NO"))



def setup(bot): bot.register_plugin(ConfigPlugin(bot))