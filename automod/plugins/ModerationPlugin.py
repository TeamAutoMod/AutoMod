import discord
from discord.ext import commands

import datetime
import asyncio
import time
import pytz
utc = pytz.UTC

from .PluginBlueprint import PluginBlueprint
from .Types import Reason, DiscordUser, Duration, Embed

from utils import Permissions
from utils.Views import ConfirmView



async def banUser(plugin, ctx, user, reason, log_type, ban_type, days=0):
    try:
        if await Permissions.is_banned(ctx, user):
            return await ctx.send(plugin.i18next.t(ctx.guild, "target_already_banned", _emote="WARN"))
        await ctx.guild.ban(user, reason=reason, delete_message_days=days)
    except Exception as ex:
        return await ctx.send(plugin.i18next.t(ctx.guild, "ban_failed", _emote="NO", error=ex))
    else:
        plugin.bot.ignore_for_event.add("bans_kicks", user.id)

        case = plugin.bot.utils.newCase(ctx.guild, log_type.capitalize(), user, ctx.author, reason)
        dm_result = await plugin.bot.utils.dmUser(
            ctx.message, 
            log_type, 
            user, 
            _emote="HAMMER", 
            color=0xff5c5c,
            moderator=ctx.message.author, 
            guild_name=ctx.guild.name, 
            reason=reason
        )

        await ctx.send(plugin.i18next.t(ctx.guild, f"user_{ban_type}", _emote="YES", user=user, reason=reason, case=case))

        await plugin.action_logger.log(
            ctx.guild, 
            log_type, 
            moderator=ctx.message.author, 
            moderator_id=ctx.message.author.id,
            user=user,
            user_id=user.id,
            reason=reason,
            case=case,
            dm=dm_result
        )


async def kickUser(plugin, ctx, user, reason):
    try:
        if await Permissions.is_banned(ctx, user):
            return await ctx.send(plugin.i18next.t(ctx.guild, "target_already_banned", _emote="WARN"))
        await ctx.guild.kick(user, reason=reason)
    except Exception as ex:
        return await ctx.send(plugin.i18next.t(ctx.guild, "kick_failed", _emote="NO", error=ex))
    else:
        plugin.bot.ignore_for_event.add("bans_kicks", user.id)
        case = plugin.bot.utils.newCase(ctx.guild, "Kick", user, ctx.author, reason)

        dm_result = await plugin.bot.utils.dmUser(
            ctx.message, 
            "kick", 
            user, 
            _emote="SHOE", 
            color=0xf79554,
            moderator=ctx.message.author, 
            guild_name=ctx.guild.name, 
            reason=reason
        )
        await ctx.send(plugin.i18next.t(ctx.guild, f"user_kicked", _emote="YES", user=user, reason=reason, case=case))

        await plugin.action_logger.log(
            ctx.guild, 
            "kick", 
            moderator=ctx.message.author, 
            moderator_id=ctx.message.author.id,
            user=user,
            user_id=user.id,
            reason=reason,
            case=case,
            dm=dm_result
        )


