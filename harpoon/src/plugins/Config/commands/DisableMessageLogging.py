


async def run(plugin, ctx):
    plugin.db.configs.update(ctx.guild.id, "message_logging", False)
    plugin.db.configs.update(ctx.guild.id, "message_log_channel", "")
    await ctx.send(plugin.t(ctx.guild, "disabled_module", _emote="YES", module="Message Logging"))