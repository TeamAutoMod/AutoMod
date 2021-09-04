import datetime
import humanize

from ....utils import Permissions
from ...Types import Embed



async def run(plugin, ctx, user):
    _id = f"{ctx.guild.id}-{user.id}"
    warns = plugin.db.warns.get(_id, "warns") if plugin.db.warns.exists(_id) else 0

    muted = "✅" if plugin.db.mutes.exists(_id) else "❌"
    muted_until = f"<t:{round(plugin.db.mutes.get(_id, 'ending').timestamp())}>" if plugin.db.mutes.exists(_id) else "``N/A``"

    banned = "❌" if not await Permissions.is_banned(ctx, user) else "✅"

    e = Embed()
    e.set_author(
        name=f"{user} ({user.id})",
        icon_url=user.display_avatar
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
        name="❯ Muted until",
        value=f"{muted_until}"
    )
    e.add_field(
        name="❯ Banned",
        value=f"``{banned}``"
    )

    await ctx.send(embed=e)