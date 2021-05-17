


async def run(plugin, ctx):
    plugin.db.configs.update(ctx.guild.id, "member_logging", False)
    plugin.db.configs.update(ctx.guild.id, "join_log_channel", "")
    await ctx.send(plugin.translator.translate(ctx.guild, "disabled_module", _emote="YES", module="Message Logging"))