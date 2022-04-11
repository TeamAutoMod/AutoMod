import discord
from discord.ext import commands

import re
import itertools
from typing import Union
from toolbox import S as Object
from urllib.parse import urlparse
import logging; log = logging.getLogger()

from . import AutoModPlugin
from .processor import ActionProcessor, LogProcessor, DMProcessor
from ..types import Embed



INVITE_RE = re.compile(
    r"(?:https?://)?(?:www\.)?(?:discord(?:\.| |\[?\(?\"?'?dot'?\"?\)?\]?)?(?:gg|io|me|li)|discord(?:app)?\.com/invite)/+((?:(?!https?)[\w\d-])+)"
)
LINK_RE = re.compile(
    r"((?:https?://)[a-z0-9]+(?:[-._][a-z0-9]+)*\.[a-z]{2,5}(?::[0-9]{1,5})?(?:/[^ \n<>]*)?)", 
    re.IGNORECASE
)
MENTION_RE = re.compile(
    r"<@[!&]?\\d+>"
)
ALLOWED_FILE_FORMATS = [
    # plain text/markdown
    "txt",
    "md",

    # image
    "jpg",
    "jpeg",
    "png",
    "webp",
    "gif",

    # video
    "mov",
    "mp4",
    "flv",
    "mkv",

    # audio
    "mp3",
    "wav",
    "m4a"
]
ZALGO = [
    u'\u030d',
    u'\u030e',
    u'\u0304',
    u'\u0305',
    u'\u033f',
    u'\u0311',
    u'\u0306',
    u'\u0310',
    u'\u0352',
    u'\u0357',
    u'\u0351',
    u'\u0307',
    u'\u0308',
    u'\u030a',
    u'\u0342',
    u'\u0343',
    u'\u0344',
    u'\u034a',
    u'\u034b',
    u'\u034c',
    u'\u0303',
    u'\u0302',
    u'\u030c',
    u'\u0350',
    u'\u0300',
    u'\u030b',
    u'\u030f',
    u'\u0312',
    u'\u0313',
    u'\u0314',
    u'\u033d',
    u'\u0309',
    u'\u0363',
    u'\u0364',
    u'\u0365',
    u'\u0366',
    u'\u0367',
    u'\u0368',
    u'\u0369',
    u'\u036a',
    u'\u036b',
    u'\u036c',
    u'\u036d',
    u'\u036e',
    u'\u036f',
    u'\u033e',
    u'\u035b',
    u'\u0346',
    u'\u031a',
    u'\u0315',
    u'\u031b',
    u'\u0340',
    u'\u0341',
    u'\u0358',
    u'\u0321',
    u'\u0322',
    u'\u0327',
    u'\u0328',
    u'\u0334',
    u'\u0335',
    u'\u0336',
    u'\u034f',
    u'\u035c',
    u'\u035d',
    u'\u035e',
    u'\u035f',
    u'\u0360',
    u'\u0362',
    u'\u0338',
    u'\u0337',
    u'\u0361',
    u'\u0489',
    u'\u0316',
    u'\u0317',
    u'\u0318',
    u'\u0319',
    u'\u031c',
    u'\u031d',
    u'\u031e',
    u'\u031f',
    u'\u0320',
    u'\u0324',
    u'\u0325',
    u'\u0326',
    u'\u0329',
    u'\u032a',
    u'\u032b',
    u'\u032c',
    u'\u032d',
    u'\u032e',
    u'\u032f',
    u'\u0330',
    u'\u0331',
    u'\u0332',
    u'\u0333',
    u'\u0339',
    u'\u033a',
    u'\u033b',
    u'\u033c',
    u'\u0345',
    u'\u0347',
    u'\u0348',
    u'\u0349',
    u'\u034d',
    u'\u034e',
    u'\u0353',
    u'\u0354',
    u'\u0355',
    u'\u0356',
    u'\u0359',
    u'\u035a',
    u'\u0323',
]
ZALGO_RE = re.compile(u'|'.join(ZALGO))


