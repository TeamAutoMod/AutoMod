import discord
from discord.ext import commands

import asyncio
import datetime
import topgg
import logging; log = logging.getLogger()

from . import AutoModPlugin
from .processor import LogProcessor
from ..schemas import GuildConfig
from ..types import Embed



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
        or msg.type != discord.MessageType.default:
            return
        
        content = " ".join([x.url for x in msg.attachments]) + msg.content
        e = Embed(
            color=0xff5c5c, 
            timestamp=datetime.datetime.utcnow(),
            description=content[:2000] # idek the limits tbh
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


def setup(bot): bot.register_plugin(InternalPlugin(bot))