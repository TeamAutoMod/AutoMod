import discord
from discord.ext import commands

import asyncio
import datetime

from .PluginBlueprint import PluginBlueprint
from .Types import Embed



async def logNewVoiceState(plugin, guild, member, before, after):
    _type = "voice_"
    kwargs = {}
    
    if before.channel is None and after.channel is not None:
        _type += "join"
        kwargs.update({
           "color": 0x5cff9d,
            "description": f"**{member}** joined voice channel **{after.channel}**"
        })
    elif before.channel is not None and after.channel is None:
        _type += "join"
        kwargs.update({
           "color": 0xff5c5c,
            "description": f"**{member}** left voice channel **{before.channel}**"
        })
    elif before.channel is not None and after.channel is not None and before.channel is not after.channel:
        _type += "join"
        kwargs.update({
            "color": 0xffdc5c,
            "description": f"**{member}** moved from voice channel **{before.channel}** to **{after.channel}**"
        })
    else:
        return
    
    e = Embed(**kwargs)
    await plugin.action_logger.log(
        guild, 
        _type, 
        _embed=e
    )

class LogsPlugin(PluginBlueprint):
    def __init__(self, bot):
        super().__init__(bot)


    @commands.Cog.listener()
    async def on_message_delete(
        self, 
        message
    ):
        if message.guild is None:
            return
        # Wait 1s before we continue
        # This is so we don't log actions
        # From e.g. message censorships
        await asyncio.sleep(0.5)
        if self.ignore_for_event.has("messages", message.id):
            return self.ignore_for_event.remove("messages", message.id)

        
        if self.db.configs.get(message.guild.id, "message_logging") is False \
        or not isinstance(message.channel, discord.TextChannel) \
        or message.author.id == self.bot.user.id \
        or str(message.channel.id) == self.db.configs.get(message.guild.id, "server_log") \
        or str(message.channel.id) == self.db.configs.get(message.guild.id, "voice_log") \
        or str(message.channel.id) == self.db.configs.get(message.guild.id, "mod_log") \
        or str(message.channel.id) == self.db.configs.get(message.guild.id, "message_log") \
        or message.type != discord.MessageType.default:
            return

        content = " ".join([x.url for x in message.attachments]) + message.content
        e = Embed(
            color=0xff5c5c, 
            timestamp=datetime.datetime.utcnow()
        )
        e.set_author(
            name=f"{message.author} ({message.author.id})",
            icon_url=message.author.display_avatar
        )
        e.add_field(
            name="Content",
            value=content
        )
        e.set_footer(
            text=f"#{message.channel.name}"
        )
        await self.action_logger.log(
            message.guild, 
            "message_deleted", 
            _embed=e
        )


    @commands.Cog.listener()
    async def on_message_edit(
        self, 
        before,
        after
    ):
        if after.guild is None:
            return
        if self.db.configs.get(after.guild.id, "message_logging") is False \
        or not isinstance(after.channel, discord.TextChannel) \
        or after.author.id == self.bot.user.id \
        or str(after.channel.id) == self.db.configs.get(after.guild.id, "server_log") \
        or str(after.channel.id) == self.db.configs.get(after.guild.id, "voice_log") \
        or str(after.channel.id) == self.db.configs.get(after.guild.id, "mod_log") \
        or str(after.channel.id) == self.db.configs.get(after.guild.id, "message_log") \
        or after.type != discord.MessageType.default:
            return
        
        if before.content != after.content and len(after.content) > 0:

            e = Embed(
                color=0xffdc5c, 
                timestamp=after.created_at
            )
            e.set_author(
                name=f"{after.author} ({after.author.id})",
                icon_url=after.author.display_avatar
            )
            e.add_field(
                name="Before",
                value=before.content
            )
            e.add_field(
                name="After",
                value=after.content
            )
            e.set_footer(text=f"#{after.channel.name}")
            await self.action_logger.log(
                after.guild, 
                "message_edited", 
                _embed=e
            )


    @commands.Cog.listener()
    async def on_voice_state_update(
        self,
        member,
        before,
        after
    ):
        guild = member.guild
        if guild is None:
            return
        
        if self.db.configs.get(guild.id, "voice_logging") is False:
            return

        await logNewVoiceState(self, guild, member, before, after)


    @commands.Cog.listener()
    async def on_member_join(
        self,
        member
    ):
        if self.db.configs.get(member.guild.id, "member_logging") is False:
            return

        prior_cases = [f"``#{x['id'].split('-')[1]}``" for x in list(filter(lambda x: x['guild'] == str(member.guild.id) and x['target_id'] == str(member.id), list(self.db.inf.find({}))))]
        
        e = Embed()
        e.set_author(name=f"{member} ({member.id})")
        e.set_thumbnail(url=member.display_avatar)
        if len(prior_cases) > 0:
            e.color = 0xffdc5c
            e.description = self.i18next.t(member.guild, "prior_cases", cases=" | ".join(prior_cases), profile=member.mention, created=round(member.created_at.timestamp()))
            e.set_footer(text="User with prior cases joined")
            await self.action_logger.log(
                member.guild, 
                "member_join_cases",
                _embed=e
            )
        else:
            e.color = 0x5cff9d
            e.description = self.i18next.t(member.guild, "normal_join", profile=member.mention, created=round(member.created_at.timestamp()))
            e.set_footer(text="User joined")
            await self.action_logger.log(
                member.guild, 
                "member_join",
                _embed=e
            )


    @commands.Cog.listener()
    async def on_member_remove(
        self,
        member
    ):
        # Wait 1s before we continue
        # This is so we don't log actions
        # From e.g. bans
        await asyncio.sleep(0.5)
        if self.ignore_for_event.has("bans_kicks", member.id):
            return self.ignore_for_event.remove("bans_kicks", member.id)

        if self.db.configs.get(member.guild.id, "member_logging") is False:
            return

        e = Embed(
            color=0x2f3136,
            description=self.i18next.t(member.guild, "leave", profile=member.mention, joined=round(member.joined_at.timestamp()))
        )
        e.set_author(name=f"{member} ({member.id})")
        e.set_thumbnail(url=member.display_avatar)
        e.set_footer(text="User left")
        await self.action_logger.log(
            member.guild, 
            "member_leave",
            _embed=e
        )

    @commands.Cog.listener()
    async def on_member_unban(
        self,
        guild,
        user
    ):
        # Wait 1s before we continue
        # This is so we don't log actions
        # From e.g. unbans
        await asyncio.sleep(0.5)
        if self.ignore_for_event.has("unbans", user.id):
            return self.ignore_for_event.remove("unbans", user.id)
        
        await self.action_logger.log(
            guild, 
            "manual_unban",
            user=user,
            user_id=user.id
        )



def setup(bot):
    bot.add_cog(LogsPlugin(bot))