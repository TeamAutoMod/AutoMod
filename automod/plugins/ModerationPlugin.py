import discord
from discord.ext import commands
from discord.ext import tasks

import datetime
import time
import pytz; utc = pytz.UTC

from .WarnsPlugin import WarnsPlugin
from .Types import Reason, DiscordUser, Duration

from utils import Permissions
from utils.Moderation import *



async def unmuteTask(bot):
    while True:
        await asyncio.sleep(10)
        if len(list(bot.db.mutes.find({}))) > 0:
            for m in bot.db.mutes.find():
                if m["ending"] < datetime.datetime.utcnow():
                    guild = bot.get_guild(int(m["id"].split("-")[0]))
                    if guild is not None:

                        target = await bot.utils.getMember(guild, int(m["id"].split("-")[1]))
                        if target is None:
                            target = "Unknown#0000"
                        else:
                            bot.handle_timeout(False, guild, target, None)
                        await bot.action_logger.log(
                            guild,
                            "unmute",
                            user=target,
                            user_id=m["id"].split("-")[1],
                            moderator=bot.user,
                            moderator_id=bot.user.id
                        )
                    bot.db.mutes.delete(m["id"])


class ModerationPlugin(WarnsPlugin):
    def __init__(self, bot):
        super().__init__(bot)
        self.bot.loop.create_task(unmuteTask(bot))
        self.running_cybernukes = list()

    
    def cog_unload(self):
        unmuteTask.stop()

    
    @commands.command()
    @commands.has_guild_permissions(kick_members=True)
    async def kick(
        self, 
        ctx, 
        users: commands.Greedy[discord.Member], 
        *, 
        reason: Reason = None
    ):
        """kick_help"""
        if reason is None:
            reason = self.i18next.t(ctx.guild, "no_reason")

        users = list(set(users))
        if ctx.message.reference != None: 
            users.append(ctx.message.reference.resolved.author)
        if len(users) < 1:
            return await ctx.send(self.i18next.t(ctx.guild, "no_member", _emote="NO"))
        
        msgs = []
        for user in users:
            user = ctx.guild.get_member(user.id)
            if user is None:
                msgs.append(self.i18next.t(ctx.guild, "target_not_on_server", _emote="NO"))
            
            elif not Permissions.is_allowed(ctx, ctx.author, user):
               msgs.append(self.i18next.t(ctx.guild, "kick_not_allowed", _emote="NO", user=user.name))
            else:
                msg = await kickUser(self, ctx, user, reason)
                msgs.append(msg)
        
        await ctx.send("\n".join(msgs))


    @commands.command()
    @commands.has_guild_permissions(ban_members=True)
    async def ban(
        self, 
        ctx, 
        users: commands.Greedy[DiscordUser], 
        *, 
        reason: Reason = None
    ):
        """ban_help"""
        if reason is None:
            reason = self.i18next.t(ctx.guild, "no_reason")

        users = list(set(users))
        if ctx.message.reference != None: 
            users.append(ctx.message.reference.resolved.author)
        if len(users) < 1:
            return await ctx.send(self.i18next.t(ctx.guild, "no_member", _emote="NO"))

        msgs = []
        for user in users:
            user = ctx.guild.get_member(user.id)
            if user is None:
                msgs.append(self.i18next.t(ctx.guild, "target_not_on_server", _emote="NO"))
            
            elif not Permissions.is_allowed(ctx, ctx.author, user):
                msgs.append(self.i18next.t(ctx.guild, "ban_not_allowed", _emote="NO", user=user.name))
            else:
                msg = await banUser(self, ctx, user, reason, "ban", "banned")
                msgs.append(msg)

        await ctx.send("\n".join(msgs))


    @commands.command()
    @commands.has_guild_permissions(ban_members=True)
    async def softban(
        self, 
        ctx, 
        users: commands.Greedy[DiscordUser], 
        *, 
        reason: Reason = None
    ):
        """softban_help"""
        if reason is None:
            reason = self.i18next.t(ctx.guild, "no_reason")

        users = list(set(users))
        if ctx.message.reference != None: 
            users.append(ctx.message.reference.resolved.author)
        if len(users) < 1:
            return await ctx.send(self.i18next.t(ctx.guild, "no_member", _emote="NO"))

        msgs = []
        for user in users:
            user = ctx.guild.get_member(user.id)
            if user is None:
                msgs.append(self.i18next.t(ctx.guild, "target_not_on_server", _emote="NO"))
            
            elif not Permissions.is_allowed(ctx, ctx.author, user):
                msgs.append(self.i18next.t(ctx.guild, "ban_not_allowed", _emote="NO", user=user.name))
            else:
                msg = await banUser(self, ctx, user, reason, "softban", "softbanned", days=7)
                await unbanUser(self, ctx, user, "Softban", softban=True)
                msgs.append(msg)

        await ctx.send("\n".join(msgs))


    @commands.command(aliases=["hackban"])
    @commands.has_guild_permissions(ban_members=True)
    async def forceban(
        self, 
        ctx, 
        users: commands.Greedy[DiscordUser], 
        *, 
        reason: Reason = None
    ):
        """forceban_help"""
        if reason is None:
            reason = self.i18next.t(ctx.guild, "no_reason")
        
        users = list(set(users))
        if ctx.message.reference != None: 
            users.append(ctx.message.reference.resolved.author)
        if len(users) < 1:
            return await ctx.send(self.i18next.t(ctx.guild, "no_member", _emote="NO"))

        msgs = []
        for user in users:
            msg = await banUser(self, ctx, user, reason, "forceban", "forcebanned")
            msgs.append(msg)

        await ctx.send("\n".join(msgs))


    @commands.command()
    @commands.has_guild_permissions(ban_members=True)
    async def mute(
        self, 
        ctx, 
        user: discord.Member,
        length: Duration, 
        *, 
        reason: Reason = None
    ):
        """mute_help"""
        if reason is None:
            reason = self.i18next.t(ctx.guild, "no_reason")
        
        if not Permissions.is_allowed(ctx, ctx.author, user):
            return await ctx.send(self.i18next.t(ctx.guild, "mute_not_allowed", _emote="NO", user=user.name))
        
        await muteUser(self, ctx, user, length, reason)


    @commands.command()
    @commands.has_guild_permissions(ban_members=True)
    async def unmute(
        self, 
        ctx, 
        user: DiscordUser,
    ):
        """unmute_help"""
        await unmuteUser(self, ctx, user)


    @commands.command()
    @commands.has_guild_permissions(ban_members=True)
    async def unban(
        self, 
        ctx, 
        user: DiscordUser,
        *,
        reason: Reason = None
    ):
        """unban_help"""
        if reason is None:
            reason = self.i18next.t(ctx.guild, "no_reason")
        await unbanUser(self, ctx, user, reason)


    @commands.group()
    @commands.has_guild_permissions(manage_messages=True)
    async def clean(
        self,
        ctx,
    ):
        """clean_help"""
        if ctx.invoked_subcommand is None:
            await ctx.invoke(self.bot.get_command("help"), query="clean")


    @clean.command(name="all")
    @commands.has_guild_permissions(manage_messages=True)
    async def _all(
        self,
        ctx,
        amount: int = None
    ):
        """clean_all_help"""
        if amount is None:
            amount = 10
        
        if amount < 1:
            return await ctx.send(self.i18next.t(ctx.guild, "amount_too_small", _emote="NO"))

        if amount > 300:
            return await ctx.send(self.i18next.t(ctx.guild, "amount_too_big", _emote="NO"))

        await cleanMessages(
            self, 
            ctx, 
            "All", 
            amount, 
            lambda m: True, 
            check_amount=amount
        )
            

    @clean.command()
    @commands.has_guild_permissions(manage_messages=True)
    async def bots(
        self,
        ctx,
        amount: int = None
    ):
        """clean_bots_help"""
        if amount is None:
            amount = 50
        
        if amount < 1:
            return await ctx.send(self.i18next.t(ctx.guild, "amount_too_small", _emote="NO"))

        if amount > 300:
            return await ctx.send(self.i18next.t(ctx.guild, "amount_too_big", _emote="NO"))

        await cleanMessages(
            self, 
            ctx, 
            "Bots", 
            amount, 
            lambda m: m.author.bot
        )


    @clean.command()
    @commands.has_guild_permissions(manage_messages=True)
    async def user(
        self,
        ctx,
        users: commands.Greedy[DiscordUser],
        amount: int = None
    ):
        """clean_user_help"""
        if amount is None:
            amount = 50

        users = list(set(users))
        if ctx.message.reference != None: 
            users.append(ctx.message.reference.resolved.author)
        if len(users) < 1:
            return await ctx.send(self.i18next.t(ctx.guild, "no_member", _emote="NO"))
        
        if amount < 1:
            return await ctx.send(self.i18next.t(ctx.guild, "amount_too_small", _emote="NO"))

        if amount > 300:
            return await ctx.send(self.i18next.t(ctx.guild, "amount_too_big", _emote="NO"))

        await cleanMessages(
            self, 
            ctx, 
            "User", 
            amount, 
            lambda m: any(m.author.id == u.id for u in users)
        )


    @clean.command(usage="clean last <duration>")
    @commands.has_guild_permissions(manage_messages=True)
    async def last(
        self,
        ctx,
        duration: Duration,
        excess = ""
    ):
        """clean_last_help"""
        if duration.unit is None:
            duration.unit = excess

        after = datetime.datetime.utcfromtimestamp(time.time() - duration.to_seconds(ctx))
        await cleanMessages(
            self, 
            ctx, 
            "Last", 
            500, 
            lambda m: True,
            after=after
        )


    @clean.command()
    @commands.has_guild_permissions(manage_messages=True)
    async def until(
        self,
        ctx,
        message: discord.Message
    ):
        """clean_until_help"""
        await cleanMessages(
            self, 
            ctx, 
            "Until", 
            500, 
            lambda m: True,
            after=discord.Object(message.id)
        )


    @clean.command()
    @commands.has_guild_permissions(manage_messages=True)
    async def between(
        self,
        ctx,
        start: discord.Message,
        end: discord.Message
    ):
        """clean_between_help"""
        await cleanMessages(
            self, 
            ctx, 
            "Between", 
            500, 
            lambda m: True,
            before=discord.Object(end.id),
            after=discord.Object(start.id)
        )



def setup(bot): bot.add_cog(ModerationPlugin(bot))