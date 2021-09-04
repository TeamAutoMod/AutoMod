


async def run(plugin, ctx, channel):
    config = plugin.db.configs.get(f"{ctx.guild.id}", "starboard")
    if config["enabled"] == False:
        return await ctx.send(plugin.i18next.t(ctx.guild, "starboard_is_disabled", _emote="NO", prefix=plugin.bot.get_guild_prefix(ctx.guild)))
    
    config["channel"] = f"{channel.id}"
    await ctx.send(plugin.i18next.t(ctx.guild, "set_starboard_channel", _emote="YES", channel=channel.mention))