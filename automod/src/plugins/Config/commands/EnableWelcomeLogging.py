


async def run(plugin, ctx, channel):
    plugin.db.configs.update(ctx.guild.id, "member_logging", True)
    plugin.db.configs.update(ctx.guild.id, "join_log_channel", f"{channel.id}")
    await ctx.send(plugin.translator.translate(ctx.guild, "enabled_module_channel", _emote="YES", module="Welcome Logging", channel=channel.mention))