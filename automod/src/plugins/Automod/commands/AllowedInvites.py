from ...Types import Embed



async def run(plugin, ctx):
    allowed = [x.strip().lower() for x in plugin.db.configs.get(ctx.guild.id, "whitelisted_invites")]
    prefix = plugin.bot.get_guild_prefix(ctx.guild)
    if len(allowed) < 1:
        return await ctx.send(plugin.t(ctx.guild, "no_whiteslisted", _emote="NO", prefix=prefix))
    else:
        e = Embed()
        e.add_field(
            name="❯ Allowed invites (by server ID)", 
            value=", ".join([f"``{x}``" for x in allowed])
        )
        await ctx.send(embed=e)