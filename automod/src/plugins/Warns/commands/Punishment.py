from discord.ext import commands

from ...Types import Embed

from ..sub.GetNewPunishments import getNewPunishments



valid_actions = [
    "ban",
    "kick",
    "mute",
    "none"
]


async def run(plugin, ctx, warns, action, time):
    action = action.lower()
    prefix = plugin.bot.get_guild_prefix(ctx.guild)
    e = Embed()
    if not action in valid_actions:
        return await ctx.send(plugin.t(ctx.guild, "invalid_action", _emote="WARN", prefix=prefix))

    if warns < 1:
        return await ctx.send(plugin.t(ctx.guild, "min_warns", _emote="NO"))

    if warns > 100:
        return await ctx.send(plugin.t(ctx.guild, "max_warns", _emote="NO"))

    current = plugin.db.configs.get(ctx.guild.id, "punishments")
    if action == "none":
        new = {x: y for x, y in current.items() if str(x) != str(warns)}
        plugin.db.configs.update(ctx.guild.id, "punishments", new)

        desc = await getNewPunishments(plugin, ctx)
        e.add_field(
            name="❯ Punishments",
            value="{}".format("\n".join(desc) if len(desc) > 0 else "None")
        )

        return await ctx.send(content=plugin.t(ctx.guild, "set_none", _emote="YES", warns=warns), embed=e)
    
    elif action != "mute":
        current.update({
            str(warns): action
        })
        plugin.db.configs.update(ctx.guild.id, "punishments", current)

        desc = await getNewPunishments(plugin, ctx)
        e.add_field(
            name="❯ Punishments",
            value="{}".format("\n".join(desc) if len(desc) > 0 else "None")
        )

        return await ctx.send(content=plugin.t(ctx.guild, f"set_{action}", _emote="YES", warns=warns), embed=e)

    else:
        if time is None:
            return await ctx.send(plugin.t(ctx.guild, "time_needed", _emote="NO", prefix=prefix))
        
        as_seconds = time.to_seconds(ctx)
        if as_seconds > 0:
            length = time.length
            unit = time.unit
            
            current.update({
                str(warns): f"{action} {as_seconds} {length} {unit}"
            })
            plugin.db.configs.update(ctx.guild.id, "punishments", current)

            desc = await getNewPunishments(plugin, ctx)
            e.add_field(
                name="❯ Punishments",
                value="{}".format("\n".join(desc) if len(desc) > 0 else "None")
            )

            return await ctx.send(content=plugin.t(ctx.guild, f"set_{action}", _emote="YES", warns=warns, length=length, unit=unit), embed=e)
        
        else:
            raise commands.BadArgument("number_too_small")