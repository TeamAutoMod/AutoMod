import traceback



async def warnUser(plugin, ctx, user, reason):
    warn_id = f"{ctx.guild.id}-{user.id}"
    warns = plugin.db.warns.get(warn_id, "warns")

    case = plugin.bot.utils.newCase(ctx.guild, "Warn", user, ctx.author, reason)
    kwargs = {
        "user": user,
        "user_id": user.id,
        "moderator": ctx.message.author,
        "moderator_id": ctx.message.author.id,
        "reason": reason, 
        "case": case
    }

    if warns is None:
        plugin.db.warns.insert(plugin.schemas.Warn(warn_id, 1))
        await plugin.action_logger.log(ctx.guild, "warn", **kwargs)
    elif (warns+1) >= plugin.db.configs.get(ctx.guild.id, "warn_threshold"):
        confirm = await ctx.prompt(plugin.t(ctx.guild, "max_warns_prompt", _emote="WARN", warns=warns), timeout=15)
        if not confirm:
            return await ctx.send(plugin.t(ctx.guild, "aborting"))
        
        plugin.db.warns.update(warn_id, "warns", 0)

        kwargs.update({"reason": "Automatic punishment escalation (Max warns)", "moderator": plugin.bot.user, "moderator_id": plugin.bot.user.id})
        await plugin.action_validator.figure_it_out(
            ctx.message, 
            ctx.guild, 
            user, 
            "max_warns", 
            **kwargs
        )
    else:
        plugin.db.warns.update(warn_id, "warns", (warns+1))
        await plugin.action_logger.log(ctx.guild, "warn", **kwargs)
    
    dm_result = await plugin.bot.utils.dmUser(ctx, "warn", user, guild_name=ctx.guild.name, reason=reason)
    await ctx.send(plugin.t(ctx.guild, "user_warned", _emote="YES", user=user, reason=reason, case=case, dm=dm_result))