from ....utils import Permissions
import traceback



async def run(plugin, ctx, users, warns, reason):
    if reason is None:
        reason = plugin.t(ctx.guild, "no_reason")

    if warns is None:
        warns = 1

    if warns < 1:
        return await ctx.send(plugin.t(ctx.guild, "min_warns", _emote="WARN"))

    if warns > 100:
        return await ctx.send(plugin.t(ctx.guild, "max_warns", _emote="WARN"))
    
    users = list(set(users))
    if len(users) < 1:
        return await ctx.send(plugin.t(ctx.guild, "no_member", _emote="WARN"))

    for user in users:
        if not Permissions.is_allowed(ctx, ctx.author, user):
            await ctx.send(plugin.t(ctx.guild, "warn_not_allowed", _emote="NO"))

        else:
            dm_result, case = await plugin.action_validator.add_warns(
                ctx.message, 
                user, warns, 
                moderator=ctx.author, 
                moderator_id=ctx.author.id,
                user=user, 
                user_id=user.id,
                reason=reason
            )

            await ctx.send(plugin.t(ctx.guild, "user_warned", _emote="YES", user=user, reason=reason, case=case, dm=dm_result, warns=warns))