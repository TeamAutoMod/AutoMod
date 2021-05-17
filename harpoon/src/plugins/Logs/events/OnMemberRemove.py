import time
import asyncio
import datetime



async def run(plugin, member):
    # Wait 1s before we continue
    # This is so we don't log actions
    # From e.g. bans
    await asyncio.sleep(0.5)
    if plugin.ignore_for_event.has("bans_kicks", member.id):
        return plugin.ignore_for_event.remove("bans_kicks", member.id)

    if plugin.db.configs.get(member.guild.id, "member_logging") is False:
        return
    
    await plugin.action_logger.log(
        member.guild, 
        "member_leave",
        user=member,
        user_id=member.id,
        joined=(datetime.datetime.fromtimestamp(time.time) - member.joined_at).days
    )