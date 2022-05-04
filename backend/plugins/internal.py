import discord
from discord.ext import commands
from discord import AuditLogAction

import asyncio
import datetime
import topgg
from toolbox import S as Object
from typing import Callable, List, Union, Tuple, TypeVar
import logging; log = logging.getLogger()

from . import AutoModPlugin, ShardedBotInstance
from .processor import LogProcessor
from ..schemas import GuildConfig
from ..types import Embed



T = TypeVar("T")


SERVER_LOG_EVENTS = {
    "role_created": {
        "emote": "CREATE",
        "color": 0x5cff9d,
        "audit_log_action": AuditLogAction.role_create,
        "text": "Role created"
    },
    "role_deleted": {
        "emote": "DELETE",
        "color": 0xff5c5c,
        "audit_log_action": AuditLogAction.role_delete,
        "text": "Role deleted"
    },
    "role_updated": {
        "emote": "UPDATE",
        "color": 0xffdc5c,
        "audit_log_action": AuditLogAction.role_update,
        "text": "Role updated",
        "extra_text": "**Change:** {change}"
    },

    "channel_created": {
        "emote": "CREATE",
        "color": 0x5cff9d,
        "audit_log_action": AuditLogAction.channel_create,
        "text": "Channel created",
        "extra_text": "**Type:** {_type}"
    },
    "channel_deleted": {
        "emote": "DELETE",
        "color": 0xff5c5c,
        "audit_log_action": AuditLogAction.channel_delete,
        "text": "Channel deleted",
        "extra_text": "**Type:** {_type}"
    },
    "channel_updated": {
        "emote": "UPDATE",
        "color": 0xffdc5c,
        "audit_log_action": AuditLogAction.channel_update,
        "text": "Channel updated",
        "extra_text": "**Type:** {_type} \n**Change:** {change} "
    },

    "thread_created": {
        "emote": "CREATE",
        "color": 0x5cff9d,
        "audit_log_action": AuditLogAction.thread_create,
        "text": "Thread created"
    },
    "thread_deleted": {
        "emote": "DELETE",
        "color": 0xff5c5c,
        "audit_log_action": AuditLogAction.thread_delete,
        "text": "Thread deleted"
    },
    "thread_updated": {
        "emote": "UPDATE",
        "color": 0xffdc5c,
        "audit_log_action": AuditLogAction.thread_update,
        "text": "Thread updated",
        "extra_text": "**Change:** {change}"
    },

    "emoji_created": {
        "emote": "CREATE",
        "color": 0x5cff9d,
        "audit_log_action": AuditLogAction.emoji_create,
        "text": "Emoji created",
        "extra_text": "**Showcase:** {showcase}"
    },
    "emoji_deleted": {
        "emote": "DELETE",
        "color": 0xff5c5c,
        "audit_log_action": AuditLogAction.emoji_delete,
        "text": "Emoji deleted"
    },

    "sticker_created": {
        "emote": "CREATE",
        "color": 0x5cff9d,
        "audit_log_action": AuditLogAction.sticker_create,
        "text": "Sticker created",
        "extra_text": "**Showcase:** {showcase}"
    },
    "sticker_deleted": {
        "emote": "DELETE",
        "color": 0xff5c5c,
        "audit_log_action": AuditLogAction.sticker_delete,
        "text": "Sticker deleted"
    },

    "nick_added": {
        "emote": "CREATE",
        "color": 0x5cff9d,
        "audit_log_action": AuditLogAction.member_update,
        "text": "Nickname added",
        "extra_text": "**New:** {change}"
    },
    "nick_removed": {
        "emote": "DELETE",
        "color": 0xff5c5c,
        "audit_log_action": AuditLogAction.member_update,
        "text": "Nickname removed",
        "extra_text": "**Old:** {change}"
    },
    "nick_updated": {
        "emote": "UPDATE",
        "color": 0xffdc5c,
        "audit_log_action": AuditLogAction.member_update,
        "text": "Nickname updated",
        "extra_text": "**Change:** {change}"
    },
    "added_role": {
        "emote": "CREATE",
        "color": 0x5cff9d,
        "audit_log_action": AuditLogAction.member_role_update,
        "text": "Role added",
        "extra_text": "**Role:** {change}"
    },
    "removed_role": {
        "emote": "DELETE",
        "color": 0xff5c5c,
        "audit_log_action": AuditLogAction.member_role_update,
        "text": "Role removed",
        "extra_text": "**Role:** {change}"
    },
    "username_updated": {
        "emote": "UPDATE",
        "color": 0xffdc5c,
        "audit_log_action": AuditLogAction.member_update,
        "text": "Username updated",
        "extra_text": "**Change:** {change}"
    },

    "joined_voice": {
        "emote": "CREATE",
        "color": 0x5cff9d,
        "audit_log_action": AuditLogAction.member_move,
        "text": "Joined voice channel",
        "extra_text": "**Channel:** <#{channel}>"
    },
    "left_voice": {
        "emote": "DELETE",
        "color": 0xff5c5c,
        "audit_log_action": AuditLogAction.member_move,
        "text": "Left voice channel",
        "extra_text": "**Channel:** <#{channel}>"
    },
    "switched_voice": {
        "emote": "SWITCH",
        "color": 0xffdc5c,
        "audit_log_action": AuditLogAction.member_move,
        "text": "Switched voice channel",
        "extra_text": "**Change:** <#{before}> → <#{after}>"
    },

    "used_command": {
        "emote": "WRENCH",
        "color": 0x5cff9d,
        "audit_log_action": None,
        "text": "Used command",
        "extra_text": "**Command:** {command} \n**Arguments:** {arguments} \n**Channel:** <#{channel}>"
    },
    "used_custom_command": {
        "emote": "TEXT",
        "color": 0x2f3136,
        "audit_log_action": None,
        "text": "Used custom command",
        "extra_text": "**Command:** {command} \n**Channel:** <#{channel}>"
    }
}


