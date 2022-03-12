import discord
from discord.ext import commands

import logging; log = logging.getLogger()
from toolbox import S as Object
from typing import Union
import itertools

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
    }
}
AUTOMOD_RULES = {
    "mentions": {
        "int_field_name": "threshold",
        "i18n_key": "set_mentions",
        "i18n_type": "maximum mentions"
    },
    "links": {
        "int_field_name": "warns",
        "i18n_key": "set_links",
        "i18n_type": "link filtering"
    },
    "invites": {
        "int_field_name": "warns",
        "i18n_key": "set_invites",
        "i18n_type": "invite filtering"
    },
    "files": {
        "int_field_name": "warns",
        "i18n_key": "set_files",
        "i18n_type": "bad file detection"
    },
    "zalgo": {
        "int_field_name": "warns",
        "i18n_key": "set_zalgo",
        "i18n_type": "zalgo filtering"
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
        config = Object(self.db.configs.get_doc(ctx.guild.id))
        rules = config.automod
        y = self.bot.emotes.get("YES")
        n = self.bot.emotes.get("NO")

        mute_perm = n
        if (ctx.guild.me.guild_permissions.value & 0x10000000000) != 0x10000000000:
            if ctx.guild.me.guild_permissions.administrator == True: mute_perm = y

        e = Embed(
            title=f"Config for {ctx.guild.name}",
        )
        e.add_fields([
            {
                "name": "❯ General",
                "value": "> **• Prefix:** {} \n> **• Can mute:** {} \n> **• Filters:** {}"\
                .format(
                    config.prefix,
                    mute_perm,
                    len(config.filters)
                ),
                "inline": True
            },
            {
                "name": "❯ Logging",
                "value": "> **• Mod Log:** {} \n> **• Message Log:** {}\n> **• Server Log:** {}"\
                .format(
                    n if config.mod_log == "" else f"<#{config.mod_log}>",
                    n if config.message_log == "" else f"<#{config.message_log}>",
                    n if config.server_log == "" else f"<#{config.server_log}>"
                ),
                "inline": True
            },
            e.blank_field(True),
            {
                "name": "❯ Automod Rules",
                "value": "> **• Max Mentions:** {} \n> **• Links:** {} \n> **• Invites:** {} \n> **• Bad Files:** {} \n> **• Zalgo:** {}"\
                .format(
                    n if not hasattr(rules, "mentions") else f"{rules.mentions.threshold}",
                    n if not hasattr(rules, "links") else f"{rules.links.warns} warn{'' if rules.links.warns == 1 else 's'}",
                    n if not hasattr(rules, "invites") else f"{rules.invites.warns} warn{'' if rules.invites.warns == 1 else 's'}",
                    n if not hasattr(rules, "files") else f"{rules.files.warns} warn{'' if rules.files.warns == 1 else 's'}",
                    n if not hasattr(rules, "zalgo") else f"{rules.zalgo.warns} warn{'' if rules.zalgo.warns == 1 else 's'}",
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
        
        data = Object(LOG_OPTIONS[option])
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


    @commands.command()
    async def automod(self, ctx, rule = None, amount: Union[int, str] = None):
        """automod_help"""
        prefix = self.get_prefix(ctx.guild)
        if rule == None or amount == None:
            e = Embed(
                title="Automoderator Configuration",
                description=self.locale.t(ctx.guild, "automod_description", prefix=prefix)
            )
            e.add_field(
                name="❯ Commands",
                value=self.locale.t(ctx.guild, "automod_commands", prefix=prefix)
            )
            return await ctx.send(embed=e)
        
        rule = rule.lower()
        if not rule in AUTOMOD_RULES:
            return await ctx.send(self.locale.t(ctx.guild, "invalid_automod_rule", _emote="NO"))
        
        current = self.db.configs.get(ctx.guild.id, "automod")
        data = Object(AUTOMOD_RULES[rule])

        if isinstance(amount, str):
            if amount.lower() == "off":
                self.db.configs.update(ctx.guild.id, "automod", {k: v for k, v in current.items() if k != rule})
                return await ctx.send(self.locale.t(ctx.guild, "automod_off", _emote="YES", _type=data.i18n_type))
            else:
                return await ctx.send(self.locale.t(ctx.guild, "invalid_automod_amount", _emote="NO", prefix=prefix, rule=rule, field=data.i18n_type))
        else:
            if amount < 1: return await ctx.send(self.locale.t(ctx.guild, "min_warns", _emote="NO"))
            if amount > 100: return await ctx.send(self.locale.t(ctx.guild, "max_warns", _emote="NO"))

            current.update({
                rule: {
                    data.int_field_name: int(amount)
                }
            })
            self.db.configs.update(ctx.guild.id, "automod", current)
            await ctx.send(self.locale.t(ctx.guild, data.i18n_key, _emote="YES", amount=amount))


    @commands.group()
    async def allowed_invites(self, ctx):
        """allowed_invites_help"""
        if ctx.invoked_subcommand == None:
            allowed = [f"``{x.strip().lower()}``" for x in self.db.configs.get(ctx.guild.id, "allowed_invites")]
            if len(allowed) < 1:
                prefix = self.get_prefix(ctx.guild)
                return await ctx.send(self.locale.t(ctx.guild, "no_allowed", _emote="NO", prefix=prefix))
            
            e = Embed(
                title="Allowed invites (by server ID)",
                description=", ".join(allowed)
            )
            await ctx.send(embed=e)


    @allowed_invites.command(remove="add")
    async def add_inv(self, ctx, guild_id: int):
        """allowed_invites_add_help"""
        allowed = [x.strip().lower() for x in self.db.configs.get(ctx.guild.id, "allowed_invites")]

        if str(guild_id) in allowed:
            return await ctx.send(self.locale.t(ctx.guild, "alr_allowed", _emote="NO"))
        
        allowed.append(str(guild_id))
        self.db.configs.update(ctx.guild.id, "allowed_invites", allowed)

        await ctx.send(self.locale.t(ctx.guild, "allowed_inv", _emote="YES"))


    @allowed_invites.command(name="remove")
    async def remove_inv(self, ctx, guild_id: int):
        """allowed_invites_remove_help"""
        allowed = [x.strip().lower() for x in self.db.configs.get(ctx.guild.id, "allowed_invites")]

        if not str(guild_id) in allowed:
            return await ctx.send(self.locale.t(ctx.guild, "not_allowed", _emote="NO"))
        
        allowed.remove(str(guild_id))
        self.db.configs.update(ctx.guild.id, "allowed_invites", allowed)

        await ctx.send(self.locale.t(ctx.guild, "unallowed_inv", _emote="YES"))


    @commands.group(aliases=["links"])
    async def link_blacklist(self, ctx):
        """link_blacklist_help"""
        if ctx.invoked_subcommand == None:
            links = [f"``{x.strip().lower()}``" for x in self.db.configs.get(ctx.guild.id, "black_listed_links")]
            if len(links) < 1:
                prefix = self.get_prefix(ctx.guild)
                return await ctx.send(self.locale.t(ctx.guild, "no_links", _emote="NO", prefix=prefix))
            
            e = Embed(
                title="Allowed links",
                description=", ".join(links)
            )
            await ctx.send(embed=e)


    @link_blacklist.command(name="add")
    async def add_link(self, ctx, url: str):
        """link_blacklist_add_help"""
        url = url.lower()
        links = [x.strip().lower() for x in self.db.configs.get(ctx.guild.id, "black_listed_links")]

        if str(url) in links:
            return await ctx.send(self.locale.t(ctx.guild, "alr_link", _emote="NO"))
        
        links.append(url)
        self.db.configs.update(ctx.guild.id, "black_listed_links", links)

        await ctx.send(self.locale.t(ctx.guild, "allowed_link", _emote="YES"))


    @link_blacklist.command(name="remove")
    async def remove_link(self, ctx, url: str):
        """link_blacklist_remove_help"""
        url = url.lower()
        links = [x.strip().lower() for x in self.db.configs.get(ctx.guild.id, "black_listed_links")]

        if not str(url) in links:
            return await ctx.send(self.locale.t(ctx.guild, "not_link", _emote="NO"))
        
        links.remove(url)
        self.db.configs.update(ctx.guild.id, "black_listed_links", links)

        await ctx.send(self.locale.t(ctx.guild, "unallowed_link", _emote="YES"))


    @commands.group(name="filter", aliases=["filters"])
    async def _filter(self, ctx):
        """filter_help"""
        if ctx.invoked_subcommand == None:
            prefix = self.get_prefix(ctx.guild)
            e = Embed(
                title="How to use filters",
                description=f"• Adding a filter: ``{prefix}filter add <name> <warns> <words>`` \n• Deleting a filter: ``{prefix}filter remove <name>``"
            )
            e.add_field(
                name="❯ Arguments",
                value="``<name>`` - *Name of the filter* \n``<warns>`` - *Warns users get when using a word within the filter* \n``<words>`` - *Words contained in the filter, seperated by commas*"
            )
            e.add_field(
                name="❯ Wildcards",
                value="You can also use an astrix (``*``) as a wildcard. E.g. \nIf you set one of the words to be ``tes*``, then things like ``test`` or ``testtt`` would all be filtered."
            )
            e.add_field(
                name="❯ Example",
                value=f"``{prefix}filter add test_filter 1 oneword, two words, wildcar*``"
            )
            await ctx.send(embed=e)


    @_filter.command(name="add")
    async def add_filter(self, ctx, name, warns: int, *, words):
        """filter_add_help"""
        name = name.lower()
        filters = self.db.configs.get(ctx.guild.id, "filters")

        if len(name) > 30: return await ctx.send(self.locale.t(ctx.guild, "filter_name_too_long", _emote="NO"))
        if name in filters: return await ctx.send(self.locale.t(ctx.guild, "filter_exists", _emote="NO"))

        if warns < 1: return await ctx.send(self.locale.t(ctx.guild, "min_warns", _emote="NO"))
        if warns > 100: return await ctx.send(self.locale.t(ctx.guild, "max_warns", _emote="NO"))

        filters[name] = {
            "warns": warns,
            "words": words.split(", ")
        }
        self.db.configs.update(ctx.guild.id, "filters", filters)

        await ctx.send(self.locale.t(ctx.guild, "added_filter", _emote="YES"))

    
    @_filter.command(name="remove")
    async def remove_filter(self, ctx, name):
        """filter_remove_help"""
        name = name.lower()
        filters = self.db.configs.get(ctx.guild.id, "filters")

        if len(filters) < 1: return await ctx.send(self.locale.t(ctx.guild, "no_filters", _emote="NO"))
        if not name in filters: return await ctx.send(self.locale.t(ctx.guild, "no_filter", _emote="NO"))

        del filters[name]
        self.db.configs.update(ctx.guild.id, "filters", filters)

        await ctx.send(self.locale.t(ctx.guild, "removed_filter", _emote="YES"))


    @_filter.command()
    async def show(self, ctx):
        """filter_show_help"""
        filters = self.db.configs.get(ctx.guild.id, "filters")
        if len(filters) < 1: return await ctx.send(self.locale.t(ctx.guild, "no_filters", _emote="NO"))

        e = Embed(
            title="Filters"
        )
        for name in dict(itertools.islice(filters.items(), 10)):
            i = filters[name]
            e.add_field(
                name=f"❯ {name} ({i['warns']} {'warn' if int(i['warns']) == 1 else 'warns'})",
                value=", ".join([f"``{x}``" for x in i["words"]])
            )

            footer = f"And {len(filters)-len(dict(itertools.islice(filters.items(), 10)))} more filters" if len(filters) > 10 else None
            if footer != None: e.set_footer(text=footer)

        await ctx.send(embed=e)


def setup(bot): bot.register_plugin(ConfigPlugin(bot))
