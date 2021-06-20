import re



async def run(plugin, ctx, threshold):
    threshold = threshold.lower()
    automod = plugin.db.configs.get(ctx.guild.id, "automod")
    
    if threshold == "off":
        automod.update({
            "raid": {"status": False, "threshold": automod["raid"]["threshold"]}
        })
        plugin.db.configs.update(ctx.guild.id, "automod", automod)

        return await ctx.send(plugin.t(ctx.guild, "raid_off", _emote="YES"))
    
    elif len(threshold.split("/")) == 2 and re.match(r"^[-+]?[0-9]+$", threshold.split("/")[0]) is not None and re.match(r"^[-+]?[0-9]+$", threshold.split("/")[1]) is not None:
        if int(threshold.split("/")[0]) > 5 or int(threshold.split("/")[1]) > 5:
            return await ctx.send(plugin.t(ctx.guild, "threshold_too_low", _emote="WARN"))

        automod.update({
            "raid": {"status": True, "threshold": f"{threshold}"}
        })
        plugin.db.configs.update(ctx.guild.id, "automod", automod)

        return await ctx.send(plugin.t(ctx.guild, "raid_on", _emote="YES", users=threshold.split("/")[0], seconds=threshold.split("/")[1]))

    else:
        prefix = plugin.bot.get_guild_prefix(ctx.guild)
        return await ctx.send(plugin.t(ctx.guild, "raid_help", _emote="WARN", prefix=prefix)) 