from ..functions.BanUser import banUser
from ....utils import Permissions


async def run(plugin, ctx, user, reason):
    if reason is None:
        reason = plugin.translator.translate(ctx.guild, "no_reason")

    user = ctx.guild.get_member(user.id)
    if user is None:
        await ctx.send(plugin.translator.translate(ctx.guild, "target_not_on_server", _emote="WARN"))
    
    if not Permissions.is_allowed(ctx, ctx.author, user):
        return await ctx.send(plugin.translator.translate(ctx.guild, "ban_not_allowed", _emote="WARN"))
    
    if await Permissions.is_banned(ctx, user):
        await ctx.send(plugin.translator.translate(ctx.guild, "target_already_banned", _emote="WARN"))

    await banUser(plugin, ctx, user, reason, "cleanban", "cleanbanned")