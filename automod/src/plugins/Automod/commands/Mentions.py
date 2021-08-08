


async def run(plugin, ctx, mentions):
    mentions = mentions.lower()
    if mentions == "off":
        automod = plugin.db.configs.get(ctx.guild.id, "automod")
        if "mentions" in automod:
            del automod["mentions"]
        plugin.db.configs.update(ctx.guild.id, "automod", automod)
        
        await ctx.send(plugin.i18next.t(ctx.guild, "automod_feature_disabled", _emote="YES", what="max-mentions"))
    else:
        try:
            mentions = int(mentions)
        except ValueError:
            await ctx.send(plugin.i18next.t(ctx.guild, "invalid_automod_feature_param", _emote="WARN", prefix=plugin.bot.get_guild_prefix(ctx.guild), command="mentions <mentions>", off_command="mentions off"))
        else:
            if mentions < 4:
                return await ctx.send(plugin.i18next.t(ctx.guild, "min_mentions", _emote="NO"))

            if mentions > 100:
                return await ctx.send(plugin.i18next.t(ctx.guild, "max_mentions", _emote="NO"))

            automod = plugin.db.configs.get(ctx.guild.id, "automod")
            automod.update({
                "mentions": {"threshold": mentions}
            })
            plugin.db.configs.update(ctx.guild.id, "automod", automod)

            await ctx.send(plugin.i18next.t(ctx.guild, "mentions_set", _emote="YES", mentions=mentions))