


async def run(plugin, ctx, channel):
    if isinstance(channel, str):
        if channel.lower() == "off":
            plugin.db.configs.update(ctx.guild.id, "server_logging", True)
            plugin.db.configs.update(ctx.guild.id, "server_log", "")
            return await ctx.send(plugin.i18next.t(ctx.guild, "log_off", _emote="YES", opt="Server Logs"))
        else:
            return await ctx.send(plugin.i18next.t(ctx.guild, "invalid_channel", _emote="NO"))
    
    plugin.db.configs.update(ctx.guild.id, "server_logging", True)
    plugin.db.configs.update(ctx.guild.id, "server_log", f"{channel.id}")
    await ctx.send(plugin.i18next.t(ctx.guild, "log_on", _emote="YES", opt="Server Logs", channel=channel.mention))