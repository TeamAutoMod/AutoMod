from ...Types import Embed

import traceback
import itertools



async def run(plugin, ctx):
    filters = plugin.db.configs.get(ctx.guild.id, "filters")

    if len(filters) < 1:
        return await ctx.send(plugin.i18next.t(ctx.guild, "no_filters", _emote="NO"))

    e = Embed()
    footer = f"And {len(filters)-len(dict(itertools.islice(filters.items(), 10)))} more filters" if len(filters) > 10 else None
    for name in dict(itertools.islice(filters.items(), 10)):
        i = filters[name]
        e.add_field(name=f"❯ {name} ({i['warns']} {'warn' if int(i['warns']) == 1 else 'warns'})", value=", ".join([f"``{x}``" for x in i["words"]]))

    if footer is not None:
        e.set_footer(text=footer)
    
    await ctx.send(embed=e)