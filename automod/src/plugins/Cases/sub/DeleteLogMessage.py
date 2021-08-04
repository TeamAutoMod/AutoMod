


async def deleteLogMessage(plugin, ctx, log_id):
    if log_id is None:
        return
    log_channel_id = plugin.db.configs.get(ctx.guild.id, "mod_log")
    if log_channel_id is "":
        return

    log_channel = await plugin.bot.utils.getChannel(ctx.guild, log_channel_id)
    if log_channel is None:
        return

    msg = await log_channel.fetch_message(int(log_id))
    if msg is None:
        return
    
    try:
        await msg.delete()
    except Exception:
        pass