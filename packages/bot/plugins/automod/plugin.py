# type: ignore

import discord
from discord.ext import commands

import re
import itertools
from toolbox import S as Object
from urllib.parse import urlparse
from typing import TypeVar, Literal, List
import logging; log = logging.getLogger()
from typing import Union, Tuple

from .. import AutoModPluginBlueprint, ShardedBotInstance
from .._processor import ActionProcessor, LogProcessor, DMProcessor
from ...types import Embed, E
from ...modals import FilterCreateModal, RegexCreateModal, FilterEditModal, RegexEditModal



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
EMOTE_RE = re.compile(
    r"<(a?):([^: \n]+):([0-9]{15,20})>"
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
ZALGO_RE = re.compile(
    u"|".join(ZALGO)
)


LOG_DATA = {
    "invites": {
        "rule": "Anti-Invites"
    },
    "links": {
        "rule": "Anti-Links"
    },
    "links_blacklist": {
        "rule": "Anti-Links (blacklist)"
    },
    "files": {
        "rule": "Anti-Files"
    },
    "zalgo": {
        "rule": "Anti-Zalgo"
    },
    "lines": {
        "rule": "Newline-Spam"
    },
    "mentions": {
        "rule": "Mention-Spam"
    },
    "emotes": {
        "rule": "Emote-Spam"
    },
    "repeat": {
        "rule": "Anti-Repetition"  
    },
    "regex": {
        "rule": "Regex-Filter"
    },
    "filter": {
        "rule": "Word-Filter"
    },
    "antispam": {
        "rule": "Anti-Spam"
    },
    "caps": {
        "rule": "Anti-CAPS"
    }
}


AUTOMOD_RULES = {
    "mentions": {
        "int_field_name": "threshold",
        "i18n_key": "set_mentions",
        "i18n_type": "maximum mentions",
        "field_name": "mention",
        "field_help": "mentions"
    },
    "links": {
        "int_field_name": "warns",
        "i18n_key": "set_links",
        "i18n_type": "link filtering",
        "field_name": "warn",
        "field_help": "warns"
    },
    "invites": {
        "int_field_name": "warns",
        "i18n_key": "set_invites",
        "i18n_type": "invite filtering",
        "field_name": "warn",
        "field_help": "warns"
    },
    "files": {
        "int_field_name": "warns",
        "i18n_key": "set_files",
        "i18n_type": "bad file detection",
        "field_name": "warn",
        "field_help": "warns"
    },
    "lines": {
        "int_field_name": "threshold",
        "i18n_key": "set_lines",
        "i18n_type": "maximum lines",
        "field_name": "line",
        "field_help": "lines"
    },
    "emotes": {
        "int_field_name": "threshold",
        "i18n_key": "set_emotes",
        "i18n_type": "maximum emotes",
        "field_name": "emote",
        "field_help": "emotes"
    },
    "repeat": {
        "int_field_name": "threshold",
        "i18n_key": "set_repeat",
        "i18n_type": "maximum repetitions",
        "field_name": "repeat",
        "field_help": "repeat"
    },
    "zalgo": {
        "int_field_name": "warns",
        "i18n_key": "set_zalgo",
        "i18n_type": "zalgo filtering",
        "field_name": "warn",
        "field_help": "warns"
    },
    "caps": {
        "int_field_name": "warns",
        "i18n_key": "set_caps",
        "i18n_type": "CAPS filtering",
        "field_name": "warn",
        "field_help": "warns"
    }
}


BYPASS_TO_SECONDS = {
    "1 Month": 2678400,
    "3 Months": 8035200,
    "6 Moths": 16070400,
    "1 Year": 32140800
}


CHANNEL_OR_ROLE_T = TypeVar("CHANNEL_OR_ROLE_T", discord.Role, discord.TextChannel)


class AutomodPlugin(AutoModPluginBlueprint):
    """Plugin for enforcing automoderator rules"""
    def __init__(
        self, 
        bot: ShardedBotInstance
    ) -> None:
        super().__init__(bot)
        self.action_processor = ActionProcessor(bot)
        self.log_processor = LogProcessor(bot)
        self.dm_processor = DMProcessor(bot)
        self.spam_cache = {}
        self.score_cache = {}


    def can_act(
        self, 
        guild: discord.Guild,  
        mod: discord.Member, 
        target: Union[
            discord.Member, 
            discord.User
        ]
    ) -> bool:
        if mod.id == target.id: return False
        if mod.id == guild.owner_id: return True

        mod = guild.get_member(mod.id)
        target = guild.get_member(target.id)
        if mod == None or target == None: return False

        rid = self.bot.db.configs.get(guild.id, "mod_role")
        if rid != "" and rid != None:
            if int(rid) in [x.id for x in target.roles]: return False

        return mod.id != target.id \
            and target.id != guild.owner.id \
            and (
                target.guild_permissions.ban_members == False 
                or target.guild_permissions.kick_members == False 
                or target.guild_permissions.manage_messages == False
            )
    

    def can_ignore(
        self,
        guild: discord.Guild,
        channel: discord.TextChannel,
        target: Union[
            discord.Member,
            discord.User
        ]
    ) -> bool:
        roles, channels = self.get_ignored_roles_channels(guild)
        if channels == None:
            self.db.configs.update(guild.id, "ignored_channels_automod", [])
        else:
            if channel.id in channels: return True

        if any(x in [i.id for i in target.roles] for x in roles): return True
        return False


    def parse_filter(
        self, 
        words: list
    ) -> Union[
        re.Pattern, 
        None
    ]:
        normal = []
        wildcards = []

        for i in words:
            i = i.replace("*", "", (i.count("*") - 1)) # remove multiple wildcards
            if i.endswith("*"):
                wildcards.append(i.replace("*", ".+"))
            else:
                normal.append(i)

        try:
            return re.compile(r"|".join([*normal, *wildcards]), re.IGNORECASE)
        except Exception:
            return None


    def parse_regex(
        self, 
        regex: str
    ) -> Union[
        re.Pattern, 
        None
    ]:
        try:
            parsed = re.compile(regex, re.IGNORECASE)
        except Exception:
            return None
        else:
            return parsed


    def validate_regex(
        self, 
        regex: str
    ) -> bool:
        try:
            re.compile(regex)
        except re.error:
            return False
        else:
            return True


    def safe_parse_url(
        self, 
        url: str
    ) -> str:
        url = url.lower()
        if not (
            url.startswith("https://") or
            url.startswith("http://")
        ):
            for x in [
                "www", 
                "www5", 
                "www2", 
                "www3"
            ]:
                url = url.replace(x, "")
        else:
            url = urlparse(url).hostname
        return url


    def parse_channels(
        self,
        channels: str
    ) -> List[
        int
    ]:
        final = []
        for s in channels.split(", "):
            if s.isdigit():
                final.append(int(s))
        return final


    def get_ignored_roles_channels(
        self, 
        guild: discord.Guild
    ) -> Tuple[
        list, 
        list
    ]:
        roles, channels = self.db.configs.get(guild.id, "ignored_roles_automod"), self.db.configs.get(guild.id, "ignored_channels_automod")
        return roles, channels


    def extract_args(
        self,
        i: discord.Interaction,
        *args
    ) -> tuple:
        return (
            i.data["components"][i.data["components"].index(
                [_ for _ in i.data["components"] if _["components"][0]["custom_id"] == x][0]
            )]["components"][0].get("value", None) for x in args
        )


    async def delete_msg(
        self, 
        rule: str, 
        found: str, 
        msg: discord.Message, 
        warns: int, 
        reason: str, 
        pattern_or_filter: Union[
            str, 
            None
        ] = None
    ) -> None:
        try:
            await msg.delete()
        except (
            discord.NotFound, 
            discord.Forbidden
        ):
            pass
        else:
            self.bot.ignore_for_events.append(msg.id)
        finally:
            data = Object(LOG_DATA[rule])
            if warns > 0:
                await self.action_processor.execute(
                    msg, 
                    msg.guild.me,
                    msg.author,
                    warns, 
                    reason,
                    **{
                        "rule": data.rule if rule not in ["filter", "regex"] else None,
                        "pattern": f"{pattern_or_filter}",
                        "found": found,
                        "channel_id": msg.channel.id,
                        "content": msg.content,
                    }
                )
            else:
                self.dm_processor.execute(
                    msg,
                    "automod_rule_triggered",
                    msg.author,
                    **{
                        "guild_name": msg.guild.name,
                        "rule": data.rule,
                        "_emote": "SWORDS"
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
                            "mod": msg.guild.me,
                            "mod_id": msg.guild.me.id,
                            "channel_id": msg.channel.id,
                            "content": msg.content,
                            "case": self.action_processor.new_case("automod", msg, msg.guild.me, msg.author, f"{reason}, automated by AutoMod")
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
                            "mod": msg.guild.me,
                            "mod_id": msg.guild.me.id,
                            "channel_id": msg.channel.id,
                            "content": msg.content,
                            "case": self.action_processor.new_case(rule, msg, msg.guild.me, msg.author, f"{reason}, automated by AutoMod")
                        }
                    )


    async def enforce_rules(
        self, 
        msg: discord.Message
    ) -> None:
        content = msg.content.replace("\\", "")

        config = Object(self.db.configs.get_doc(msg.guild.id))
        rules = config.automod
        filters = config.filters
        regexes = config.regexes
        antispam = config.antispam

        if antispam.enabled == True:
            if not self.can_ignore(msg.guild, msg.channel, msg.author):
                if not msg.guild.id in self.spam_cache:
                    self.spam_cache.update({
                        msg.guild.id: commands.CooldownMapping.from_cooldown(
                            antispam.rate,
                            float(antispam.per),
                            commands.BucketType.user
                        )
                    })
                
                mapping = self.spam_cache[msg.guild.id]
                now = msg.created_at.timestamp()

                users = mapping.get_bucket(msg)
                if users.update_rate_limit(now):
                    return await self.delete_msg(
                        "antispam",
                        f"{users.rate}/{round(users.per, 0)}",
                        msg, 
                        antispam.warns, 
                        f"Spam detected"
                    )


        if len(filters) > 0:
            for name in filters:
                f = filters[name]
                if msg.channel.id in f["channels"] or len(f["channels"]) < 1:
                    parsed = self.parse_filter(f["words"])
                    if parsed != None:
                        found = parsed.findall(content)
                        if found:
                            return await self.delete_msg(
                                "filter",
                                ", ".join([f"``{x}``" for x in found]),
                                msg, 
                                int(f["warns"]), 
                                f"Blacklisted spam",
                                name
                            )
        
        if len(regexes) > 0:
            for name, data in regexes.items():
                if msg.channel.id in f["channels"] or len(f["channels"]) < 1:
                    parsed = self.parse_regex(data["regex"])
                    if parsed != None:
                        found = parsed.findall(content)
                        if found:
                            return await self.delete_msg(
                                "regex",
                                ", ".join([f"``{x}``" for x in found]),
                                msg, 
                                int(data["warns"]), 
                                f"Blacklisted spam",
                                name
                            )
        
        if len(rules) < 1: return
        if self.can_ignore(
            msg.guild, 
            msg.channel, 
            msg.author
        ): return

        if hasattr(rules, "invites"):
            found = INVITE_RE.findall(content)
            if found:
                for inv in found:
                    try:
                        invite: discord.Invite = await self.bot.fetch_invite(inv)
                    except discord.NotFound:
                        return await self.delete_msg(
                            "invites",
                            f"``{inv}``",
                            msg, 
                            rules.invites.warns, 
                            f"Sending Discord invite link or equivalent redirect"
                        )
                    if invite.guild == None:
                        return await self.delete_msg(
                            "invites",
                            f"``{inv}``",
                            msg, 
                            rules.invites.warns, 
                            f"Sending Discord invite link or equivalent redirect"
                        )
                    else:
                        if invite.guild == None \
                            or (
                                not invite.guild.id in config.allowed_invites \
                                and invite.guild.id != msg.guild.id
                            ):
                                return await self.delete_msg(
                                    "invites",
                                    f"``{inv}``",
                                    msg, 
                                    rules.invites.warns, 
                                    f"Sending Discord invite link or equivalent redirect"
                                )
        
        if hasattr(rules, "links"):
            found = LINK_RE.findall(content)
            if found:
                for link in found:
                    url = urlparse(link)
                    if url.hostname in config.black_listed_links:
                        return await self.delete_msg(
                            "links_blacklist", 
                            f"``{url.hostname}``",
                            msg, 
                            rules.links.warns, 
                            f"Posting a link without permission"
                        )
                    else:
                        if not url.hostname in config.white_listed_links:
                            return await self.delete_msg(
                                "links", 
                                f"``{url.hostname}``",
                                msg, 
                                rules.links.warns, 
                                f"Posting a link without permission"
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
                        ", ".join([f"``{x}``" for x in forbidden]), 
                        msg, 
                        rules.files.warns, 
                        f"Posting forbidden attachment type"
                    )

        if hasattr(rules, "zalgo"):
            found = ZALGO_RE.search(content)
            if found:
                return await self.delete_msg(
                    "zalgo", 
                    f"``{found.group()}``", 
                    msg, 
                    rules.zalgo.warns, 
                    f"Excessive or/and unwanted use of symbols"
                )

        if hasattr(rules, "mentions"):
            found = len(MENTION_RE.findall(content))
            if found > rules.mentions.threshold:
                return await self.delete_msg(
                    "mentions", 
                    f"``{found}``", 
                    msg, 
                    0 if (found - rules.mentions.threshold) == 1 else 1, 
                    f"Excessive use of mentions"
                )

        if hasattr(rules, "lines"):
            found = len(content.split("\n"))
            if found > rules.lines.threshold:
                return await self.delete_msg(
                    "lines", 
                    f"``{found}``", 
                    msg, 
                    0 if (found - rules.lines.threshold) == 1 else 1, 
                    f"Message too long"
                )

        if hasattr(rules, "emotes"):
            found = len(EMOTE_RE.findall(content))
            if found > rules.emotes.threshold:
                return await self.delete_msg(
                    "emotes", 
                    f"``{found}``", 
                    msg, 
                    0 if (found - rules.emotes.threshold) == 1 else 1, 
                    f"Excessive use of emotes"
                )

        if hasattr(rules, "repeat"):
            found = {}
            for word in content.split(" "):
                found.update({
                    word.lower(): found.get(word.lower(), 0) + 1
                })
            if len(found.keys()) < 12:
                for k, v in found.items():
                    if v > rules.repeat.threshold:
                        return await self.delete_msg(
                            "repeat", 
                            f"``{k} ({v}x)``", 
                            msg, 
                            0 if (v - rules.repeat.threshold) == 1 else 1, 
                            f"Duplicated text"
                        )
        
        if hasattr(rules, "caps"):
            if len(content) > 10:
                perc_caps = round(((len([x for x in content if x.isupper()]) / len(content)) * 100))
                if perc_caps >= 75:
                    return await self.delete_msg(
                        "caps", 
                        f"``{perc_caps}% in {len(content)} chars``", 
                        msg, 
                        rules.caps.warns, 
                        f"Excessive use of CAPS"
                    )


    @AutoModPluginBlueprint.listener()
    async def on_message(
        self, 
        msg: discord.Message
    ) -> None:
        if msg.guild == None: return
        if not msg.guild.chunked: await self.bot.chunk_guild(msg.guild)
        if not self.can_act(msg.guild, msg.guild.me, msg.author): return

        await self.enforce_rules(msg)


    @AutoModPluginBlueprint.listener()
    async def on_message_edit(
        self, 
        _, 
        msg: discord.Message
    ) -> None:
        if msg.guild == None: return
        if not msg.guild.chunked: await self.bot.chunk_guild(msg.guild)
        if not self.can_act(msg.guild, msg.guild.me, msg.author): return

        await self.enforce_rules(msg)


    @discord.app_commands.command(
        name="automod", 
        description="🔰 Configure the automoderator"
    )
    @discord.app_commands.describe(
        rule="The rule you want to configure", 
        warns_or_threshold="Warn amount or threshold for this rule (use 0 to just  have the message deleted)",
        disable="Set this to true if you want to disable the rule"
    )
    @discord.app_commands.default_permissions(manage_guild=True)
    async def automod(
        self, 
        ctx: discord.Interaction, 
        rule: Literal[
            "Invites",
            "Links",
            "Files",
            "Mentions",
            "Lines",
            "Emotes",
            "Repeat",
            "Zalgo",
            "Caps"
        ],
        warns_or_threshold: int = None,
        disable: Literal[
            "True"
        ] = None
    ) -> None:
        """
        automod_help
        examples:
        -automod invites 1
        -automod mentions 10
        -automod files 0
        -automod links off
        """
        amount = warns_or_threshold
        if warns_or_threshold == None and disable == None:
            e = Embed(
                ctx,
                title="Automoderator Configuration",
                description=self.locale.t(ctx.guild, "automod_description", prefix="/")
            )
            e.add_field(
                name="**❯ Command usage**",
                value=self.locale.t(ctx.guild, "automod_commands", prefix="/")
            )
            return await ctx.response.send_message(embed=e)
        
        rule = rule.lower()
        if not rule in AUTOMOD_RULES:
            e = Embed(
                ctx,
                description=self.locale.t(ctx.guild, "invalid_automod_rule", _emote="NO", given=rule)
            )
            e.add_field(
                name="**❯ Valid rules**",
                value=">  mentions \n>  links \n>  invites \n>  files \n>  zalgo \n>  lines \n>  emotes \n>  repeat \n>  caps"
            )
            return await ctx.response.send_message(embed=e)
        
        current = self.db.configs.get(ctx.guild.id, "automod")
        data = Object(AUTOMOD_RULES[rule])

        if disable != None:
            self.db.configs.update(ctx.guild.id, "automod", {k: v for k, v in current.items() if k != rule})
            return await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "automod_off", _emote="YES", _type=data.i18n_type), 1))
        else:
            amount = round(int(amount))
            if rule in ["mentions", "lines", "emotes", "repeat"]:
                if amount < 5: return await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "min_am_amount", _emote="NO", field=rule.replace("s", "")), 0))
                if amount > 100: return await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "max_am_amount", _emote="NO", field=rule.replace("s", "")), 0))
            else:
                if amount < 0: return await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "min_warns_esp", _emote="NO"), 0))
                if amount > 100: return await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "max_warns", _emote="NO"), 0))

            current.update({
                rule: {
                    data.int_field_name: int(amount)
                }
            })
            self.db.configs.update(ctx.guild.id, "automod", current)

            text = ""
            if not rule in ["mentions", "lines", "emotes", "repeat"] and amount == 0:
                text = self.locale.t(ctx.guild, f"{data.i18n_key}_zero", _emote="YES")
            else:
                text = self.locale.t(ctx.guild, data.i18n_key, _emote="YES", amount=amount, plural="" if amount == 1 else "s")

            await ctx.response.send_message(text)


    allowed_invites = discord.app_commands.Group(
        name="allowed_invites",
        description="🔀 Configure allowed invite links",
        default_permissions=discord.Permissions(manage_guild=True)
    )
    @allowed_invites.command(
        name="show",
        description="🔗 Shows all currently allowed invite links"
    )
    @discord.app_commands.default_permissions(manage_guild=True)
    async def show_inv(
        self, 
        ctx: discord.Interaction,
    ) -> None:
        """
        allowed_invites_help
        examples:
        -allowed_invites show
        """
        allowed = [f"``{x.strip().lower()}``" for x in self.db.configs.get(ctx.guild.id, "allowed_invites")]
        if len(allowed) < 1: return await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "no_allowed", _emote="NO", prefix="/"), 0))
        
        e = Embed(
            ctx,
            title="Allowed invites (by server ID)",
            description="> {}".format(", ".join(allowed))
        )
        await ctx.response.send_message(embed=e)


    @allowed_invites.command(
        name="add",
        description="✅ Adds a guild to the allowed invite list"
    )
    @discord.app_commands.default_permissions(manage_guild=True)
    async def add_inv(
        self, 
        ctx: discord.Interaction, 
        guild_id: str
    ) -> None:
        """
        allowed_invites_add_help
        examples:
        -allowed_invites add 701507539589660793
        """
        allowed = [x.strip().lower() for x in self.db.configs.get(ctx.guild.id, "allowed_invites")]
        if str(guild_id) in allowed: return await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "alr_allowed", _emote="NO"), 0))
        
        allowed.append(str(guild_id))
        self.db.configs.update(ctx.guild.id, "allowed_invites", allowed)

        await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "allowed_inv", _emote="YES"), 1))


    @allowed_invites.command(
        name="remove",
        description="❌ Removes a guild from the allowed invite list"
    )
    @discord.app_commands.default_permissions(manage_guild=True)
    async def remove_inv(
        self, 
        ctx: discord.Interaction, 
        guild_id: str
    ) -> None:
        """
        allowed_invites_remove_help
        examples:
        -allowed_invites remove 701507539589660793
        """
        allowed = [x.strip().lower() for x in self.db.configs.get(ctx.guild.id, "allowed_invites")]
        if not str(guild_id) in allowed: return await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "not_allowed", _emote="NO"), 0))
        
        allowed.remove(str(guild_id))
        self.db.configs.update(ctx.guild.id, "allowed_invites", allowed)

        await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "unallowed_inv", _emote="YES"), 1))


    link_blacklist = discord.app_commands.Group(
        name="link_blacklist",
        description="🔀 Configure the link blacklist",
        default_permissions=discord.Permissions(manage_guild=True)
    )
    @link_blacklist.command(
        name="show",
        description="🔗 Shows the current link blacklist"
    )
    @discord.app_commands.default_permissions(manage_guild=True)
    async def show_link(
        self, 
        ctx: discord.Interaction
    ) -> None:
        """
        link_blacklist_help
        examples:
        -link_blacklist show
        """
        links = [f"``{x.strip().lower()}``" for x in self.db.configs.get(ctx.guild.id, "black_listed_links")]
        if len(links) < 1: return await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "no_links", _emote="NO", prefix="/"), 0))
        
        e = Embed(
            ctx,
            title="Blacklisted links",
            description="> {}".format(", ".join(links))
        )
        await ctx.response.send_message(embed=e)


    @link_blacklist.command(
        name="add",
        description="✅ Adds a link to the blacklist"
    )
    @discord.app_commands.default_permissions(manage_guild=True)
    async def add_link(
        self, 
        ctx: discord.Interaction, 
        url: str
    ) -> None:
        """
        link_blacklist_add_help
        examples:
        -link_blacklist add google.com
        """
        url = self.safe_parse_url(url)

        links = [x.strip().lower() for x in self.db.configs.get(ctx.guild.id, "black_listed_links")]
        if str(url) in links: return await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "alr_link", _emote="NO"), 0))
        
        links.append(url)
        self.db.configs.update(ctx.guild.id, "black_listed_links", links)

        await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "allowed_link", _emote="YES"), 1))


    @link_blacklist.command(
        name="remove",
        description="❌ Removes the link from the blacklist"
    )
    @discord.app_commands.default_permissions(manage_guild=True)
    async def remove_link(
        self, 
        ctx: discord.Interaction, 
        url: str
    ) -> None:
        """
        link_blacklist_remove_help
        examples:
        -link_blacklist remove google.com
        """
        url = self.safe_parse_url(url)

        links = [x.strip().lower() for x in self.db.configs.get(ctx.guild.id, "black_listed_links")]
        if not str(url) in links: return await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "not_link", _emote="NO"), 0))
        
        links.remove(url)
        self.db.configs.update(ctx.guild.id, "black_listed_links", links)

        await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "unallowed_link", _emote="YES"), 1))


    link_whitelist = discord.app_commands.Group(
        name="link_whitelist",
        description="🔀 Configure the link whitelist",
        default_permissions=discord.Permissions(manage_guild=True)
    )
    @link_whitelist.command(
        name="show",
        description="🔗 Shows the current link whitelist"
    )
    @discord.app_commands.default_permissions(manage_guild=True)
    async def show_link2(
        self, 
        ctx: discord.Interaction
    ) -> None:
        """
        link_whitelist_help
        examples:
        -link_whitelist
        """
        links = [f"``{x.strip().lower()}``" for x in self.db.configs.get(ctx.guild.id, "white_listed_links")]
        if len(links) < 1: return await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "no_links2", _emote="NO", prefix="/"), 0))
        
        e = Embed(
            ctx,
            title="Allowed links",
            description="> {}".format(", ".join(links))
        )
        await ctx.response.send_message(embed=e)


    @link_whitelist.command(
        name="add",
        description="✅ Adds a link to the whitelist"
    )
    @discord.app_commands.default_permissions(manage_guild=True)
    async def add_link2(
        self, 
        ctx: discord.Interaction, 
        url: str
    ) -> None:
        """
        link_whitelist_add_help
        examples:
        -link_whitelist add google.com
        """
        url = self.safe_parse_url(url)
        links = [x.strip().lower() for x in self.db.configs.get(ctx.guild.id, "white_listed_links")]

        if str(url) in links: return await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "alr_link2", _emote="NO"), 0))
        
        links.append(url)
        self.db.configs.update(ctx.guild.id, "white_listed_links", links)

        await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "allowed_link2", _emote="YES"), 1))


    @link_whitelist.command(
        name="remove",
        description="❌ Removes the link from the whitelist"
    )
    @discord.app_commands.default_permissions(manage_guild=True)
    async def remove_link_2(
        self, 
        ctx: discord.Interaction, 
        url: str
    ) -> None:
        """
        link_whitelist_remove_help
        examples:
        -link_whitelist remove google.com
        """
        url = self.safe_parse_url(url)
        links = [x.strip().lower() for x in self.db.configs.get(ctx.guild.id, "white_listed_links")]

        if not str(url) in links: return await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "not_link2", _emote="NO"), 0))
        
        links.remove(url)
        self.db.configs.update(ctx.guild.id, "white_listed_links", links)

        await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "unallowed_link2", _emote="YES"), 1))


    _filter = discord.app_commands.Group(
        name="filter",
        description="🔀 Configure word filters",
        default_permissions=discord.Permissions(manage_messages=True)
    )
    @_filter.command(
        name="show",
        description="⛔️ Shows all active word filters"
    )
    @discord.app_commands.default_permissions(manage_messages=True)
    async def show_filter(
        self, 
        ctx: discord.Interaction
    ) -> None:
        """
        filter_show_help
        examples:
        -filter show
        """
        filters = self.db.configs.get(ctx.guild.id, "filters")
        if len(filters) < 1: return await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "no_filters", _emote="NO"), 0))

        e = Embed(
            ctx,
            title="Filters"
        )
        for indx, name in enumerate(dict(itertools.islice(filters.items(), 10))):
            i = filters[name]
            action = str(i["warns"]) + " warn" if i["warns"] == 1 else str(i["warns"]) + " warns" if i["warns"] > 0 else "delete message"
            channels = "all channels" if len(i["channels"]) < 1 else ", ".join([f'#{ctx.guild.get_channel(int(x))}' for x in i["channels"]])

            e.add_field(
                name=f"**❯ {name}**",
                value=f">  **Action:** {action} \n>  **Channels:** {channels} \n>  **Words:** \n```\n{', '.join([f'{x}' for x in i['words']])}\n```",
                inline=True
            )
            if indx % 2 == 0: e.add_fields([e.blank_field(True, 2)])

            footer = f"And {len(filters)-len(dict(itertools.islice(filters.items(), 10)))} more filters" if len(filters) > 10 else None
            if footer != None: e.set_footer(text=footer)

        await ctx.response.send_message(embed=e)
    

    @_filter.command(
        name="add",
        description="✅ Creates a new word filter"
    )
    @discord.app_commands.default_permissions(manage_messages=True)
    async def add_filter(
        self, 
        ctx: discord.Interaction
    ) -> None:
        """
        filter_add_help
        examples:
        -filter add
        """
        async def callback(
            i: discord.Interaction
        ) -> None:
            name, warns, words, channels = self.extract_args(i, "name", "warns", "words", "channels")

            name = name.lower()
            filters = self.db.configs.get(i.guild.id, "filters")

            if len(name) > 30: return await i.response.send_message(embed=E(self.locale.t(i.guild, "filter_name_too_long", _emote="NO"), 0))
            if name in filters: return await i.response.send_message(embed=E(self.locale.t(i.guild, "filter_exists", _emote="NO"), 0))
            
            try: warns = int(warns)
            except Exception as ex: return await i.response.send_message(embed=E(self.locale.t(i.guild, "must_be_int", _emote="NO", arg="warns"), 0))

            if warns < 0: return await i.response.send_message(embed=E(self.locale.t(i.guild, "min_warns_esp", _emote="NO"), 0))
            if warns > 100: return await i.response.send_message(embed=E(self.locale.t(i.guild, "max_warns", _emote="NO"), 0))

            filters[name] = {
                "warns": warns,
                "words": words.split(", "),
                "channels": [] if channels == None else self.parse_channels(channels)
            }
            self.db.configs.update(i.guild.id, "filters", filters)
            await i.response.send_message(embed=E(self.locale.t(i.guild, "added_filter", _emote="YES"), 1))

        modal = FilterCreateModal(self.bot, "Create Filter", callback)
        await ctx.response.send_modal(modal)

    
    @_filter.command(
        name="remove",
        description="❌ Deletes an exisiting word filter"
    )
    @discord.app_commands.describe(
        name="Name of the filter",
    )
    @discord.app_commands.default_permissions(manage_messages=True)
    async def remove_filter(
        self, 
        ctx: discord.Interaction, 
        name: str
    ) -> None:
        """
        filter_remove_help
        examples:
        -filter remove test_filter
        """
        name = name.lower()
        filters = self.db.configs.get(ctx.guild.id, "filters")

        if len(filters) < 1: return await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "no_filters", _emote="NO"), 0))
        if not name in filters: return await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "no_filter", _emote="NO"), 0))

        del filters[name]
        self.db.configs.update(ctx.guild.id, "filters", filters)

        await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "removed_filter", _emote="YES"), 1))

    
    @_filter.command(
        name="edit",
        description="🔀 Edits an exisiting word filter"
    )
    @discord.app_commands.describe(
        name="Name of the filter",
    )
    @discord.app_commands.default_permissions(manage_messages=True)
    async def edit_filter(
        self, 
        ctx: discord.Interaction, 
        name: str, 
    ) -> None:
        """
        filter_edit_help
        examples:
        -filter edit test_filter
        """
        name = name.lower()
        filters = self.db.configs.get(ctx.guild.id, "filters")

        if len(name) > 30: return await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "filter_name_too_long", _emote="NO"), 0))
        if not name in filters: return await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "no_filter", _emote="NO"), 0))

        async def callback(
            i: discord.Interaction
        ) -> None:
            warns, words, channels = self.extract_args(i, "warns", "words", "channels")

            try: warns = int(warns)
            except Exception as ex: return await i.response.send_message(embed=E(self.locale.t(i.guild, "must_be_int", _emote="NO", arg="warns"), 0))

            if warns < 0: return await i.response.send_message(embed=E(self.locale.t(i.guild, "min_warns_esp", _emote="NO"), 0))
            if warns > 100: return await i.response.send_message(embed=E(self.locale.t(i.guild, "max_warns", _emote="NO"), 0))

            filters[name] = {
                "warns": warns,
                "words": words.split(", "),
                "channels": [] if channels == None else self.parse_channels(channels)
            }
            self.db.configs.update(i.guild.id, "filters", filters)

            await i.response.send_message(embed=E(self.locale.t(i.guild, "edited_filter", _emote="YES"), 1))
        
        modal = FilterEditModal(
            self.bot, 
            f"Edit Filter {name}", 
            filters[name].get("warns"),
            ", ".join(filters[name].get("words")),
            ", ".join(filters[name].get("channels")),
            callback
        )
        await ctx.response.send_modal(modal)

    
    regex = discord.app_commands.Group(
        name="regex",
        description="🔀 Configure regex filters",
        default_permissions=discord.Permissions(manage_messages=True)
    )
    @regex.command(
        name="show",
        description="⛔️ Shows a list of active regex filters"
    )
    @discord.app_commands.default_permissions(manage_messages=True)
    async def show_regex(
        self, 
        ctx: discord.Interaction
    ) -> None:
        r"""
        regex_help
        examples:
        -regex show
        """
        regexes = self.db.configs.get(ctx.guild.id, "regexes")
        if len(regexes) < 1: return await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "no_regexes", _emote="NO"), 0))

        e = Embed(
            ctx,
            title="Regexes"
        )
        for indx, name in enumerate(dict(itertools.islice(regexes.items(), 10))):
            data = regexes[name]
            action = str(data["warns"]) + " warn" if data["warns"] == 1 else str(data["warns"]) + " warns" if data["warns"] > 0 else "delete message"
            channels = "all channels" if len(data["channels"]) < 1 else ", ".join([f"#{ctx.guild.get_channel(int(x))}" for x in data["channels"]])

            e.add_field(
                name=f"**❯ {name}**",
                value=f">  **Action:** {action} \n>  **Channels:** {channels} \n>  **Pattern:** \n```\n{data['regex']}\n```",
                inline=True
            )
            if indx % 2 == 0: e.add_fields([e.blank_field(True, 2)])

            footer = f"And {len(regexes)-len(dict(itertools.islice(regexes.items(), 10)))} more filters" if len(regexes) > 10 else None
        if footer != None: e.set_footer(text=footer)
        
        await ctx.response.send_message(embed=e)


    @regex.command(
        name="add",
        description="✅ Adds a new regex filter with the given name, warns, pattern and channels"
    )
    async def add_regex(
        self, 
        ctx: discord.Interaction, 
    ) -> None:
        r"""
        regex_add_help
        examples:
        -regex add
        """
        async def callback(
            i: discord.Interaction
        ) -> None:
            name, warns, regex, channels = self.extract_args(i, "name", "warns", "pattern", "channels")
            regexes = self.db.configs.get(i.guild.id, "regexes")
            name = name.lower()

            if len(name) > 30: return await i.response.send_message(embed=E(self.locale.t(i.guild, "regex_name_too_long", _emote="NO"), 0))
            if name in regexes: return await i.response.send_message(embed=E(self.locale.t(i.guild, "regex_exists", _emote="NO"), 0))

            try: warns = int(warns)
            except Exception as ex: return await i.response.send_message(embed=E(self.locale.t(i.guild, "must_be_int", _emote="NO", arg="warns"), 0))

            if warns < 0: return await i.response.send_message(embed=E(self.locale.t(i.guild, "min_warns_esp", _emote="NO"), 0))
            if warns > 100: return await i.response.send_message(embed=E(self.locale.t(i.guild, "max_warns", _emote="NO"), 0))

            if self.validate_regex(regex) == False: return await i.response.send_message(embed=E(self.locale.t(i.guild, "invalid_regex", _emote="NO"), 0))

            regexes[name] = {
                "warns": warns,
                "regex": regex,
                "channels": [] if channels == None else self.parse_channels(channels)
            }
            self.db.configs.update(i.guild.id, "regexes", regexes)

            await i.response.send_message(embed=E(self.locale.t(i.guild, "added_regex", _emote="YES"), 1))
        
        modal = RegexCreateModal(self.bot, "Create Regex Filter", callback)
        await ctx.response.send_modal(modal)


    @regex.command(
        name="remove",
        description="❌ Deletes an exisiting regex filter"
    )
    @discord.app_commands.describe(
        name="Name of the filter",
    )
    @discord.app_commands.default_permissions(manage_messages=True)
    async def remove_regex(
        self, 
        ctx: discord.Interaction, 
        name: str
    ) -> None:
        """
        regex_remove_help
        examples:
        -regex remove test_regex
        """
        regexes = self.db.configs.get(ctx.guild.id, "regexes")
        name = name.lower()

        if not name in regexes: return await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "regex_doesnt_exist", _emote="NO"), 0))

        del regexes[name]
        self.db.configs.update(ctx.guild.id, "regexes", regexes)

        await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "removed_regex", _emote="YES"), 1))


    @regex.command(
        name="edit",
        description="🔀 Edits an existing regex filter"
    )
    @discord.app_commands.describe(
        name="Name of the regex filter you want to edit",
    )
    @discord.app_commands.default_permissions(manage_messages=True)
    async def edit_regex(
        self, 
        ctx: discord.Interaction, 
        name: str
    ) -> None:
        r"""
        regex_edit_help
        examples:
        -regex edit test_regex
        """
        name = name.lower()
        regexes = self.db.configs.get(ctx.guild.id, "regexes")

        if len(name) > 30: return await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "regex_name_too_long", _emote="NO"), 0))
        if not name in regexes: return await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "regex_doesnt_exist", _emote="NO"), 0))

        async def callback(
            i: discord.Interaction
        ) -> None:
            warns, regex, channels = self.extract_args(i, "warns", "pattern", "channels")

            try: warns = int(warns)
            except Exception as ex: return await i.response.send_message(embed=E(self.locale.t(i.guild, "must_be_int", _emote="NO", arg="warns"), 0))

            if warns < 0: return await i.response.send_message(embed=E(self.locale.t(i.guild, "min_warns_esp", _emote="NO"), 0))
            if warns > 100: return await i.response.send_message(embed=E(self.locale.t(i.guild, "max_warns", _emote="NO"), 0))

            if self.validate_regex(regex) == False: return await i.response.send_message(embed=E(self.locale.t(i.guild, "invalid_regex", _emote="NO"), 0))

            regexes[name] = {
                "warns": warns,
                "regex": regex,
                "channels": [] if channels == None else self.parse_channels(channels)
            }
            self.db.configs.update(i.guild.id, "regexes", regexes)

            await i.response.send_message(embed=E(self.locale.t(i.guild, "edited_regex", _emote="YES"), 1))

        modal = RegexEditModal(
            self.bot, 
            f"Edit Regex {name}", 
            regexes[name].get("warns"),
            regexes[name].get("regex"),
            ", ".join(regexes[name].get("channels")),
            callback
        )
        await ctx.response.send_modal(modal)


    @discord.app_commands.command(
        name="antispam",
        description="🔄 Configure the antispam filter"
    )
    @discord.app_commands.describe(
        rate="Allowed amount of messages (put 'off' here to disable the antispam filter)",
        per="Timeframe the amount messages are allowed to be sent in",
        warns="Amount of warns users should receive when spam is detected"
    )
    @discord.app_commands.default_permissions(manage_guild=True)
    async def antispam(
        self, 
        ctx: discord.Interaction, 
        rate: str = None,
        per: int = None, 
        warns: int = None
    ) -> None:
        """
        antispam_help
        examples:
        -antispam
        -antispam 12 per:10 3
        -antispam off
        """
        config = self.db.configs.get(ctx.guild.id, "antispam")

        prefix = "/"
        info_embed = Embed(
            ctx,
            description=self.locale.t(ctx.guild, "antispam_info", _emote="NO")
        )
        info_embed.add_fields([
            {
                "name": "**❯ View current config**",
                "value": f"``{prefix}antispam``"
            },
            {
                "name": "**❯ Enable antispam**",
                "value": f"``{prefix}antispam <rate> <per> <warns>``"
            },
            {
                "name": "**❯ Disable antispam**",
                "value": f"``{prefix}antispam rate:off``"
            }
        ])

        if rate == None and per == None and warns == None:
            e = Embed(
                ctx,
                title="Antispam Config"
            )
            e.add_fields([
                {
                    "name": "**❯ Status**",
                    "value": ">  Enabled" if config["enabled"] == True else ">  Disabled",
                    "inline": False
                },
                {
                    "name": "**❯ Threshold**",
                    "value": f">  **{config['rate']}** messages per **{config['per']}** seconds" if config["enabled"] == True else ">  N/A",
                    "inline": False
                },
                {
                    "name": "**❯ Action**",
                    "value": f">  **{config['warns']}** warn{'' if config['warns'] == 1 else 's'}" if config["enabled"] == True else ">  N/A",
                    "inline": False
                }
            ])

            await ctx.response.send_message(embed=e)
        elif per == None and warns == None:
            if not rate.isdigit():
                if rate.lower() == "off":
                    config.update({
                        "enabled": False
                    })
                    self.db.configs.update(ctx.guild.id, "antispam", config)
                    await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "disabled_antispam", _emote="YES"), 1))
                else:
                    await ctx.response.send_message(embed=info_embed)
            else:
                await ctx.response.send_message(embed=info_embed)
        elif warns == None:
            await ctx.response.send_message(embed=info_embed)
        else:
            try:
                rate = int(rate)
                per = int(per)
            except ValueError:
                return await ctx.response.send_message(embed=info_embed)
            else:
                if rate < 3: return await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "min_rate", _emote="NO"), 0))
                if rate > 21: return await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "max_rate", _emote="NO"), 0))

                if per < 3: return await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "min_per", _emote="NO"), 0))
                if per > 20: return await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "max_per", _emote="NO"), 0))

                if warns < 1: return await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "min_warns", _emote="NO"), 0))
                if warns > 100: return await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "min_warns", _emote="NO"), 0))

                config.update({
                    "enabled": True,
                    "rate": rate,
                    "per": per,
                    "warns": warns
                })

                am_plugin = self.bot.get_plugin("AutoModPluginBlueprint")
                am_plugin.spam_cache.update({
                    ctx.guild.id: commands.CooldownMapping.from_cooldown(
                        rate,
                        float(per),
                        commands.BucketType.user
                    )
                })
                self.db.configs.update(ctx.guild.id, "antispam", config)
                await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "enabled_antispam", _emote="YES", rate=rate, per=per, warns=warns), 0))


    ignore_automod = discord.app_commands.Group(
        name="ignore_automod",
        description="🔀 Manage ignored roles & channels for the automoderator",
        default_permissions=discord.Permissions(manage_guild=True)
    )
    @ignore_automod.command(
        name="show",
        description="🔒 Shows the current list of ignored roles & channels for the automoderator"
    )
    @discord.app_commands.default_permissions(manage_guild=True)
    async def show(
        self, 
        ctx: discord.Interaction
    ) -> None:
        """
        ignore_automod_help
        examples:
        -ignore_automod show
        """
        roles, channels = self.get_ignored_roles_channels(ctx.guild)

        if (len(roles) + len(channels)) < 1:
            return await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "no_ignored_am", _emote="NO"), 0))
        else:
            e = Embed(
                ctx,
                title="Ignored roles & channels for the automoderator"
            )
            e.add_fields([
                {
                    "name": "**❯ Roles**",
                    "value": ">  {}".format(", ".join([f"<@&{x}>" for x in roles])) if len(roles) > 0 else ">  None"
                },
                {
                    "name": "**❯ Channels**",
                    "value": ">  {}".format(", ".join([f"<#{x}>" for x in channels])) if len(channels) > 0 else ">  None"
                }
            ])

            await ctx.response.send_message(embed=e)


    @ignore_automod.command(
        name="add",
        description="✅ Adds the given role or channel as ignored for the automoderator"
    )
    @discord.app_commands.describe(
        role="Users with this role will be ignored by the automod",
        channel="Messages within this channel will be ignored by the automod"
    )
    @discord.app_commands.default_permissions(manage_guild=True)
    async def add(
        self, 
        ctx: discord.Interaction,
        role: discord.Role = None,
        channel: discord.TextChannel = None
    ) -> None:
        """
        ignore_automod_add_help
        examples:
        -ignore_automod add @test
        -ignore_automod add #test
        """
        if role == None and channel == None: return self.error(ctx, commands.BadArgument("At least one role or channel required"))
        role_or_channel = [role, channel]

        roles, channels = self.get_ignored_roles_channels(ctx.guild)
        
        added, ignored = [], []
        for e in role_or_channel:
            if isinstance(e, discord.Role):
                if not e.id in roles:
                    roles.append(e.id); added.append(e)
                else:
                    ignored.append(e)
            elif isinstance(e, discord.TextChannel):
                if not e.id in channels:
                    channels.append(e.id); added.append(e)
                else:
                    ignored.append(e)
        
        self.db.configs.multi_update(ctx.guild.id, {
            "ignored_roles_automod": roles,
            "ignored_channels_automod": channels
        })

        e = Embed(
            ctx,
            title="Updated the following roles & channels"
        )
        e.add_fields([
            {
                "name": "**❯ Added roles**",
                "value": ">  {}".format(", ".join(
                    [
                        x.mention for x in added if isinstance(x, discord.Role)
                    ]
                )) if len(
                    [
                        _ for _ in added if isinstance(_, discord.Role)
                    ]
                ) > 0 else ">  None"
            },
            {
                "name": "**❯ Added channels**",
                "value": ">  {}".format(", ".join(
                    [
                        x.mention for x in added if isinstance(x, discord.TextChannel)
                    ]
                )) if len(
                    [
                        _ for _ in added if isinstance(_, discord.TextChannel)
                    ]
                ) > 0 else ">  None"
            },
            {
                "name": "**❯ Ignored**",
                "value": ">  {}".format(", ".join(
                    [
                        x.mention for x in ignored
                    ]
                )) if len(
                    [
                        _ for _ in ignored
                    ]
                ) > 0 else ">  None"
            },
        ])

        await ctx.response.send_message(embed=e)


    @ignore_automod.command(
        name="remove",
        description="❌ Removes the given role or channel as ignored for the automoderator"
    )
    @discord.app_commands.default_permissions(manage_guild=True)
    async def remove(
        self, 
        ctx: discord.Interaction, 
        role: discord.Role = None,
        channel: discord.TextChannel = None
    ) -> None:
        """
        ignore_automod_remove_help
        examples:
        -ignore_automod remove @test
        -ignore_automod remove #test
        """
        if role == None and channel == None: return self.error(ctx, commands.BadArgument("At least one role or channel required"))
        role_or_channel = [role, channel]
        
        roles, channels = self.get_ignored_roles_channels(ctx.guild)

        removed, ignored = [], []
        for e in role_or_channel:
            if isinstance(e, discord.Role):
                if e.id in roles:
                    roles.remove(e.id); removed.append(e)
                else:
                    ignored.append(e)
            elif isinstance(e, discord.TextChannel):
                if e.id in channels:
                    channels.remove(e.id); removed.append(e)
                else:
                    ignored.append(e)
            else:
                ignored.append(e)
        
        self.db.configs.multi_update(ctx.guild.id, {
            "ignored_roles_automod": roles,
            "ignored_channels_automod": channels
        })

        e = Embed(
            ctx,
            title="Updated the following roles & channels"
        )
        e.add_fields([
            {
                "name": "**❯ Removed roles**",
                "value": ">  {}".format(", ".join(
                    [
                        x.mention for x in removed if isinstance(x, discord.Role)
                    ]
                )) if len(
                    [
                        _ for _ in removed if isinstance(_, discord.Role)
                    ]
                ) > 0 else ">  None"
            },
            {
                "name": "**❯ Removed channels**",
                "value": ">  {}".format(", ".join(
                    [
                        x.mention for x in removed if isinstance(x, discord.TextChannel)
                    ]
                )) if len(
                    [
                        _ for _ in removed if isinstance(_, discord.TextChannel)
                    ]
                ) > 0 else ">  None"
            },
            {
                "name": "**❯ Ignored**",
                "value": ">  {}".format(", ".join(
                    [
                        x.mention for x in ignored
                    ]
                )) if len(
                    [
                        _ for _ in ignored
                    ]
                ) > 0 else ">  None"
            },
        ])

        await ctx.response.send_message(embed=e)


async def setup(
    bot: ShardedBotInstance
) -> None: await bot.register_plugin(AutomodPlugin(bot))