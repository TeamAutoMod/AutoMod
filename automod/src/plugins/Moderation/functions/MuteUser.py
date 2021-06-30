import discord
from discord.ext import commands

import datetime
import traceback



async def muteUser(plugin, ctx, user, length, reason):
    if length.unit is None:
        parts = reason.split(" ")
        length.unit = parts[0]
        reason = " ".join(parts[1:])

    mute_role_id = plugin.db.configs.get(ctx.guild.id, "mute_role")
    if mute_role_id is None:
        return await ctx.send(plugin.t(ctx.guild, "no_mute_role", _emote="NO"))
    
    mute_role = await plugin.bot.utils.getRole(ctx.guild, mute_role_id)
    if mute_role is None:
        return await ctx.send(plugin.t(ctx.guild, "no_mute_role", _emote="NO"))

    mute_id = f"{ctx.guild.id}-{user.id}"
    # Check if user is already muted. If so, should we extend their mute?
    if plugin.db.mutes.exists(mute_id):
        confirm = await ctx.prompt(plugin.t(ctx.guild, "already_muted", _emote="WARN", user=user), timeout=15)
        if not confirm:
            return await ctx.send(plugin.t(ctx.guild, "aborting"))
        
        until = (plugin.db.mutes.get(mute_id, "ending") + datetime.timedelta(seconds=length.to_seconds(ctx)))
        plugin.db.mutes.update(mute_id, "ending", until)

        await ctx.send(plugin.t(ctx.guild, "mute_extended", _emote="YES", user=user, length=length.length, unit=length.unit, reason=reason))
        await plugin.action_logger.log(
            ctx.guild, 
            "mute_extended", 
            moderator=ctx.message.author, 
            moderator_id=ctx.message.author.id,
            user=user,
            user_id=user.id,
            length=length.length, 
            unit=length.unit,
            reason=reason
        )
        if not mute_role in user.roles:
            try:
                await user.add_roles(mute_role)
            except Exception:
                return
        return
    else:
        if ctx.guild.me.top_role.position > mute_role.position:
            seconds = length.to_seconds(ctx)
            if seconds >= 1:
                try:
                    await user.add_roles(mute_role)
                except Exception as ex:
                    await ctx.send(plugin.t(ctx.guild, "mute_failed", _emote="NO", error=ex))
                else:
                    until = (datetime.datetime.utcnow() + datetime.timedelta(seconds=seconds))
                    plugin.db.mutes.insert(plugin.schemas.Mute(ctx.guild.id, user.id, until))

                    case = plugin.bot.utils.newCase(ctx.guild, "Mute", user, ctx.author, reason)

                    dm_result = await plugin.bot.utils.dmUser(ctx.message, "mute", user, _emote="MUTE", guild_name=ctx.guild.name, length=length.length, unit=length.unit, reason=reason)
                    await ctx.send(plugin.t(ctx.guild, "user_muted", _emote="YES", user=user, length=length.length, unit=length.unit, reason=reason, case=case, dm=dm_result))
                    
                    last = await ctx.message.channel.history(limit=20).find(lambda x: x.author.id == user.id)
                    await plugin.action_logger.log(
                        ctx.guild, 
                        "mute", 
                        moderator=ctx.message.author, 
                        moderator_id=ctx.message.author.id,
                        user=user,
                        user_id=user.id,
                        length=length.length, 
                        unit=length.unit,
                        context=f"\n**Context:** [Here!]({last.jump_url})" if last is not None else "",
                        reason=reason, 
                        case=case
                    )
            else:
                raise commands.BadArgument("number_too_small")
        else:
            await ctx.send(plugin.t(ctx.guild, "role_too_high", _emote="NO"))
