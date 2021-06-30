


async def run(plugin, ctx, channel):
    if isinstance(channel, str):
        if channel.lower() == "off":
            plugin.db.configs.update(ctx.guild.id, "voice_log", "")
            plugin.db.configs.update(ctx.guild.id, "voice_logging", False)
            return await ctx.send(plugin.t(ctx.guild, "log_off", _emote="YES", opt="Voice Logs"))
        else:
            return await ctx.send(plugin.t(ctx.guild, "invalid_channel", _emote="NO"))
    
    plugin.db.configs.update(ctx.guild.id, "voice_log", f"{channel.id}")
    plugin.db.configs.update(ctx.guild.id, "voice_logging", True)
    await ctx.send(plugin.t(ctx.guild, "log_on", _emote="YES", opt="Voice Logs", channel=channel.mention))