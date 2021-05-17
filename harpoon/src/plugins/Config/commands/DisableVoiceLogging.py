


async def run(plugin, ctx):
    plugin.db.configs.update(ctx.guild.id, "voice_logging", False)
    plugin.db.configs.update(ctx.guild.id, "voice_log_channel", "")
    await ctx.send(plugin.t(ctx.guild, "disabled_module", _emote="YES", module="Voice Logging"))