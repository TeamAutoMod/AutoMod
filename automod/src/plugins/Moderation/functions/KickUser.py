


async def kickUser(plugin, ctx, user, reason):
    try:
        await ctx.guild.kick(user, reason=reason)
    except Exception as ex:
        return await ctx.send(plugin.t(ctx.guild, "kick_failed", _emote="WARN", error=ex))
    else:
        plugin.bot.ignore_for_event.add("bans_kicks", user.id)
        case = plugin.bot.utils.newCase(ctx.guild, "Kick", user, ctx.author, reason)

        dm_result = await plugin.bot.utils.dmUser(ctx.message, "kick", user, _emote="SHOE", guild_name=ctx.guild.name, reason=reason)
        await ctx.send(plugin.t(ctx.guild, f"user_kicked", _emote="YES", user=user, reason=reason, case=case, dm=dm_result))

        await plugin.action_logger.log(
            ctx.guild, 
            "kick", 
            moderator=ctx.message.author, 
            moderator_id=ctx.message.author.id,
            user=user,
            user_id=user.id,
            reason=reason,
            case=case
        )