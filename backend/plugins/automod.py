import discord
from discord.ext import commands

import re
from toolbox import S as Object
from urllib.parse import urlparse
import logging; log = logging.getLogger()

from . import AutoModPlugin
from .processor import ActionProcessor



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


class AutomodPlugin(AutoModPlugin):
    """Plugin for enforcing automoderator rules"""
    def __init__(self, bot):
        super().__init__(bot)
        self.action_processor = ActionProcessor(bot)


    async def can_act(self, guild, mod, target):
        if not guild.chunked: await guild.chunk(cache=True)
        mod = guild.get_member(mod.id)
        target = guild.get_member(target.id)
        if mod == None or target == None: return False

        return mod.id != target.id \
            and target.id != guild.owner.id \
            and mod.top_role > target.top_role


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


    async def delete_msg(self, msg, warns, reason):
        try:
            await msg.delete()
        except (discord.NotFound, discord.Forbidden):
            pass
        else:
            self.bot.ignore_for_events.append(msg.id)
        finally:
            await self.action_processor.execute(
                msg, 
                msg.guild.me,
                msg.author,
                warns, 
                reason
            )


    async def enforce_rules(self, msg):
        content = msg.content.replace("\\", "")

        config = Object(self.db.configs.get_doc(msg.guild.id))
        rules = config.automod
        filters = config.filters

        if len(rules) < 1: return

        if len(filters) > 0:
            for name in filters:
                f = filters[name]
                parsed = self.parse_filter(f["words"])
                if parsed != None:
                    found = parsed.findall(content)
                    if found:
                        return await self.delete_msg(msg, int(f["warns"]), f"Triggered filter '{name}' with '{', '.join(found)}'")
        
        if hasattr(rules, "invites"):
            found = INVITE_RE.findall(content)
            if found:
                for inv in found:
                    try:
                        invite: discord.Invite = await self.bot.fetch_invite(inv)
                    except discord.NotFound:
                        return await self.delete_msg(msg, rules.invites.warns, f"Advertising ({inv})")
                    if invite.guild == None:
                        return await self.delete_msg(msg, rules.invites.warns, f"Advertising ({inv})")
                    else:
                        if invite.guild == None \
                            or (
                                not invite.guild.id in config.allowed_invites \
                                and invite.guild.id != msg.guild.id
                            ):
                                return await self.delete_msg(msg, rules.invites.warns, f"Advertising ({inv})")
        
        if hasattr(rules, "links"):
            found = LINK_RE.findall(content)
            if found:
                for link in found:
                    url = urlparse(link)
                    if url.hostname in config.black_listed_links:
                        return await self.delete_msg(msg, rules.links.warns, f"Forbidden link ({url.hostname})")

        if hasattr(rules, "files"):
            if len(msg.attachments) > 0:
                forbidden = [
                    k for k, v in {
                        x: x.url.split(".")[-1] for x in msg.attachments
                    } if v.lower() not in ALLOWED_FILE_FORMATS
                ]
                if len(forbidden) > 0:
                    return await self.delete_msg(msg, rules.files.warns, f"Forbidden attachment type ({', '.join(forbidden)})")

        if hasattr(rules, "zalgo"):
            found = ZALGO_RE.search(content)
            if found:
                return await self.delete_msg(msg, rules.zalgo.warns, "Zalgo found")

        if hasattr(rules, "mentions"):
            found = len(MENTION_RE.findall(content))
            if found >= rules.mentions.max:
                return await self.delete_msg(msg, abs(rules.mentions.max - found), f"Spamming mentions ({found})")
    

    @AutoModPlugin.listener()
    async def on_message(self, msg: discord.Message):
        if msg.guild == None: return
        if not msg.guild.chunked: await msg.guild.chunk(cache=True)
        if not await self.can_act(msg.guild, msg.guild.me, msg.author): return

        await self.enforce_rules(msg)


    @AutoModPlugin.listener()
    async def on_message_edit(self, _, msg: discord.Message):
        if msg.guild == None: return
        if not msg.guild.chunked: await msg.guild.chunk(cache=True)
        if not await self.can_act(msg.guild, msg.guild.me, msg.author): return

        await self.enforce_rules(msg)


def setup(bot): bot.register_plugin(AutomodPlugin(bot))