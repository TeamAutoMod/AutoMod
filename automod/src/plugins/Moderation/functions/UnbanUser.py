


async def unbanUser(plugin, ctx, user, reason, softban=False):
    try:
        await ctx.guild.unban(user=user, reason="Softban")
    except Exception as ex:
        return await ctx.send(plugin.translator.translate(ctx.guild, "unban_failed", _emote="WARN", error=ex))
    else:
        if softban:
            plugin.bot.ignore_for_event.add("bans_kicks", user.id)
            return
        else:
            plugin.bot.ignore_for_event.add("bans_kicks", user.id)
            case = plugin.bot.utils.newCase(ctx.guild, "Unban", user, ctx.author, reason)
            await ctx.send(plugin.translator.translate(ctx.guild, "user_unbanned", _emote="YES", user=user, reason=f"Softban (#{case})", case=case))

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
