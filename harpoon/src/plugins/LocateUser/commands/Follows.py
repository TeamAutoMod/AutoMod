from ...Types import Embed



async def run(plugin, ctx):
    _id = f"{ctx.guild.id}-{ctx.author.id}"
    if not plugin.db.follows.exists(_id):
        return await ctx.send(plugin.translator.translate(ctx.guild, "no_follows", _emote="WARN"))

    follows = [f"• {x}" for x in plugin.db.follows.get(_id, "users")]
    if len(follows) < 1:
        return await ctx.send(plugin.translator.translate(ctx.guild, "no_follows", _emote="WARN"))

    e = Embed(
        title="Active Alerts",
        description="```\n{}\n```".format("\n".join(follows))
    )
    
    await ctx.send(embed=e)