class InternalPlugin(AutoModPlugin):
    """Plugin for internal/log events"""
    def __init__(self, bot: ShardedBotInstance) -> None:
        super().__init__(bot)
        self.log_processor = LogProcessor(bot)
        if bot.config.top_gg_token != "":
            self.topgg = topgg.DBLClient(
                bot,
                bot.config.top_gg_token,
                autopost=True,
                post_shard_count=True
            )


    async def _find_in_audit_log(self, guild: discord.Guild, action: discord.AuditLogAction, check: Callable) -> Union[discord.Member, discord.User, None]:
        try:
            if guild.me == None: return None

            e = None
            if guild.me.guild_permissions.view_audit_log:
                try:
                    async for _e in guild.audit_logs(
                        action=action,
                        limit=10
                    ): 
                        if check(_e) == True:
                            if e == None or _e.id > e.id:
                                e = _e
                except discord.Forbidden:
                    pass
            
            if e != None:
                return e.user
            else:
                return None
        except (
            asyncio.TimeoutError, asyncio.CancelledError
        ): return None


    async def find_in_audit_log(self, guild: discord.Guild, action: discord.AuditLogAction, check: Callable) -> Union[discord.Member, discord.User, None]:
        try:
            return await asyncio.wait_for(
                self._find_in_audit_log(guild, action, check),
                timeout=10
            )
        except (
            asyncio.TimeoutError, asyncio.CancelledError
        ): return None


    async def server_log_embed(self, action: discord.AuditLogAction, guild: discord.Guild, obj: T, check_for_audit: Union[Callable, bool], **text_kwargs) -> Embed:
        data = Object(SERVER_LOG_EVENTS[action])
        e = Embed(
            color=data.color
        )
        if check_for_audit != False:
            mod = await self.find_in_audit_log(
                guild,
                data.audit_log_action,
                check_for_audit
            )
            
            by_field = ""
            if mod != None:
                mod = guild.get_member(mod.id)
                if mod != None:
                    if mod.guild_permissions.manage_messages == True:
                        by_field = "Moderator"
                    else:
                        rid = self.db.configs.get(guild.id, "mod_role")
                        if rid != "":
                            if int(rid) in [x.id for x in mod.roles]:
                                by_field = "Moderator"
                            else:
                                by_field = "User"
                        else:
                            by_field = "User"
                else:
                    by_field = "User"
            else:
                by_field = "User"

            e.description = "{} **{}:** {} ({}) \n\n**{}:** {}\n{}".format(
                self.bot.emotes.get(data.emote),
                data.text,
                obj.name if not hasattr(obj, "banner") else obj.mention,
                obj.id,
                by_field,
                f"{mod.mention} ({mod.id})" if mod != None else "Unknown",
                str(data.extra_text).format(**text_kwargs) if len(text_kwargs) > 0 else ""
            )
        else:
            e.description = "{} **{}:** {} ({}) \n\n{}".format(
                self.bot.emotes.get(data.emote),
                data.text,
                obj.name if not hasattr(obj, "banner") else obj.mention,
                obj.id,
                str(data.extra_text).format(**text_kwargs) if len(text_kwargs) > 0 else ""
            )

        return e


    def get_ignored_roles_channels(self, guild: discord.Guild) -> Tuple[list, list]:
        roles, channels = self.db.configs.get(guild.id, "ignored_roles_log"), self.db.configs.get(guild.id, "ignored_channels_log")
        return roles, channels


    @AutoModPlugin.listener()
    async def on_guild_join(self, guild: discord.Guild) -> None:
        log.info(f"📥 Joined guild: {guild.name} ({guild.id})")

        try:
            await guild.chunk(cache=True)
        except Exception as ex:
            log.warn(f"❌ Failed to chunk members for guild {guild.id} upon joining - {ex}")
        finally:
            if not self.db.configs.exists(guild.id):
                self.db.configs.insert(GuildConfig(guild, self.config.default_prefix))


    @AutoModPlugin.listener()
    async def on_guild_remove(self, guild: discord.Guild) -> None:
        if guild == None: return
        log.info(f"📤 Removed from guild: {guild.name} ({guild.id})")
        if self.db.configs.exists(guild.id):
            self.db.cases.multi_delete({"guild": f"{guild.id}"})
            self.db.configs.delete(guild.id)


    @AutoModPlugin.listener()
    async def on_message_delete(self, msg: discord.Message) -> None:
        if msg.guild == None: return

        await asyncio.sleep(0.3) # wait a bit before checking ignore_for_events
        if msg.id in self.bot.ignore_for_events:
            return self.bot.ignore_for_events.remove(msg.id)
        
        # I hate this
        cfg = self.db.configs.get_doc(msg.guild.id)
        if cfg["message_log"] == "" \
        or not isinstance(msg.channel, discord.TextChannel) \
        or msg.author.id == self.bot.user.id \
        or str(msg.channel.id) == cfg["server_log"] \
        or str(msg.channel.id) == cfg["mod_log"] \
        or str(msg.channel.id) == cfg["message_log"] \
        or str(msg.channel.id) == cfg["join_log"] \
        or str(msg.channel.id) == cfg["member_log"] \
        or str(msg.channel.id) == cfg["voice_log"] \
        or str(msg.channel.id) == cfg["bot_log"] \
        or msg.type != discord.MessageType.default:
            return

        roles, channels = self.get_ignored_roles_channels(msg.guild)
        if msg.channel.id in channels: return
        if any(x in [i.id for i in msg.author.roles] for x in roles): return
        
        content = " ".join([x.url for x in msg.attachments]) + msg.content
        if content == "": return
        e = Embed(
            color=0xff5c5c, 
            timestamp=datetime.datetime.utcnow(),
            description=content[:2000] # idk the limits tbh
        )
        e.set_author(
            name="{0.name}#{0.discriminator} ({0.id})".format(msg.author),
            icon_url=msg.author.display_avatar
        )
        e.set_footer(
            text="#{}".format(msg.channel.name)
        )

        await self.log_processor.execute(msg.guild, "message_deleted", **{
            "_embed": e
        })


    @AutoModPlugin.listener()
    async def on_message_edit(self, b: discord.Message, a: discord.Message) -> None:
        if a.guild == None: return

        cfg = self.db.configs.get_doc(a.guild.id)
        if cfg["message_log"] == "" \
        or not isinstance(a.channel, discord.TextChannel) \
        or a.author.id == self.bot.user.id \
        or str(a.channel.id) == cfg["server_log"] \
        or str(a.channel.id) == cfg["mod_log"] \
        or str(a.channel.id) == cfg["message_log"] \
        or str(a.channel.id) == cfg["join_log"] \
        or str(a.channel.id) == cfg["member_log"] \
        or str(a.channel.id) == cfg["voice_log"] \
        or str(a.channel.id) == cfg["bot_log"] \
        or a.type != discord.MessageType.default:
            return

        roles, channels = self.get_ignored_roles_channels(a.guild)
        if a.channel.id in channels: return
        if any(x in [i.id for i in a.author.roles] for x in roles): return
        
        if b.content != a.content and len(a.content) > 0:
            e = Embed(
                color=0xffdc5c, 
                timestamp=a.created_at
            )
            e.set_author(
                name="{0.name}#{0.discriminator} ({0.id})".format(a.author),
                icon_url=a.author.display_avatar
            )
            e.add_field(
                name="Before",
                value=b.content
            )
            e.add_field(
                name="After",
                value=a.content
            )
            e.set_footer(
                text="#{}".format(a.channel.name)
            )

            await self.log_processor.execute(a.guild, "message_edited", **{
                "_embed": e
            })


    @AutoModPlugin.listener()
    async def on_member_join(self, user: discord.Member) -> None:
        e = Embed(
            color=0x5cff9d,
            description=self.locale.t(user.guild, "user_joined", profile=user.mention, created=round(user.created_at.timestamp()))
        )
        e.set_thumbnail(
            url=user.display_avatar
        )
        e.set_footer(
            text="User joined"
        )
        await self.log_processor.execute(user.guild, "user_joined", **{
            "_embed": e
        })


    @AutoModPlugin.listener()
    async def on_member_remove(self, user: discord.Member) -> None:
        await asyncio.sleep(0.3)
        if user.id in self.bot.ignore_for_events:
            return self.bot.ignore_for_events.remove(user.id)
        if user.id == self.bot.user.id: return
        
        e = Embed(
            color=0x2f3136,
            description=self.locale.t(user.guild, "user_left", profile=user.mention, joined=round(user.joined_at.timestamp()))
        )
        e.set_thumbnail(
            url=user.display_avatar
        )
        e.set_footer(
            text="User left"
        )
        await self.log_processor.execute(user.guild, "user_left", **{
            "_embed": e
        })

    
    @AutoModPlugin.listener()
    async def on_guild_role_create(self, role: discord.Role) -> None:
        embed = await self.server_log_embed(
            "role_created",
            role.guild,
            role,
            lambda x: x.target.id == role.id
        )

        await self.log_processor.execute(role.guild, "role_created", **{
            "_embed": embed
        })


    @AutoModPlugin.listener()
    async def on_guild_role_delete(self, role: discord.Role) -> None:
        embed = await self.server_log_embed(
            "role_deleted",
            role.guild,
            role,
            lambda x: x.target.id == role.id
        )

        await self.log_processor.execute(role.guild, "role_deleted", **{
            "_embed": embed
        })


    @AutoModPlugin.listener()
    async def on_guild_role_update(self, b: discord.Role, a: discord.Role) -> None:
        roles, _ = self.get_ignored_roles_channels(a.guild)
        if a.id in roles: return

        change = ""
        if b.name != a.name:
            change += "Name (``{}`` → ``{}``)".format(
                a.name,
                b.name
            )
        if b.permissions != a.permissions:
            new = "Permissions"
            if len(change) < 1:
                change += new
            else:
                change += f" & {new}"
        if b.color != a.color:
            new = "Color (``{}`` → ``{}``)".format(
                b.color,
                a.color
            )
            if len(change) < 1:
                change += new
            else:
                change += f" & {new}"
        
        if len(change) < 1: return

        embed = await self.server_log_embed(
            "role_updated",
            a.guild,
            b,
            lambda x: x.target.id == a.id,
            change=change
        )

        await self.log_processor.execute(a.guild, "role_updated", **{
            "_embed": embed
        })


    @AutoModPlugin.listener()
    async def on_guild_channel_create(self, channel: discord.abc.GuildChannel) -> None:
        embed = await self.server_log_embed(
            "channel_created",
            channel.guild,
            channel,
            lambda x: x.target.id == channel.id,
            _type=str(channel.type).replace("_", " ").title()
        )

        await self.log_processor.execute(channel.guild, "channel_created", **{
            "_embed": embed
        })


    @AutoModPlugin.listener()
    async def on_guild_channel_delete(self, channel: discord.abc.GuildChannel) -> None:
        _, channels = self.get_ignored_roles_channels(channel.guild)
        if channel.id in channels: return

        embed = await self.server_log_embed(
            "channel_deleted",
            channel.guild,
            channel,
            lambda x: x.target.id == channel.id,
            _type=str(channel.type).replace("_", " ").title()
        )

        await self.log_processor.execute(channel.guild, "channel_deleted", **{
            "_embed": embed
        })


    @AutoModPlugin.listener()
    async def on_guild_channel_update(self, b: discord.abc.GuildChannel, a: discord.abc.GuildChannel) -> None:
        _, channels = self.get_ignored_roles_channels(b.guild)
        if a.id in channels: return

        if a.position != b.position: return

        change = ""
        if b.name != a.name:
            change += "Name (``{}`` → ``{}``)".format(
                b.name,
                a.name
            )
        
        new = ""
        for k, v in b.overwrites.items():
            if k in a.overwrites:
                if a.overwrites[k] != v:
                    new = "Permissions updated"
            else:
                new = "Permissions created"
        
        if new != "":
            if len(change) < 1:
                change += new
            else:
                change += f" & {new}"
        
        if len(change) < 1: return

        embed = await self.server_log_embed(
            "channel_updated",
            a.guild,
            a,
            lambda x: x.target.id == b.id,
            change=change,
            _type=str(a.type).replace("_", " ").title()
        )

        await self.log_processor.execute(a.guild, "channel_updated", **{
            "_embed": embed
        })

    
    @AutoModPlugin.listener()
    async def on_guild_emojis_update(self, _, b: List[discord.Emoji], a: List[discord.Emoji]) -> None:
        if len(b) > len(a):
            action = "emoji_deleted"
            emoji = [x for x in b if x not in a][0]
            extra_text = {}
        elif len(b) < len(a):
            action = "emoji_created"
            emoji = [x for x in a if x not in b][0]
            extra_text = {"showcase": f"<:{emoji.name}:{emoji.id}>"}
        else:
            return

        if emoji.guild == None: return

        embed = await self.server_log_embed(
            action,
            emoji.guild,
            emoji,
            lambda x: x.target.id == emoji.id,
            **extra_text
        )

        await self.log_processor.execute(emoji.guild, action, **{
            "_embed": embed
        })


    @AutoModPlugin.listener()
    async def on_guild_stickers_update(self, _, b: List[discord.GuildSticker], a: List[discord.GuildSticker]) -> None:
        if len(b) > len(a):
            action = "sticker_deleted"
            sticker = [x for x in b if x not in a][0]
            extra_text = {}
        elif len(b) < len(a):
            action = "sticker_created"
            sticker = [x for x in a if x not in b][0]
            extra_text = {"showcase": f"[Here]({sticker.url})"}
        else:
            return

        if sticker.guild == None: return

        embed = await self.server_log_embed(
            action,
            sticker.guild,
            sticker,
            lambda x: x.target.id == sticker.id,
            **extra_text
        )

        await self.log_processor.execute(sticker.guild, action, **{
            "_embed": embed
        })


    @AutoModPlugin.listener()
    async def on_thread_create(self, thread: discord.Thread) -> None:
        _, channels = self.get_ignored_roles_channels(thread.guild)
        if thread.parent.id in channels: return

        embed = await self.server_log_embed(
            "thread_created",
            thread.guild,
            thread,
            lambda x: x.target.id == thread.id
        )

        await self.log_processor.execute(thread.guild, "thread_created", **{
            "_embed": embed
        })
        await self.bot.join_thread(thread)

    
    @AutoModPlugin.listener()
    async def on_thread_delete(self, thread: discord.Thread) -> None:
        _, channels = self.get_ignored_roles_channels(thread.guild)
        if thread.parent.id in channels:
            return

        embed = await self.server_log_embed(
            "thread_deleted",
            thread.guild,
            thread,
            lambda x: x.target.id == thread.id
        )

        await self.log_processor.execute(thread.guild, "thread_deleted", **{
            "_embed": embed
        })


    @AutoModPlugin.listener()
    async def on_thread_update(self, b: discord.Thread, a: discord.Thread) -> None:
        _, channels = self.get_ignored_roles_channels(b.guild)
        if b.parent.id in channels or a.parent.id in channels: return

        change = ""
        if b.name != a.name:
            change += "Name (``{}`` → ``{}``)".format(
                b.name,
                a.name
            )
        if b.archived != a.archived:
            new = "Archived" if a.archived == True else "Unarchived"
            if len(change) < 1:
                change += new
            else:
                change += f" & {new}"
        
        if len(change) < 1: return

        embed = await self.server_log_embed(
            "thread_updated",
            a.guild,
            a,
            lambda x: x.target.id == a.id,
            change=change
        )

        await self.log_processor.execute(a.guild, "thread_updated", **{
            "_embed": embed
        })


    @AutoModPlugin.listener()
    async def on_member_update(self, b: discord.Member, a: discord.Member) -> None:
        if not a.guild.chunked: await a.guild.chunk(cache=True)

        roles, _ = self.get_ignored_roles_channels(a.guild)
        if any(x in [i.id for i in a.roles] for x in roles): return
        for r in [*b.roles, *a.roles]:
            if r.id in roles: return

        key = ""
        change = ""
        check_audit = False
        if b.nick != a.nick:
            if b.nick == None and a.nick != None:
                change += "``{}``".format(
                    a.nick
                )
                key = "nick_added"
            elif b.nick != None and a.nick == None:
                change += "``{}``".format(
                    b.nick
                )
                key = "nick_removed"
            else:
                change += "``{}`` → ``{}``".format(
                    b.nick,
                    a.nick
                )
                key = "nick_updated"
            
        if b.roles != a.roles:
            check_audit = True
            added_roles = [x.mention for x in a.roles if x not in b.roles]
            removed_roles = [x.mention for x in b.roles if x not in a.roles]


            if len(added_roles) > 0:
                key = "added_role"
                change = ", ".join(added_roles)
            elif len(removed_roles) > 0:
                key = "removed_role"
                change = ", ".join(removed_roles)
        
        if key == "": return

        embed = await self.server_log_embed(
            key,
            a.guild,
            a,
            False if check_audit == False else lambda x: x.target.id == a.id,
            change=change
        )

        await self.log_processor.execute(a.guild, "member_updated", **{
            "_embed": embed
        })


    @AutoModPlugin.listener()
    async def on_user_update(self, b: discord.User, a: discord.User) -> None:
        change = ""
        if b.name != a.name or b.discriminator != a.discriminator:
            change += "``{}`` → ``{}``".format(
                f"{b.name}#{b.discriminator}",
                f"{a.name}#{a.discriminator}"
            )
        
        if len(change) < 1: return

        for guild in self.bot.guilds:
            m = guild.get_member(a.id)
            if m != None:
                roles, _ = self.get_ignored_roles_channels(m.guild)
                if any(x in [i.id for i in m.roles] for x in roles): return

                embed = await self.server_log_embed(
                    "username_updated",
                    guild,
                    a,
                    False,
                    change=change
                )

                await self.log_processor.execute(guild, "member_updated", **{
                    "_embed": embed
                })


    @AutoModPlugin.listener()
    async def on_voice_state_update(self, user: discord.Member, b: discord.VoiceState, a: discord.VoiceState) -> None:
        if user.guild == None: return

        roles, channels = self.get_ignored_roles_channels(user.guild)
        if any(x in [i.id for i in user.roles] for x in roles): return

        key = ""
        text = {}
        if b.channel != a.channel:
            if b.channel == None and a.channel != None:
                if a.channel.id not in channels:
                    key = "joined_voice"
                    text.update({
                        "channel": a.channel.id
                    })
            elif b.channel != None and a.channel == None:
                if b.channel.id not in channels:
                    key = "left_voice"
                    text.update({
                        "channel": b.channel.id
                    })
            elif b.channel != None and a.channel != None:
                if b.channel.id not in channels and a.channel.id not in channels:
                    key = "switched_voice"
                    text.update({
                        "before": b.channel.id,
                        "after": a.channel.id
                    })
            else:
                pass
            if key != "":
                embed = await self.server_log_embed(
                    key,
                    user.guild,
                    user,
                    False,
                    **text
                )

                await self.log_processor.execute(user.guild, key, **{
                    "_embed": embed
                })


    @AutoModPlugin.listener()
    async def on_command_completion(self, ctx: commands.Context):
        if ctx.guild == None: return
        if ctx.command == None: return

        roles, channels = self.get_ignored_roles_channels(ctx.guild)
        if ctx.channel.id in channels: return
        if any(x in [i.id for i in ctx.author.roles] for x in roles): return

        _args = [f"``{x if not isinstance(x, discord.Message) else x.id}``" for x in ctx.args[2:] if x != None]
        if len(_args) < 1:
            args = "None"
        else:
            args = ", ".join(_args)

        embed = await self.server_log_embed(
            "used_command",
            ctx.guild,
            ctx.author,
            False,
            command=ctx.command.qualified_name,
            channel=ctx.channel.id,
            arguments=args
        )
        await self.log_processor.execute(ctx.guild, "used_command", **{
            "_embed": embed
        })

    
    @AutoModPlugin.listener()
    async def on_custom_command_completion(self, msg: discord.Message, name: str) -> None:
        if msg.guild == None: return

        roles, channels = self.get_ignored_roles_channels(msg.guild)
        if msg.channel.id in channels: return
        if any(x in [i.id for i in msg.author.roles] for x in roles): return

        embed = await self.server_log_embed(
            "used_custom_command",
            msg.guild,
            msg.author,
            False,
            command=name,
            channel=msg.channel.id,
        )
        await self.log_processor.execute(msg.guild, "used_custom_command", **{
            "_embed": embed
        })


    @AutoModPlugin.listener()
    async def on_member_unban(self, guild: discord.Guild, user: discord.User) -> None:
        await asyncio.sleep(0.3) # wait a bit before checking ignore_for_events
        if user.id in self.bot.ignore_for_events:
            return self.bot.ignore_for_events.remove(user.id)

        await self.log_processor.execute(guild, "manual_unban", **{
            "user": user,
            "user_id": user.id
        })


    @AutoModPlugin.listener()
    async def on_autopost_success(self):
        log.info(f"📬 Posted server count ({self.topgg.guild_count}) and shard count ({len(self.bot.shards)})")


async def setup(bot) -> None: await bot.register_plugin(InternalPlugin(bot))