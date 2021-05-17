


async def run(plugin, ctx):
    plugin.db.configs.update(ctx.guild.id, "antispam", True)
    await ctx.send(plugin.translator.translate(ctx.guild, "enabled_module_no_channel", _emote="YES", module="Antispam"))