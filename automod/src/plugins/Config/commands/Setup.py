from ...Types import Embed



async def run(plugin, ctx):
    prefix = plugin.bot.get_guild_prefix(ctx.guild)
    e = Embed(
        title="Setup commands",
        description=plugin.i18next.t(ctx.guild, "setup_description")
    )
    e.add_field(
        name="❯ Mute role",
        value=f"``{prefix}setup muted``"
    )
    e.add_field(
        name="❯ Automoderator",
        value=f"``{prefix}setup automod``"
    )
    e.add_field(
        name="❯ Restrict roles",
        value=f"``{prefix}setup restrict``"
    )
    await ctx.send(embed=e)