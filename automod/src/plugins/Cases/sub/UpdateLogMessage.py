


async def updateLogMessage(plugin, ctx, log_id, case, reason):
    if log_id is None:
        return
    log_channel_id = plugin.db.configs.get(ctx.guild.id, "mod_log")
    if log_channel_id == "":
        return await ctx.send(plugin.i18next.t(ctx.guild, "no_mod_log_set", _emote="NO"))

    log_channel = await plugin.bot.utils.getChannel(ctx.guild, log_channel_id)
    if log_channel is None:
        return await ctx.send(plugin.i18next.t(ctx.guild, "no_mod_log_set", _emote="NO"))

    try:
        msg = await log_channel.fetch_message(int(log_id))
    except Exception:
        return await ctx.send(plugin.i18next.t(ctx.guild, "log_not_found", _emote="NO"))
    if msg is None:
        return await ctx.send(plugin.i18next.t(ctx.guild, "log_not_found", _emote="NO"))
    
    try:
        current = plugin.db.inf.get(f"{ctx.guild.id}-{case}", "reason")
        e = msg.embeds[0]
        e.description = e.description.replace(f"**Reason:** {current}", f"**Reason:** {reason}")
        await msg.edit(embed=e)
    except Exception as ex:
        await ctx.send(plugin.i18next.t(ctx.guild, "log_edit_failed", _emote="NO", exc=ex))
    else:
        plugin.db.inf.update(f"{ctx.guild.id}-{case}", "reason", reason)
        await ctx.send(plugin.i18next.t(ctx.guild, "log_edited", _emote="YES", case=case))