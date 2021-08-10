


async def getLogForCase(plugin, ctx, case):
    if not "log_id" in case:
        return
    
    log_id = case["log_id"]
    if log_id == "":
        return None

    if "jump_url" in case:
        instant = case["jump_url"]
        if instant != "":
            return instant
        
    log_channel_id = plugin.db.configs.get(ctx.guild.id, "mod_log")
    if log_channel_id == "":
        return None

    return f"https://discord.com/channels/701507539589660793/{log_channel_id}/{log_id}"