


async def run(plugin, ctx, _plugin):
    _plugin_ = plugin.bot.get_cog(_plugin)
    if _plugin_ is None:
        return await ctx.send(plugin.t(ctx.guild, "plugin_not_found", _emote="WARN"))
    else:
        try:
            plugin.bot.reload_extension(_plugin_.path)
        except Exception as ex:
            await ctx.send(plugin.t(ctx.guild, "plugin_reload_failed", _emote="WARN", exc=ex))
        else:
            await ctx.send(plugin.t(ctx.guild, "plugin_reloaded", _emote="YES", plugin=str(_plugin_)))