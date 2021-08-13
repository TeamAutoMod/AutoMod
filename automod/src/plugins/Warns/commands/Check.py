import datetime
import humanize

from ....utils import Permissions
from ...Types import Embed



async def run(plugin, ctx, user):
    _id = f"{ctx.guild.id}-{user.id}"
    warns = plugin.db.warns.get(_id, "warns") if plugin.db.warns.exists(_id) else 0

    muted = "Yes" if plugin.db.mutes.exists(_id) else "No"
    mute_remaining = humanize.naturaldelta((datetime.datetime.utcnow() - plugin.db.mutes.get(_id, "ending"))) if plugin.db.mutes.exists(_id) else "N/A"

    banned = "No" if not await Permissions.is_banned(ctx, user) else "Yes"

    e = Embed()
    e.set_author(
        name=f"{user} ({user.id})",
        icon_url=user.avatar.url
    )
    e.add_field(
        name="❯ Warns",
        value=f"``{warns}``"
    )
    e.add_field(
        name="❯ Muted",
        value=f"``{muted}``"
    )
    e.add_field(
        name="❯ Remaining Mute Time",
        value=f"``{mute_remaining}``"
    )
    e.add_field(
        name="❯ Banned",
        value=f"``{banned}``"
    )

    await ctx.send(embed=e)