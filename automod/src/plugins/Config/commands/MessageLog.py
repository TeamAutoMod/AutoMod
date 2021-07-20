


async def run(plugin, ctx, channel):
    if isinstance(channel, str):
        if channel.lower() == "off":
            plugin.db.configs.update(ctx.guild.id, "message_logging", False)
            plugin.db.configs.update(ctx.guild.id, "message_log", "")
            return await ctx.send(plugin.t(ctx.guild, "log_off", _emote="YES", opt="Message Logs"))
        else:
            return await ctx.send(plugin.t(ctx.guild, "invalid_channel", _emote="NO"))
    
    plugin.db.configs.update(ctx.guild.id, "message_logging", True)
    plugin.db.configs.update(ctx.guild.id, "message_log", f"{channel.id}")
    await ctx.send(plugin.t(ctx.guild, "log_on", _emote="YES", opt="Message Logs", channel=channel.mention))