async def muteUser(plugin, ctx, user, length, reason):
    if length.unit is None:
        length.unit = "m"

    prefix = plugin.bot.get_guild_prefix(ctx.guild)
    mute_role_id = plugin.db.configs.get(ctx.guild.id, "mute_role")
    if mute_role_id == "":
        return await ctx.send(plugin.i18next.t(ctx.guild, "no_mute_role", _emote="NO", prefix=prefix))
    
    mute_role = await plugin.bot.utils.getRole(ctx.guild, mute_role_id)
    if mute_role is None:
        return await ctx.send(plugin.i18next.t(ctx.guild, "no_mute_role", _emote="NO", prefix=prefix))

    mute_id = f"{ctx.guild.id}-{user.id}"
    # Check if user is already muted. If so, should we extend their mute?
    if plugin.db.mutes.exists(mute_id):

        async def confirm(interaction):
            until = (plugin.db.mutes.get(mute_id, "ending") + datetime.timedelta(seconds=length.to_seconds(ctx)))
            plugin.db.mutes.update(mute_id, "ending", until)

            await interaction.response.edit_message(
                content=plugin.i18next.t(ctx.guild, "mute_extended", _emote="YES", user=user, until=f"<t:{round(until.timestamp())}>", reason=reason), 
                embed=None, 
                view=None
            )
            await plugin.action_logger.log(
                ctx.guild, 
                "mute_extended", 
                moderator=ctx.message.author, 
                moderator_id=ctx.message.author.id,
                user=user,
                user_id=user.id,
                expiration=f"<t:{round(until.timestamp())}:D>",
                reason=reason
            )
            if not mute_role in user.roles:
                try:
                    await user.add_roles(mute_role)
                except Exception:
                    return
            return

        async def cancel(interaction):
            e = Embed(
                description=plugin.i18next.t(ctx.guild, "aborting")
            )
            await interaction.response.edit_message(embed=e, view=None)

        async def timeout():
            if message is not None:
                e = Embed(
                    description=plugin.i18next.t(ctx.guild, "aborting")
                )
                await message.edit(embed=e, view=None)

        def check(interaction):
            return interaction.user.id == ctx.author.id and interaction.message.id == message.id

        e = Embed(
            description=plugin.i18next.t(ctx.guild, "already_muted_description")
        )
        message = await ctx.send(
            embed=e,
            view=ConfirmView(
                ctx.guild.id, 
                on_confirm=confirm, 
                on_cancel=cancel, 
                on_timeout=timeout,
                check=check
            )
        )

    else:
        if ctx.guild.me.top_role.position > mute_role.position:
            seconds = length.to_seconds(ctx)
            if seconds >= 1:
                try:
                    await user.add_roles(mute_role)
                except Exception as ex:
                    await ctx.send(plugin.i18next.t(ctx.guild, "mute_failed", _emote="NO", error=ex))
                else:
                    until = (datetime.datetime.utcnow() + datetime.timedelta(seconds=seconds))
                    plugin.db.mutes.insert(plugin.schemas.Mute(ctx.guild.id, user.id, until))

                    case = plugin.bot.utils.newCase(ctx.guild, "Mute", user, ctx.author, reason)

                    dm_result = await plugin.bot.utils.dmUser(
                        ctx.message, 
                        "mute", 
                        user, 
                        _emote="MUTE", 
                        color=0xffdc5c,
                        moderator=ctx.message.author,
                        guild_name=ctx.guild.name, 
                        until=f"<t:{round(until.timestamp())}>", 
                        reason=reason
                    )
                    await ctx.send(plugin.i18next.t(ctx.guild, "user_muted", _emote="YES", user=user, until=f"<t:{round(until.timestamp())}>", reason=reason, case=case))
                    
                    await plugin.action_logger.log(
                        ctx.guild, 
                        "mute", 
                        moderator=ctx.message.author, 
                        moderator_id=ctx.message.author.id,
                        user=user,
                        user_id=user.id,
                        expiration=f"<t:{round(until.timestamp())}:D>",
                        reason=reason, 
                        case=case,
                        dm=dm_result
                    )
            else:
                raise commands.BadArgument("number_too_small")
        else:
            await ctx.send(plugin.i18next.t(ctx.guild, "role_too_high", _emote="NO"))


async def finishCleaning(plugin, channel_id):
    await asyncio.sleep(1)
    del plugin.cleaning[channel_id]


async def cleanMessages(plugin, ctx, category, amount, predicate, before=None, after=None, check_amount=None):
    if not hasattr(plugin, "cleaning"):
        plugin.cleaning = dict()
    count = 0

    if ctx.channel.id in plugin.cleaning:
        return await ctx.send(plugin.i18next.t(ctx.guild, "already_cleaning", _emote="WARN"))
    plugin.cleaning[ctx.channel.id] = set()

    try:
        def check(msg):
            nonlocal count
            match = predicate(msg) and count < amount
            if match:
                count += 1
            return match

        try:
            deleted = await ctx.channel.purge(
                limit=min(amount, 500) if check_amount is None else check_amount, 
                check=check, 
                before=before if before else None,
                after=after
            )
        except discord.Forbidden:
            raise
        except discord.NotFound:
            await asyncio.sleep(1)
            await ctx.send(plugin.i18next.t(ctx.guild, "already_cleaned", _emote="WARN"))
        
        else:
            try:
                await ctx.message.delete()
            except Exception:
                pass
            finally:
                await ctx.send(plugin.i18next.t(ctx.guild, "messages_deleted", _emote="YES", count=len(deleted), plural="" if len(deleted) == 1 else "s"), delete_after=5)
        
    except Exception as ex:
        plugin.bot.loop.create_task(finishCleaning(plugin, ctx.channel.id))
        await ctx.send(plugin.i18next.t(ctx.guild, "clean_fail", _emote="NO", exc=ex))
    
    plugin.bot.loop.create_task(finishCleaning(plugin, ctx.channel.id))



