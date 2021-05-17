


async def run(plugin, ctx):
    plugin.db.configs.update(ctx.guild.id, "antispam", False)
    await ctx.send(plugin.t(ctx.guild, "disabled_module", _emote="YES", module="Antispam"))