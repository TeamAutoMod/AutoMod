import datetime
import humanize
import time

from ...Types import Embed



async def run(plugin, ctx):
    g = ctx.guild

    e = Embed()
    e.set_thumbnail(
        url=ctx.guild.icon_url_as()
    )
    e.add_field(
        name="❯ Information",
        value="• ID: {} \n• Owner: {} ({})"\
        .format(
            g.id, g.owner, g.owner.id
        )
    )
    e.add_field(
        name="❯ Channels",
        value="• Text: {} \n• Voice: {}"\
        .format(
            len(g.text_channels), 
            len(g.voice_channels)
        )
    )
    e.add_field(
        name="❯ Members",
        value="• Total: {} \n• Users: {} \n• Bots: {}"\
        .format(
            len(g.members), 
            len([x for x in g.members if not x.bot]), 
            len([x for x in g.members if x.bot])
        )
    )
    e.add_field(
        name="❯ Other",
        value="• Roles: {} \n• Emojis: {} \n• Created at: <t:{}>\n• Features: {}"\
        .format(
            len(g.roles), 
            len(g.emojis), 
            round(g.created_at.timestamp()),
            ", ".join(g.features) if len(g.features) > 0 else "None"
        )
    )
    await ctx.send(embed=e)