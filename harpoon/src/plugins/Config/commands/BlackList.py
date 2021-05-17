from ...Types import Embed



async def run(plugin, ctx):
    if plugin.db.configs.get(ctx.guild.id, "automod") is False:
        return await ctx.send(plugin.t(ctx.guild, "automod_disabled", _emote="WARN"))
    
    censored = plugin.db.configs.get(ctx.guild.id, "censored_words")
    prefix = plugin.bot.get_guild_prefix(ctx.guild)
    if len(censored) < 1:
        return await ctx.send(plugin.t(ctx.guild, "black_list_empty", _emote="WARN", prefix=prefix))
    
    e = Embed(
        title="Censor List",
        description="• Add a phrase: ``{0}config black_list add <phrase>`` \n• Remove a phrase: ``{0}config black_list remove <phrase>``".format(prefix)
    )
    e.add_field(
        name="Phrases",
        value="```\n{}\n```".format("\n".join(censored))
    )
    
    await ctx.send(embed=e)