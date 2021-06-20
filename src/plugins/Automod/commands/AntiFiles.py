


async def run(plugin, ctx, warns):
    if warns < 1:
        return await ctx.send(plugin.t(ctx.guild, "min_warns", _emote="WARN"))

    if warns > 100:
        return await ctx.send(plugin.t(ctx.guild, "max_warns", _emote="WARN"))

    automod = plugin.db.configs.get(ctx.guild.id, "automod")
    automod.update({
        "files": {"warns": warns}
    })

    await ctx.send(plugin.t(ctx.guild, "warns_set", _emote="YES", warns=warns, what="they send forbidden/uncommon attachment types"))