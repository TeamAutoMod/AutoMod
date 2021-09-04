from ...Types import Embed



async def run(plugin, ctx):
    prefix = plugin.db.configs.get(ctx.guild.id, "prefix")
    e = Embed(
        title="How to use filters",
        description=f"• Adding a filter: ``{prefix}filter add <name> <warns> <words>`` \n• Deleting a filter: ``{prefix}filter remove <name>``"
    )
    e.add_field(
        name="❯ Arguments",
        value="``<name>`` - *Name of the filter* \n``<warns>`` - *Warns users get when using a word within the filter* \n``<words>`` - *Words contained in the filter, seperated by commas*"
    )
    e.add_field(
        name="❯ Wildcards",
        value="You can also use an astrix (``*``) as a wildcard. E.g. \nIf you set one of the words to be ``tes*``, then things like ``test`` or ``testtt`` would all be filtered."
    )
    e.add_field(
        name="❯ Example",
        value=f"``{prefix}filter add test_filter 1 oneword, two words, wildcar*``"
    )
    await ctx.send(embed=e)