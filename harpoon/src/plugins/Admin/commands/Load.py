


async def run(plugin, ctx, _plugin):
    _plugin_ = plugin.bot.get_cog(_plugin)
    if _plugin_ is None:
        return await ctx.send(plugin.translator.translate(ctx.guild, "plugin_not_found", _emote="WARN"))
    else:
        try:
            plugin.bot.load_extension(_plugin_.path)
        except Exception as ex:
            await ctx.send(plugin.translator.translate(ctx.guild, "plugin_load_failed", _emote="WARN", exc=ex))
        else:
            await ctx.send(plugin.translator.translate(ctx.guild, "plugin_loaded", _emote="YES", plugin=str(_plugin_)))