restrictions = {
    "embed": {
        "role": "embed_role",
        "action": "Embed restriction",
        "success": "embed restricted"
    },
    "emoji": {
        "role": "emoji_role",
        "action": "Emoji restriction",
        "success": "emoji restricted"
    },
    "tag": {
        "role": "tag_role",
        "action": "Tag restriction",
        "success": "tag restricted"
    }
}
async def restrictUser(plugin, ctx, restriction, user, reason):
    restriction = restriction.lower()
    prefix = plugin.bot.get_guild_prefix(ctx.guild)

    if restriction not in restrictions:
        return await ctx.send(plugin.i18next.t(ctx.guild, "invalid_restriction"))
    
    d = restrictions[restriction]
    role_id = plugin.db.configs.get(ctx.guild.id, d["role"])
    if role_id == "":
        return await ctx.send(plugin.i18next.t(ctx.guild, "no_restrict_role", prefix=prefix))

    role = await plugin.bot.utils.getRole(ctx.guild, int(role_id))
    if role is None:
        return await ctx.send(plugin.i18next.t(ctx.guild, "no_restrict_role", prefix=prefix))

    if role in user.roles:
        return await ctx.send(plugin.i18next.t(ctx.guild, "already_restricted", _emote="NO", success=d["success"]))

    try:
        await user.add_roles(role)
    except Exception as ex:
        return await ctx.send(plugin.i18next.t(ctx.guild, "restrict_failed", _emote="NO", error=ex))
    else:
        case = plugin.bot.utils.newCase(ctx.guild, d["action"], user, ctx.author, reason)
        dm_result = await plugin.bot.utils.dmUser(
            ctx.message, 
            "restrict", 
            user, 
            _emote="RESTRICT", 
            color=0xffdc5c,
            moderator=ctx.message.author,
            guild_name=ctx.guild.name, 
            success=d["success"],
            reason=reason
        )
        
        await ctx.send(plugin.i18next.t(ctx.guild, "user_restricted", _emote="YES", user=user, success=d["success"], case=case))

        await plugin.action_logger.log(
            ctx.guild, 
            "restrict", 
            moderator=ctx.message.author, 
            moderator_id=ctx.message.author.id,
            user=user,
            user_id=user.id,
            action=d["action"],
            reason=reason, 
            case=case,
            dm=dm_result
        )

async def unbanUser(plugin, ctx, user, reason, softban=False):
    try:
        if not await Permissions.is_banned(ctx, user):
            return await ctx.send(plugin.i18next.t(ctx.guild, "target_not_banned", _emote="NO"))
        await ctx.guild.unban(user=user, reason="Softban")
    except Exception as ex:
        return await ctx.send(plugin.i18next.t(ctx.guild, "unban_failed", _emote="NO", error=ex))
    else:
        if softban:
            plugin.bot.ignore_for_event.add("unbans", user.id)
            return
        else:
            plugin.bot.ignore_for_event.add("unbans", user.id)
            case = plugin.bot.utils.newCase(ctx.guild, "Unban", user, ctx.author, reason)
            await ctx.send(plugin.i18next.t(ctx.guild, "user_unbanned", _emote="YES", user=user, reason=f"Softban (#{case})", case=case))

            await plugin.action_logger.log(
                ctx.guild, 
                "unban", 
                moderator=ctx.message.author, 
                moderator_id=ctx.message.author.id,
                user=user,
                user_id=user.id,
                reason=reason,
                case=case
            )
    