LOG_DATA = {
    "invites": {
        "rule": "Anti-Invites"
    },
    "links": {
        "rule": "Anti-Links"
    },
    "files": {
        "rule": "Anti-Files"
    },
    "zalgo": {
        "rule": "Anti-Zalgo"
    },
    "regex": {
        "rule": "Regex-Filter"
    },
    "filter": {
        "rule": "Word-Filter"
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


class AutomodPlugin(AutoModPlugin):
    """Plugin for enforcing automoderator rules"""
    def __init__(self, bot):
        super().__init__(bot)
        self.action_processor = ActionProcessor(bot)
        self.log_processor = LogProcessor(bot)
        self.dm_processor = DMProcessor(bot)


    def can_act(self, guild, mod, target):
        mod = guild.get_member(mod.id)
        target = guild.get_member(target.id)
        if mod == None or target == None: return False

        rid = self.bot.db.configs.get(guild.id, "mod_role")
        if rid != "":
            r = guild.get_role(int(rid))
            if r != None:
                if r in target.roles:
                    return False

        return mod.id != target.id \
            and target.id != guild.owner.id \
            and (target.guild_permissions.kick_members == False or target.guild_permissions.kick_members == False)


    def parse_filter(self, words):
        normal = []
        wildcards = []

        for i in words:
            i = i.replace("*", "", (i.count("*") - 1)) # remove multiple wildcards
            if i.endswith("*"):
                wildcards.append(i.replace("*", ".+"))
            else:
                normal.append(i)

        try:
            return re.compile(r"|".join([*normal, *wildcards]))
        except Exception:
            return None


    def parse_regex(self, regex):
        try:
            parsed = re.compile(regex)
        except Exception:
            return None
        else:
            return parsed


    def validate_regex(self, regex):
        try:
            re.compile(regex)
        except re.error:
            return False
        else:
            return True


    def safe_parse_url(self, url):
        url = url.lower()
        if not (
            url.startswith("https://") or
            url.startswith("http://")
        ):
            for x in ["www", "www5"]:
                url = url.replace(x, "")
        else:
            url = urlparse(url).hostname
        return url


    async def delete_msg(self, rule, found, msg, warns, reason, pattern_or_filter=None):
        try:
            await msg.delete()
        except (discord.NotFound, discord.Forbidden):
            pass
        else:
            self.bot.ignore_for_events.append(msg.id)
        finally:
            if warns > 0:
                await self.action_processor.execute(
                    msg, 
                    msg.guild.me,
                    msg.author,
                    warns, 
                    reason
                )
            else:
                data = Object(LOG_DATA[rule])

                self.dm_processor.execute(
                    msg,
                    "automod_rule_triggered",
                    msg.author,
                    **{
                        "guild_name": msg.guild.name,
                        "rule": data.rule,
                        "_emote": "SHIELD"
                    }
                )
                if rule not in ["filter", "regex"]:
                    await self.log_processor.execute(
                        msg.guild,
                        "automod_rule_triggered",
                        **{
                            "rule": data.rule,
                            "found": found,
                            "user_id": msg.author.id,
                            "user": msg.author,
                            "mod_id": msg.guild.me.id,
                            "mod": msg.guild.me
                        }
                    )
                else:
                    await self.log_processor.execute(
                        msg.guild,
                        f"{rule}_triggered",
                        **{
                            "pattern": f"{pattern_or_filter}",
                            "found": found,
                            "user_id": msg.author.id,
                            "user": msg.author,
                            "mod_id": msg.guild.me.id,
                            "mod": msg.guild.me
                        }
                    )


    async def enforce_rules(self, msg):
        content = msg.content.replace("\\", "")

        config = Object(self.db.configs.get_doc(msg.guild.id))
        rules = config.automod
        filters = config.filters
        regexes = config.regexes

        if len(rules) < 1: return

        if len(filters) > 0:
            for name in filters:
                f = filters[name]
                parsed = self.parse_filter(f["words"])
                if parsed != None:
                    found = parsed.findall(content)
                    if found:
                        return await self.delete_msg(
                            "filter",
                            ", ".join(found),
                            msg, 
                            int(f["warns"]), 
                            f"Triggered filter '{name}' with '{', '.join(found)}'",
                            name
                        )
        
        if len(regexes) > 0:
            for name, data in regexes.items():
                parsed = self.parse_regex(data["regex"])
                if parsed != None:
                    found = parsed.findall(content)
                    if found:
                        return await self.delete_msg(
                            "regex",
                            ", ".join(found),
                            msg, 
                            int(data["warns"]), 
                            f"Triggered regex '{name}' with '{', '.join(found)}'",
                            name
                        )
        
        if hasattr(rules, "invites"):
            found = INVITE_RE.findall(content)
            if found:
                for inv in found:
                    try:
                        invite: discord.Invite = await self.bot.fetch_invite(inv)
                    except discord.NotFound:
                        return await self.delete_msg(
                            "invites",
                            inv,
                            msg, 
                            rules.invites.warns, 
                            f"Advertising ({inv})"
                        )
                    if invite.guild == None:
                        return await self.delete_msg(
                            "invites",
                            inv,
                            msg, 
                            rules.invites.warns, 
                            f"Advertising ({inv})"
                        )
                    else:
                        if invite.guild == None \
                            or (
                                not invite.guild.id in config.allowed_invites \
                                and invite.guild.id != msg.guild.id
                            ):
                                return await self.delete_msg(
                                    "invites",
                                    inv,
                                    msg, 
                                    rules.invites.warns, 
                                    f"Advertising ({inv})"
                                )
        
        if hasattr(rules, "links"):
            found = LINK_RE.findall(content)
            if found:
                for link in found:
                    url = urlparse(link)
                    if url.hostname in config.black_listed_links:
                        return await self.delete_msg(
                            "links", 
                            url.hostname,
                            msg, 
                            rules.links.warns, 
                            f"Forbidden link ({url.hostname})"
                        )
                    else:
                        if not url.hostname in config.white_listed_links:
                            return await self.delete_msg(
                                "links", 
                                url.hostname,
                                msg, 
                                rules.links.warns, 
                                f"Forbidden link ({url.hostname})"
                            )

        if hasattr(rules, "files"):
            if len(msg.attachments) > 0:
                try:
                    forbidden = [
                        x.url.split(".")[-1] for x in msg.attachments \
                        if not x.url.split(".")[-1].lower() in ALLOWED_FILE_FORMATS
                    ]
                except Exception:
                    forbidden = []
                if len(forbidden) > 0:
                    return await self.delete_msg(
                        "files", 
                        ", ".join(forbidden), 
                        msg, 
                        rules.files.warns, 
                        f"Forbidden attachment type ({', '.join(forbidden)})"
                    )

        if hasattr(rules, "zalgo"):
            found = ZALGO_RE.search(content)
            if found:
                return await self.delete_msg(
                    "zalgo", 
                    found, 
                    msg, 
                    rules.zalgo.warns, 
                    "Zalgo found"
                )

        if hasattr(rules, "mentions"):
            found = len(MENTION_RE.findall(content))
            if found >= rules.mentions.threshold:
                return await self.delete_msg(
                    "mentions", 
                    found, 
                    msg, 
                    abs(rules.mentions.threshold - found), 
                    f"Spamming mentions ({found})"
                )
    

    @AutoModPlugin.listener()
    async def on_message(self, msg: discord.Message):
        if msg.guild == None: return
        if not msg.guild.chunked: await msg.guild.chunk(cache=True)
        if not self.can_act(msg.guild, msg.guild.me, msg.author): return

        await self.enforce_rules(msg)


    @AutoModPlugin.listener()
    async def on_message_edit(self, _, msg: discord.Message):
        if msg.guild == None: return
        if not msg.guild.chunked: await msg.guild.chunk(cache=True)
        if not self.can_act(msg.guild, msg.guild.me, msg.author): return

        await self.enforce_rules(msg)


    @commands.command()
    @AutoModPlugin.can("manage_guild")
    async def automod(self, ctx, rule = None, amount: Union[int, str] = None):
        """
        automod_help
        examples:
        -automod invites 1
        -automod mentions 10
        -automod files 0
        -automod links off
        """
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
            if rule == "mentions":
                if amount < 8: return await ctx.send(self.locale.t(ctx.guild, "min_mentions", _emote="NO"))
                if amount > 100: return await ctx.send(self.locale.t(ctx.guild, "max_mentions", _emote="NO"))
            else:
                if amount < 0: return await ctx.send(self.locale.t(ctx.guild, "min_warns_esp", _emote="NO"))
                if amount > 100: return await ctx.send(self.locale.t(ctx.guild, "max_warns", _emote="NO"))

            current.update({
                rule: {
                    data.int_field_name: int(amount)
                }
            })
            self.db.configs.update(ctx.guild.id, "automod", current)

            text = ""
            if rule != "mentions" and amount == 0:
                text = self.locale.t(ctx.guild, f"{data.i18n_key}_zero", _emote="YES")
            else:
                text = self.locale.t(ctx.guild, data.i18n_key, _emote="YES", amount=amount, plural="" if amount == 1 else "s")

            await ctx.send(text)


    @commands.group()
    @AutoModPlugin.can("manage_guild")
    async def allowed_invites(self, ctx):
        """
        allowed_invites_help
        examples:
        -allowed_invites
        -allowed_invites add 701507539589660793
        -allowed_invites remove 701507539589660793
        """
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


    @allowed_invites.command(name="add")
    @AutoModPlugin.can("manage_guild")
    async def add_inv(self, ctx, guild_id: int):
        """
        allowed_invites_add_help
        examples:
        -allowed_invites add 701507539589660793
        """
        allowed = [x.strip().lower() for x in self.db.configs.get(ctx.guild.id, "allowed_invites")]

        if str(guild_id) in allowed:
            return await ctx.send(self.locale.t(ctx.guild, "alr_allowed", _emote="NO"))
        
        allowed.append(str(guild_id))
        self.db.configs.update(ctx.guild.id, "allowed_invites", allowed)

        await ctx.send(self.locale.t(ctx.guild, "allowed_inv", _emote="YES"))


    @allowed_invites.command(name="remove")
    @AutoModPlugin.can("manage_guild")
    async def remove_inv(self, ctx, guild_id: int):
        """
        allowed_invites_remove_help
        examples:
        -allowed_invites remove 701507539589660793
        """
        allowed = [x.strip().lower() for x in self.db.configs.get(ctx.guild.id, "allowed_invites")]

        if not str(guild_id) in allowed:
            return await ctx.send(self.locale.t(ctx.guild, "not_allowed", _emote="NO"))
        
        allowed.remove(str(guild_id))
        self.db.configs.update(ctx.guild.id, "allowed_invites", allowed)

        await ctx.send(self.locale.t(ctx.guild, "unallowed_inv", _emote="YES"))


    @commands.group(aliases=["links"])
    @AutoModPlugin.can("manage_guild")
    async def link_blacklist(self, ctx):
        """
        link_blacklist_help
        examples:
        -link_blacklist
        -link_blacklist add google.com
        -link_blacklist remove google.com
        """
        if ctx.invoked_subcommand == None:
            links = [f"``{x.strip().lower()}``" for x in self.db.configs.get(ctx.guild.id, "black_listed_links")]
            if len(links) < 1:
                prefix = self.get_prefix(ctx.guild)
                return await ctx.send(self.locale.t(ctx.guild, "no_links", _emote="NO", prefix=prefix))
            
            e = Embed(
                title="Blacklisted links",
                description=", ".join(links)
            )
            await ctx.send(embed=e)


    @link_blacklist.command(name="add")
    @AutoModPlugin.can("manage_guild")
    async def add_link(self, ctx, url: str):
        """
        link_blacklist_add_help
        examples:
        -link_blacklist add google.com
        """
        url = self.safe_parse_url(url)
        links = [x.strip().lower() for x in self.db.configs.get(ctx.guild.id, "black_listed_links")]

        if str(url) in links:
            return await ctx.send(self.locale.t(ctx.guild, "alr_link", _emote="NO"))
        
        links.append(url)
        self.db.configs.update(ctx.guild.id, "black_listed_links", links)

        await ctx.send(self.locale.t(ctx.guild, "allowed_link", _emote="YES"))


    @link_blacklist.command(name="remove")
    @AutoModPlugin.can("manage_guild")
    async def remove_link(self, ctx, url: str):
        """
        link_blacklist_remove_help
        examples:
        -link_blacklist remove google.com
        """
        url = self.safe_parse_url(url)
        links = [x.strip().lower() for x in self.db.configs.get(ctx.guild.id, "black_listed_links")]

        if not str(url) in links:
            return await ctx.send(self.locale.t(ctx.guild, "not_link", _emote="NO"))
        
        links.remove(url)
        self.db.configs.update(ctx.guild.id, "black_listed_links", links)

        await ctx.send(self.locale.t(ctx.guild, "unallowed_link", _emote="YES"))


    @commands.group()
    @AutoModPlugin.can("manage_guild")
    async def link_whitelist(self, ctx):
        """
        link_whitelist_help
        examples:
        -link_whitelist
        -link_whitelist add google.com
        -link_whitelist remove google.com
        """
        if ctx.invoked_subcommand == None:
            links = [f"``{x.strip().lower()}``" for x in self.db.configs.get(ctx.guild.id, "white_listed_links")]
            if len(links) < 1:
                prefix = self.get_prefix(ctx.guild)
                return await ctx.send(self.locale.t(ctx.guild, "no_links2", _emote="NO", prefix=prefix))
            
            e = Embed(
                title="Allowed links",
                description=", ".join(links)
            )
            await ctx.send(embed=e)


    @link_whitelist.command(name="add")
    @AutoModPlugin.can("manage_guild")
    async def add_link2(self, ctx, url: str):
        """
        link_whitelist_add_help
        examples:
        -link_whitelist add google.com
        """
        url = self.safe_parse_url(url)
        links = [x.strip().lower() for x in self.db.configs.get(ctx.guild.id, "white_listed_links")]

        if str(url) in links:
            return await ctx.send(self.locale.t(ctx.guild, "alr_link2", _emote="NO"))
        
        links.append(url)
        self.db.configs.update(ctx.guild.id, "white_listed_links", links)

        await ctx.send(self.locale.t(ctx.guild, "allowed_link2", _emote="YES"))


    @link_whitelist.command(name="remove")
    @AutoModPlugin.can("manage_guild")
    async def remove_link_2(self, ctx, url: str):
        """
        link_whitelist_remove_help
        examples:
        -link_whitelist remove google.com
        """
        url = self.safe_parse_url(url)
        links = [x.strip().lower() for x in self.db.configs.get(ctx.guild.id, "white_listed_links")]

        if not str(url) in links:
            return await ctx.send(self.locale.t(ctx.guild, "not_link2", _emote="NO"))
        
        links.remove(url)
        self.db.configs.update(ctx.guild.id, "white_listed_links", links)

        await ctx.send(self.locale.t(ctx.guild, "unallowed_link2", _emote="YES"))


    @commands.group(name="filter", aliases=["filters"])
    @AutoModPlugin.can("manage_guild")
    async def _filter(self, ctx):
        """
        filter_help
        examples:
        -filter add test_filter 1 banana, apples, grape fruit
        -filter remove test_filter
        -filter show
        """
        if ctx.invoked_subcommand == None:
            prefix = self.get_prefix(ctx.guild)
            e = Embed(
                title="How to use filters",
                description=f"• Adding a filter: ``{prefix}filter add <name> <warns> <words>`` \n• Deleting a filter: ``{prefix}filter remove <name>``"
            )
            e.add_field(
                name="❯ Arguments",
                value="``<name>`` - *Name of the filter* \n``<warns>`` - *Warns users get when flagged. Use 0 if you want the message to be deleted* \n``<words>`` - *Words contained in the filter, seperated by commas*"
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
    @AutoModPlugin.can("manage_guild")
    async def add_filter(self, ctx, name, warns: int, *, words):
        """
        filter_add_help
        examples:
        -filter add test_filter 1 banana, apples, grape fruit
        """
        name = name.lower()
        filters = self.db.configs.get(ctx.guild.id, "filters")

        if len(name) > 30: return await ctx.send(self.locale.t(ctx.guild, "filter_name_too_long", _emote="NO"))
        if name in filters: return await ctx.send(self.locale.t(ctx.guild, "filter_exists", _emote="NO"))

        if warns < 0: return await ctx.send(self.locale.t(ctx.guild, "min_warns_esp", _emote="NO"))
        if warns > 100: return await ctx.send(self.locale.t(ctx.guild, "max_warns", _emote="NO"))

        filters[name] = {
            "warns": warns,
            "words": words.split(", ")
        }
        self.db.configs.update(ctx.guild.id, "filters", filters)

        await ctx.send(self.locale.t(ctx.guild, "added_filter", _emote="YES"))

    
    @_filter.command(name="remove")
    @AutoModPlugin.can("manage_guild")
    async def remove_filter(self, ctx, name):
        """
        filter_remove_help
        examples:
        -filter remove test_filter
        """
        name = name.lower()
        filters = self.db.configs.get(ctx.guild.id, "filters")

        if len(filters) < 1: return await ctx.send(self.locale.t(ctx.guild, "no_filters", _emote="NO"))
        if not name in filters: return await ctx.send(self.locale.t(ctx.guild, "no_filter", _emote="NO"))

        del filters[name]
        self.db.configs.update(ctx.guild.id, "filters", filters)

        await ctx.send(self.locale.t(ctx.guild, "removed_filter", _emote="YES"))


    @_filter.command()
    @AutoModPlugin.can("ban_members")
    async def show(self, ctx):
        """
        filter_show_help
        examples:
        -filter show
        """
        filters = self.db.configs.get(ctx.guild.id, "filters")
        if len(filters) < 1: return await ctx.send(self.locale.t(ctx.guild, "no_filters", _emote="NO"))

        e = Embed(
            title="Filters"
        )
        for name in dict(itertools.islice(filters.items(), 10)):
            i = filters[name]
            e.add_field(
                name=f"❯ {name} ({str(i['warns']) + ' warn' if i['warns'] == 1 else str(i['warns']) + ' warns' if i['warns'] > 0 else 'delete message'})",
                value=", ".join([f"``{x}``" for x in i["words"]])
            )

            footer = f"And {len(filters)-len(dict(itertools.islice(filters.items(), 10)))} more filters" if len(filters) > 10 else None
            if footer != None: e.set_footer(text=footer)

        await ctx.send(embed=e)


    @commands.group(aliases=["rgx"])
    @AutoModPlugin.can("manage_messages")
    async def regex(self, ctx):
        """
        regex_help
        examples:
        -regex
        -regex add test_regex \b(banana)\b 1
        -regex remove test_regex
        """
        if ctx.invoked_subcommand == None:
            regexes = self.db.configs.get(ctx.guild.id, "regexes")
            if len(regexes) < 1: return await ctx.send(self.locale.t(ctx.guild, "no_regexes", _emote="NO"))

            e = Embed(
                title="Regexes"
            )
            for name, data in regexes.items():
                e.add_field(
                    name=f"❯ {name} ({str(data['warns']) + ' warn' if data['warns'] == 1 else str(data['warns']) + ' warns' if data['warns'] > 0 else 'delete message'})",
                    value=f"```\n{data['regex']}\n```"
                )
            
            await ctx.send(embed=e)


    @regex.command(name="add")
    @AutoModPlugin.can("manage_messages")
    async def add_regex(self, ctx, name, regex, warns: int):
        """
        regex_add_help
        examples:
        -regex add test_regex \b(banana)\b 1
        """
        regexes = self.db.configs.get(ctx.guild.id, "regexes")
        name = name.lower()

        if len(name) > 30: return await ctx.send(self.locale.t(ctx.guild, "regex_name_too_long", _emote="NO"))
        if name in regexes: return await ctx.send(self.locale.t(ctx.guild, "regex_exists", _emote="NO"))

        if warns < 0: return await ctx.send(self.locale.t(ctx.guild, "min_warns_esp", _emote="NO"))
        if warns > 100: return await ctx.send(self.locale.t(ctx.guild, "max_warns", _emote="NO"))

        if self.validate_regex(regex) == False: return await ctx.send(self.locale.t(ctx.guild, "invalid_regex", _emote="NO"))

        regexes[name] = {
            "warns": warns,
            "regex": regex
        }
        self.db.configs.update(ctx.guild.id, "regexes", regexes)

        await ctx.send(self.locale.t(ctx.guild, "added_regex", _emote="YES"))


    @regex.command(name="remove", aliases=["delete", "del"])
    async def remove_regex(self, ctx, name):
        """
        regex_remove_help
        examples:
        -regex remove test_regex
        """
        regexes = self.db.configs.get(ctx.guild.id, "regexes")
        name = name.lower()

        if name not in regexes: return await ctx.send(self.locale.t(ctx.guild, "regex_doesnt_exist", _emote="NO"))

        del regexes[name]
        self.db.configs.update(ctx.guild.id, "regexes", regexes)

        await ctx.send(self.locale.t(ctx.guild, "removed_regex", _emote="YES"))


async def setup(bot): await bot.register_plugin(AutomodPlugin(bot))