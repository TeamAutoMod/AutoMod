import discord



async def run(plugin, ctx, guild_id):
    # Ensure this is an int
    guild_id = int(guild_id) 
    allowed_guilds = plugin.bot.config["allowed_guilds"]
    if guild_id not in allowed_guilds:
        return await ctx.send(plugin.translator.translate(ctx.guild, "not_allowed", _emote="WARN"))

    g = discord.utils.get(plugin.bot.guilds, id=guild_id)
    if g is not None:
        await g.leave()
    
    plugin.bot.modify_config.unallowed_guild(guild_id)
    await ctx.send(plugin.translator.translate(ctx.guild, "unallowed_guild", _emote="YES", guild_id=guild_id))