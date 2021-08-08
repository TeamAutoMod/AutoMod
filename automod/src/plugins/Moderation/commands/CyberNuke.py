import discord

import datetime
import time

from ..sub.BanUser import banUser
from ....utils import Permissions



async def run(plugin, ctx, join, age):
    if ctx.guild.id in plugin.running_cybernukes:
        return await ctx.send(plugin.i18next.t(ctx.guild, "cybernuke_running", _emote="NO"))

    if join.unit is None:
        join.unit = "m"
    if age.unit is None:
        age.unit = "m"

    join = datetime.datetime.utcfromtimestamp(time.time() - join.to_seconds(ctx))
    age = datetime.datetime.utcfromtimestamp(time.time() - age.to_seconds(ctx))

    targets = list(filter(lambda x: x.joined_at <= join and x.created_at <= age, ctx.guild.members))
    if len(targets) < 1:
        return await ctx.send(plugin.i18next.t(ctx.guild, "no_targets", _emote="NO"))
    if len(targets) > 100:
        return await ctx.send(plugin.i18next.t(ctx.guild, "too_many_targets", _emote="NO"))

    plugin.running_cybernukes.append(ctx.guild.id)
    confirm = await ctx.prompt(f"This will ban {len(targets)} users.", timeout=15)
    if not confirm:
        plugin.running_cybernukes.remove(ctx.guild.id)
        return await ctx.send(plugin.i18next.t(ctx.guild, "aborting"))

    case = plugin.bot.utils.newCase(ctx.guild, "Cybernuke", targets[0], ctx.author, f"Cybernuke ({len(targets)})")
    banned = 0
    for i, t in enumerate(targets):
        reason = f"Cybernuke ``({i+1}/{len(targets)})``"

        if not Permissions.is_allowed(ctx, ctx.author, t):
            await ctx.send(plugin.i18next.t(ctx.guild, "ban_not_allowed", _emote="NO"))
        else:
            try:
                await ctx.guild.ban(t, reason=reason)
            except Exception as ex:
                await ctx.send(plugin.i18next.t(ctx.guild, "ban_failed", _emote="NO", error=ex))
            else:
                banned += 1
                dm_result = await plugin.bot.utils.dmUser(ctx.message, "cybernuke", t, _emote="HAMMER", guild_name=ctx.guild.name, reason=reason)

                await plugin.action_logger.log(
                    ctx.guild,
                    "cybernuke",
                    moderator=ctx.message.author, 
                    moderator_id=ctx.message.author.id,
                    user=t,
                    user_id=t.id,
                    reason=reason,
                    case=case,
                    dm=dm_result
                )
    plugin.running_cybernukes.remove(ctx.guild.id)
    await ctx.send(plugin.i18next.t(ctx.guild, "users_cybernuked", _emote="YES", banned=banned, total=len(targets), case=case))