async def unmuteUser(plugin, ctx, user):
    mute_id = f"{ctx.guild.id}-{user.id}"
    if not plugin.db.mutes.exists(mute_id):
        return await ctx.send(plugin.i18next.t(ctx.guild, "not_muted", _emote="NO"))

    plugin.db.mutes.delete(mute_id)
    await ctx.send(plugin.i18next.t(ctx.guild, "mute_lifted", _emote="YES", user=user))

    # Can we remove the role?
    try:
        mute_role_id = plugin.db.configs.get(ctx.guild.id, "mute_role")
        mute_role = await plugin.bot.utils.getRole(ctx.guild, mute_role_id)
        member = ctx.guild.get_member(user.id)
        await member.remove_roles(mute_role)
    except Exception:
        pass
    finally:
        await plugin.action_logger.log(
            ctx.guild, 
            "manual_unmute", 
            moderator=ctx.message.author, 
            moderator_id=ctx.message.author.id,
            user=user,
            user_id=user.id
        )


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

                            try:
                                mute_role_id = bot.db.configs.get(guild.id, "mute_role")
                                mute_role = await bot.utils.getRole(guild, int(mute_role_id))

                                await target.remove_roles(mute_role)
                            except Exception:
                                pass
                        
                        await bot.action_logger.log(
                            guild,
                            "unmute",
                            user=target,
                            user_id=m["id"].split("-")[1]
                        )
                    bot.db.mutes.delete(m["id"])


