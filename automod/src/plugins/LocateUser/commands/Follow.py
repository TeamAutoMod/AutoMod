import discord



async def run(plugin, ctx, user_id):
    if discord.utils.get(ctx.guild.members, id=user_id) is None:
        return await ctx.send(plugin.t(ctx.guild, "target_not_on_server", _emote="NO"))

    if user_id == ctx.author.id:
        return await ctx.send(plugin.t(ctx.guild, "cant_follow_yourself", _emote="NO"))

    _id = f"{ctx.guild.id}-{ctx.author.id}"
    if not plugin.db.follows.exists(_id):
        plugin.db.follows.insert(plugin.schemas.Follow(_id, user_id))
        return await ctx.send(plugin.t(ctx.guild, "followed", _emote="YES", user=user_id))
    
    follows = plugin.db.follows.get(_id, "users")
    if user_id in follows:
        return await plugin.t(ctx.guild, "already_following", _emote="WARN")

    follows.append(user_id)
    plugin.db.follows.update(_id, "users", follows)

    await ctx.send(plugin.t(ctx.guild, "followed", _emote="YES", user=user_id))