import discord
from discord import AuditLogAction

import asyncio
import datetime
import topgg
from toolbox import S as Object
from typing import List
import logging; log = logging.getLogger()

from . import AutoModPlugin
from .processor import LogProcessor
from ..schemas import GuildConfig
from ..types import Embed



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
        "text": "Channel deleted"
    },
    "channel_updated": {
        "emote": "UPDATE",
        "color": 0xffdc5c,
        "audit_log_action": AuditLogAction.channel_update,
        "text": "Channel updated",
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
}
class InternalPlugin(AutoModPlugin):
    """Plugin for internal/log events"""
    def __init__(self, bot):
        super().__init__(bot)
        self.log_processor = LogProcessor(bot)
        if bot.config.top_gg_token != "":
            self.topgg = topgg.DBLClient(
                bot,
                bot.config.top_gg_token,
                autopost=True,
                post_shard_count=True
            )


    async def _find_in_audit_log(self, guild, action, check):
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


    async def find_in_audit_log(self, guild, action, check):
        try:
            return await asyncio.wait_for(
                self._find_in_audit_log(guild, action, check),
                timeout=10
            )
        except (
            asyncio.TimeoutError, asyncio.CancelledError
        ): return None


    async def server_log_embed(self, action, guild, obj, check_for_audit, **text_kwargs):
        data = Object(SERVER_LOG_EVENTS[action])
        mod = await self.find_in_audit_log(
            guild,
            data.audit_log_action,
            check_for_audit
        )

        e = Embed(
            color=data.color,
            description="{} **{}:** {} ({}) \n\n**Moderator:** {}\n{}".format(
                self.bot.emotes.get(data.emote),
                data.text,
                obj.name,
                obj.id,
                f"{mod.mention} ({mod.id})" if mod != None else "Unknown",
                str(data.extra_text).format(**text_kwargs) if len(text_kwargs) > 0 else ""
            )
        )

        return e


    @AutoModPlugin.listener()
    async def on_guild_join(self, guild: discord.Guild):
        log.info(f"Joined guild: {guild.name} ({guild.id})")

        try:
            await guild.chunk(cache=True)
        except Exception as ex:
            log.warn(f"Failed to chunk members for guild {guild.id} upon joining - {ex}")
        finally:
            if not self.db.configs.exists(guild.id):
                self.db.configs.insert(GuildConfig(guild, self.config.default_prefix))


    @AutoModPlugin.listener()
    async def on_guild_remove(self, guild: discord.Guild):
        if guild == None: return
        log.info(f"Removed from guild: {guild.name} ({guild.id})")
        if self.db.configs.exists(guild.id):
            self.db.cases.multi_delete({"guild": f"{guild.id}"})
            self.db.configs.delete(guild.id)


    @AutoModPlugin.listener()
    async def on_message_delete(self, msg: discord.Message):
        if msg.guild == None: return

        await asyncio.sleep(0.3) # wait a bit before checking ignore_for_events
        if msg.id in self.bot.ignore_for_events:
            return self.bot.ignore_for_events.remove(msg.id)
        
        # I hate this
        if self.db.configs.get(msg.guild.id, "message_log") == "" \
        or not isinstance(msg.channel, discord.TextChannel) \
        or msg.author.id == self.bot.user.id \
        or str(msg.channel.id) == self.db.configs.get(msg.guild.id, "server_log") \
        or str(msg.channel.id) == self.db.configs.get(msg.guild.id, "mod_log") \
        or str(msg.channel.id) == self.db.configs.get(msg.guild.id, "message_log") \
        or str(msg.channel.id) == self.db.configs.get(msg.guild.id, "join_log") \
        or msg.type != discord.MessageType.default:
            return
        
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
    async def on_message_edit(self, b: discord.Message, a: discord.Message):
        if a.guild == None: return

        if self.db.configs.get(a.guild.id, "message_log") == "" \
        or not isinstance(a.channel, discord.TextChannel) \
        or a.author.id == self.bot.user.id \
        or str(a.channel.id) == self.db.configs.get(a.guild.id, "server_log") \
        or str(a.channel.id) == self.db.configs.get(a.guild.id, "mod_log") \
        or str(a.channel.id) == self.db.configs.get(a.guild.id, "message_log") \
        or a.type != discord.MessageType.default:
            return
        
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
    async def on_member_join(self, user: discord.Member):
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
    async def on_member_remove(self, user: discord.Member):
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
    async def on_guild_role_create(self, role: discord.Role):
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
    async def on_guild_role_delete(self, role: discord.Role):
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
    async def on_guild_role_update(self, b: discord.Role, a: discord.Role):
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
    async def on_guild_channel_create(self, channel: discord.abc.GuildChannel):
        embed = await self.server_log_embed(
            "channel_created",
            channel.guild,
            channel,
            lambda x: x.target.id == channel.id,
            _type=str(channel.type)
        )

        await self.log_processor.execute(channel.guild, "channel_created", **{
            "_embed": embed
        })


    @AutoModPlugin.listener()
    async def on_guild_channel_delete(self, channel: discord.abc.GuildChannel):
        embed = await self.server_log_embed(
            "channel_deleted",
            channel.guild,
            channel,
            lambda x: x.target.id == channel.id
        )

        await self.log_processor.execute(channel.guild, "channel_deleted", **{
            "_embed": embed
        })


    @AutoModPlugin.listener()
    async def on_guild_channel_update(self, b: discord.abc.GuildChannel, a: discord.abc.GuildChannel):
        change = ""
        if b.name != a.name:
            change += "Name (``{}`` → ``{}``)".format(
                b.name,
                a.name
            )
        if b.overwrites != a.overwrites:
            new = "Permissions"
            if len(change) < 1:
                change += new
            else:
                change += f" & {new}"
        
        if len(change) < 1: return

        embed = await self.server_log_embed(
            "channel_updated",
            a.guild,
            a,
            lambda x: x.target.id == a.id,
            change=change
        )

        await self.log_processor.execute(a.guild, "channel_updated", **{
            "_embed": embed
        })

    
    @AutoModPlugin.listener()
    async def on_guild_emojis_update(self, _, b: List[discord.Emoji], a: List[discord.Emoji]):
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
    async def on_member_unban(self, guild: discord.Guild, user: discord.User):
        await asyncio.sleep(0.3) # wait a bit before checking ignore_for_events
        if user.id in self.bot.ignore_for_events:
            return self.bot.ignore_for_events.remove(user.id)

        await self.log_processor.execute(guild, "manual_unban", **{
            "user": user,
            "user_id": user.id
        })


    @AutoModPlugin.listener()
    async def on_autopost_success(self):
        log.info(f"Posted server count ({self.topgg.guild_count}) and shard count ({len(self.bot.shards)})")


async def setup(bot): await bot.register_plugin(InternalPlugin(bot))
