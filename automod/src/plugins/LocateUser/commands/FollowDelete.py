


async def run(plugin, ctx, user_id):
    _id = f"{ctx.guild.id}-{ctx.author.id}"
    if not plugin.db.follows.exists(_id):
        return await ctx.send(plugin.t(ctx.guild, "no_follows", _emote="WARN"))

    follows = plugin.db.follows.get(_id, "users")
    if len(follows) < 1:
        return await ctx.send(plugin.t(ctx.guild, "no_follows", _emote="WARN"))

    if user_id not in follows:
        return await plugin.t(ctx.guild, "not_following", _emote="WARN")

    follows.remove(user_id)
    plugin.db.follows.update(_id, "users", follows)

    await ctx.send(plugin.t(ctx.guild, "unfollowed", _emote="YES", user=user_id))