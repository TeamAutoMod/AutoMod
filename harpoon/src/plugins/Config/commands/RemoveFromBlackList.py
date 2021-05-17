


async def run(plugin, ctx, text):
    if plugin.db.configs.get(ctx.guild.id, "automod") is False:
        return await ctx.send(plugin.t(ctx.guild, "automod_disabled", _emote="WARN"))
    
    text = text.lower()
    censored = [x.lower() for x in plugin.db.configs.get(ctx.guild.id, "censored_words")]
    prefix = plugin.bot.get_guild_prefix(ctx.guild)
    if len(censored) < 1:
        return await ctx.send(plugin.t(ctx.guild, "black_list_empty", _emote="WARN", prefix=prefix))

    if text not in censored:
        return await ctx.send(plugin.t(ctx.guild, "not_on_black_list", _emote="WARN"))

    censored.remove(text)
    plugin.db.configs.update(ctx.guild.id, "censored_words", censored)
    
    await ctx.send(plugin.t(ctx.guild, "removed_from_black_list", _emote="YES", word=text))