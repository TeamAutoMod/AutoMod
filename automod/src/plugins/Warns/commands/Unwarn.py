from ....utils import Permissions



async def run(plugin, ctx, users, warns, reason):
    if reason is None:
        reason = plugin.t(ctx.guild, "no_reason")

    if warns is None:
        warns = 1
    else:
        try:
            warns = int(warns)
        except ValueError:
            reason = warns
            warns = 1

    if warns < 1:
        return await ctx.send(plugin.t(ctx.guild, "min_warns", _emote="NO"))

    if warns > 100:
        return await ctx.send(plugin.t(ctx.guild, "max_warns", _emote="NO"))
    
    users = list(set(users))
    if len(users) < 1:
        return await ctx.send(plugin.t(ctx.guild, "no_member", _emote="NO"))

    for user in users:
        if not Permissions.is_allowed(ctx, ctx.author, user):
            await ctx.send(plugin.t(ctx.guild, "unwarn_not_allowed", _emote="NO"))

        else:
            _id = f"{ctx.guild.id}-{user.id}"
            if not plugin.db.warns.exists(_id):
                plugin.db.warns.insert(plugin.schemas.Warn(_id, 0))
                return await ctx.send(plugin.t(ctx.guild, "no_warns", _emote="NO"))
            else:
                current = plugin.db.warns.get(_id, "warns")
                if current < 1:
                    return await ctx.send(plugin.t(ctx.guild, "no_warns", _emote="NO"))
                new = (current - warns) if (current - warns) >= 0 else 0
                plugin.db.warns.update(_id, "warns", new)
            
            case = plugin.bot.utils.newCase(ctx.guild, "Unwarn", user, ctx.author, reason)

            dm_result = await plugin.bot.utils.dmUser(ctx.message, "unwarn", user, _emote="ANGEL", warns=warns, guild_name=ctx.guild.name, reason=reason)
            await ctx.send(plugin.t(ctx.guild, "user_unwarned", _emote="YES", user=user, reason=reason, case=case, dm=dm_result, warns=warns))

            await plugin.action_logger.log(
                ctx.guild, 
                "unwarn",
                user=user,
                user_id=user.id,
                warns=warns,
                old_warns=current,
                new_warns=new,
                moderator=ctx.author,
                moderator_id=ctx.author.id,
                reason=reason,
                case=case,
                dm=dm_result
            )