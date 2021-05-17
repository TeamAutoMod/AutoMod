from ...Types import Embed



async def run(plugin, ctx, user):
    try:
        mutuals = []
        for g in plugin.bot.guilds:
            if g.get_member(user) is not None:
                mutuals.append(g.name)
        
        await ctx.send(embed=Embed(title=plugin.t(ctx.guild, "mutual_guilds"), description="```\n{}\n```".format("\n".join(mutuals))))
    except Exception as ex:
        await ctx.send(ex)