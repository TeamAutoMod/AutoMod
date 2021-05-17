import traceback



async def run(plugin, ctx, text):
    if plugin.db.configs.get(ctx.guild.id, "automod") is False:
        return await ctx.send(plugin.translator.translate(ctx.guild, "automod_disabled", _emote="WARN"))
    
    text = text.lower()
    censored = [x.lower() for x in plugin.db.configs.get(ctx.guild.id, "censored_words")]
    if text in censored:
        return await ctx.send(plugin.translator.translate(ctx.guild, "already_on_black_list", _emote="WARN"))

    censored.append(text)
    plugin.db.configs.update(ctx.guild.id, "censored_words", censored)
    
    await ctx.send(plugin.translator.translate(ctx.guild, "added_to_black_list", _emote="YES", word=text))