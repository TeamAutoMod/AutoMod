import discord



async def enableRaidMode(plugin, guild, moderator, reason):
    state = {"last": guild.verification_level, "in_raid": False}

    try:
        await guild.edit(verification_level=discord.VerificationLevel.high)
    except Exception:
        pass
    else:
        state.update({"in_raid": True})
        plugin.raids[guild.id] = state

        await plugin.action_logger.log(
            guild, 
            "raid_on", 
            moderator=moderator, 
            moderator_id=moderator.id,
            reason=reason
        )


async def disableRaidMode(plugin, guild, moderator, reason):
    state = plugin.raids[guild.id]

    try:
        await guild.edit(verification_level=state["last"])
    except Exception:
        pass
    finally:
        del plugin.raids[guild.id]
        plugin.last_joiners[guild.id].clear()

        await plugin.action_logger.log(
            guild, 
            "raid_off", 
            moderator=moderator,
            moderator_id=moderator.id,
            reason=reason
        )