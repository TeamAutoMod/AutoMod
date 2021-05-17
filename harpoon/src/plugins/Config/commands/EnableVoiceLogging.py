


async def run(plugin, ctx, channel):
    plugin.db.configs.update(ctx.guild.id, "voice_logging", True)
    plugin.db.configs.update(ctx.guild.id, "voice_log_channel", f"{channel.id}")
    await ctx.send(plugin.t(ctx.guild, "enabled_module_channel", _emote="YES", module="Voice Logging", channel=channel.mention))