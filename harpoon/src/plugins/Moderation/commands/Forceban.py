from ..functions.BanUser import banUser
from ....utils import Permissions


async def run(plugin, ctx, user, reason):
    if reason is None:
        reason = plugin.t(ctx.guild, "no_reason")
    
    if await Permissions.is_banned(ctx, user):
        await ctx.send(plugin.t(ctx.guild, "target_already_banned", _emote="WARN"))

    await banUser(plugin, ctx, user, reason, "forceban", "forcebanned")