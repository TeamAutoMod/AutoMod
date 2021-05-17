


async def run(plugin, ctx, channel):
    plugin.db.configs.update(ctx.guild.id, "action_log_channel", f"{channel.id}")
    await ctx.send(plugin.translator.translate(ctx.guild, "action_log_set", _emote="YES", channel=channel.mention))