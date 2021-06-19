import asyncio



async def run(plugin, guild, user):
    # Wait 1s before we continue
    # This is so we don't log actions
    # From e.g. unbans
    await asyncio.sleep(0.5)
    if plugin.ignore_for_event.has("unbans", user.id):
        return plugin.ignore_for_event.remove("unbans", user.id)
    
    await plugin.action_logger.log(
        guild, 
        "manual_unban",
        user=user,
        user_id=user.id
    )