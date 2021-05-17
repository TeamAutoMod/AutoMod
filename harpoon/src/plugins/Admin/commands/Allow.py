


async def run(plugin, ctx, guild_id):
    # Ensure this is an int
    guild_id = int(guild_id) 
    allowed_guilds = plugin.bot.config["allowed_guilds"]
    if guild_id in allowed_guilds:
        return await ctx.send(plugin.t(ctx.guild, "already_allowed", _emote="WARN"))
    
    plugin.bot.modify_config.allow_guild(guild_id)
    await ctx.send(plugin.t(ctx.guild, "allowed_guild", _emote="YES", guild_id=guild_id))