class ModerationPlugin(PluginBlueprint):
    def __init__(self, bot):
        super().__init__(bot)
        self.bot.loop.create_task(unmuteTask(self.bot))
        self.running_cybernukes = list()

    
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
        if len(users) < 1:
            return await ctx.send(self.i18next.t(ctx.guild, "no_member", _emote="NO"))
        for user in users:
            user = ctx.guild.get_member(user.id)
            if user is None:
                await ctx.send(self.i18next.t(ctx.guild, "target_not_on_server", _emote="NO"))
            
            elif not Permissions.is_allowed(ctx, ctx.author, user):
                await ctx.send(self.i18next.t(ctx.guild, "kick_not_allowed", _emote="NO"))
            else:
                await kickUser(self, ctx, user, reason)


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
        if len(users) < 1:
            return await ctx.send(self.i18next.t(ctx.guild, "no_member", _emote="NO"))
        for user in users:
            user = ctx.guild.get_member(user.id)
            if user is None:
                await ctx.send(self.i18next.t(ctx.guild, "target_not_on_server", _emote="NO"))
            
            elif not Permissions.is_allowed(ctx, ctx.author, user):
                await ctx.send(self.i18next.t(ctx.guild, "ban_not_allowed", _emote="NO"))
            else:
                await banUser(self, ctx, user, reason, "ban", "banned")


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
        if len(users) < 1:
            return await ctx.send(self.i18next.t(ctx.guild, "no_member", _emote="NO"))
        for user in users:
            user = ctx.guild.get_member(user.id)
            if user is None:
                await ctx.send(self.i18next.t(ctx.guild, "target_not_on_server", _emote="NO"))
            
            elif not Permissions.is_allowed(ctx, ctx.author, user):
                await ctx.send(self.i18next.t(ctx.guild, "ban_not_allowed", _emote="NO"))
            else:
                await banUser(self, ctx, user, reason, "softban", "softbanned", days=7)
                await unbanUser(self, ctx, user, "Softban", softban=True)


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
        if len(users) < 1:
            return await ctx.send(self.i18next.t(ctx.guild, "no_member", _emote="NO"))
        for user in users:
            await banUser(self, ctx, user, reason, "forceban", "forcebanned")


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
            return await ctx.send(self.i18next.t(ctx.guild, "mute_not_allowed", _emote="NO"))
        

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



    @commands.command()
    @commands.has_guild_permissions(manage_messages=True)
    async def purge(
        self,
        ctx,
        amount: int = None
    ):
        """purge_help"""
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


    @commands.group()
    @commands.has_guild_permissions(manage_messages=True)
    async def clean(
        self,
        ctx,
    ):
        """clean_help"""
        if ctx.invoked_subcommand is None:
            await ctx.invoke(self.bot.get_command("help"), query="clean")
            

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


    @commands.command()
    @commands.has_guild_permissions(ban_members=True)
    async def cybernuke(
        self, 
        ctx, 
        join: Duration,
        age: Duration
    ):
        """cybernuke_help"""
        if ctx.guild.id in self.running_cybernukes:
            return await ctx.send(self.i18next.t(ctx.guild, "cybernuke_running", _emote="NO"))

        if join.unit is None:
            join.unit = "m"
        if age.unit is None:
            age.unit = "m"

        join = utc.localize(datetime.datetime.utcfromtimestamp(time.time() - join.to_seconds(ctx)))
        age = utc.localize(datetime.datetime.utcfromtimestamp(time.time() - age.to_seconds(ctx)))

        targets = list(filter(lambda x: x.joined_at >= join and x.created_at >= age, ctx.guild.members))
        if len(targets) < 1:
            return await ctx.send(self.i18next.t(ctx.guild, "no_targets", _emote="NO"))
        if len(targets) > 100:
            return await ctx.send(self.i18next.t(ctx.guild, "too_many_targets", _emote="NO"))


        message = None
        async def cancel(interaction):
            self.running_cybernukes.remove(ctx.guild.id)
            e = Embed(
                description=self.i18next.t(ctx.guild, "aborting")
            )
            await interaction.response.edit_message(embed=e, view=None)

        async def timeout():
            if message is not None:
                e = Embed(
                    description=self.i18next.t(ctx.guild, "aborting")
                )
                await message.edit(embed=e, view=None)

        def check(interaction):
            return interaction.user.id == ctx.author.id and interaction.message.id == message.id

        async def confirm(interaction):
            case = self.bot.utils.newCase(ctx.guild, "Cybernuke", targets[0], ctx.author, f"Cybernuke ({len(targets)})")
            banned = 0
            for i, t in enumerate(targets):
                reason = f"Cybernuke ``({i+1}/{len(targets)})``"

                if not Permissions.is_allowed(ctx, ctx.author, t):
                    pass
                else:
                    try:
                        await ctx.guild.ban(t, reason=reason)
                    except Exception:
                        pass
                    else:
                        banned += 1
                        dm_result = await self.bot.utils.dmUser(
                            ctx.message, 
                            "cybernuke", 
                            t, 
                            _emote="HAMMER", 
                            color=0xff5c5c,
                            moderator=ctx.message.author, 
                            guild_name=ctx.guild.name, 
                            reason=reason
                        )

                        await self.action_logger.log(
                            ctx.guild,
                            "cybernuke",
                            moderator=ctx.message.author, 
                            moderator_id=ctx.message.author.id,
                            user=t,
                            user_id=t.id,
                            reason=reason,
                            case=case,
                            dm=dm_result
                        )
            
            self.running_cybernukes.remove(ctx.guild.id)
            await interaction.response.edit_message(
                content=self.i18next.t(ctx.guild, "users_cybernuked", _emote="YES", banned=banned, total=len(targets), case=case), 
                embed=None, 
                view=None
            )

        self.running_cybernukes.append(ctx.guild.id)
        e = Embed(
            description=self.i18next.t(ctx.guild, "cybernuke_description", targets=len(targets))
        )
        message = await ctx.send(
            embed=e,
            view=ConfirmView(
                ctx.guild.id, 
                on_confirm=confirm, 
                on_cancel=cancel, 
                on_timeout=timeout,
                check=check
            )
        )


    @commands.command()
    @commands.has_guild_permissions(kick_members=True)
    async def restrict(
        self,
        ctx,
        restriction: str,
        user: discord.Member,
        *,
        reason: Reason = None
    ):
        """restrict_help"""
        if reason is None:
            reason = self.i18next.t(ctx.guild, "no_reason")
        
        if not Permissions.is_allowed(ctx, ctx.author, user):
            return await ctx.send(self.i18next.t(ctx.guild, "restrict_not_allowed", _emote="NO"))

        await restrictUser(self, ctx, restriction, user, reason)


def setup(bot):
    bot.add_cog(ModerationPlugin(bot))