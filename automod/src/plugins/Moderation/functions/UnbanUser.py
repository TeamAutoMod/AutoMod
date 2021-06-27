from ....utils import Permissions



async def unbanUser(plugin, ctx, user, reason, softban=False):
    try:
        if not await Permissions.is_banned(ctx, user):
            return await ctx.send(plugin.t(ctx.guild, "target_not_banned", _emote="WARN"))
        await ctx.guild.unban(user=user, reason="Softban")
    except Exception as ex:
        return await ctx.send(plugin.t(ctx.guild, "unban_failed", _emote="NO", error=ex))
    else:
        if softban:
            plugin.bot.ignore_for_event.add("unbans", user.id)
            return
        else:
            plugin.bot.ignore_for_event.add("unbans", user.id)
            case = plugin.bot.utils.newCase(ctx.guild, "Unban", user, ctx.author, reason)
            await ctx.send(plugin.t(ctx.guild, "user_unbanned", _emote="YES", user=user, reason=f"Softban (#{case})", case=case))

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
