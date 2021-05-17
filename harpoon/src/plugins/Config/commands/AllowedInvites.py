from ...Types import Embed



async def run(plugin, ctx):
    if plugin.db.configs.get(ctx.guild.id, "automod") is False:
        return await ctx.send(plugin.translator.translate(ctx.guild, "automod_disabled", _emote="WARN"))

    allowed = plugin.db.configs.get(ctx.guild.id, "whitelisted_invites")
    prefix = plugin.bot.get_guild_prefix(ctx.guild)
    
    e = Embed(
        title="Allowed Invites"
    )
    if len(allowed) < 1:
        e.description = "Currently all invites are blacklisted \n• Whitelist one by using ``{}config allowed_invites add <server>``".format(prefix)
    else:
        e.description = "Currently ``{}`` invites are whitelisted \n• Whitelist another one by using ``{}config allowed_invites add <server>``".format(len(allowed), prefix)
        e.add_field(
            name="Whitelisted Servers (By ID)",
            value="```\n{}\n```".format("\n".join(allowed))
        )

    await ctx.send(embed=e)