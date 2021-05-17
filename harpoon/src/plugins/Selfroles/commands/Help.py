from ...Types import Embed



async def run(plugin, ctx):
    roles = [x for x in plugin.db.configs.get(ctx.guild.id, "selfroles")]
    if len(roles) < 1:
        return await ctx.send(plugin.translator.translate(ctx.guild, "no_selfroles", _emote="WARN"))

    prefix = plugin.bot.get_guild_prefix(ctx.guild)
    description = """
    To give yourself a role, type e.g. ``{0}role add {1}`` where **{1}** is the role you want. {2} \n
    To remove a role, type ``{0}role remove {1}``, again replacing **{1}** with the role you want to remove.
    """.format(
        prefix, 
        roles[0],
        f"You can also add multiple roles at once, e.g. ``{prefix}role add {roles[0]} {roles[1]}``" if len(roles) > 1 else "" 
    )

    e = Embed(title="How to get roles", description=description)
    e.add_field(name="Roles available to you:", value="```\n{}\n```".format("\n".join([f"• {x}" for x in roles])))
    await ctx.send(embed=e)
