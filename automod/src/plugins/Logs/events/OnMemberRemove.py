import time
import asyncio
import datetime
import humanize

from ...Types import Embed



async def run(plugin, member):
    # Wait 1s before we continue
    # This is so we don't log actions
    # From e.g. bans
    await asyncio.sleep(0.5)
    if plugin.ignore_for_event.has("bans_kicks", member.id):
        return plugin.ignore_for_event.remove("bans_kicks", member.id)

    if plugin.db.configs.get(member.guild.id, "member_logging") is False:
        return
    
    ago = humanize.naturaldelta((datetime.datetime.fromtimestamp(time.time()) - member.joined_at))
    joined = member.joined_at.strftime("%Y-%m-%d %H:%M:%S")

    e = Embed(
        color=0x2f3136,
        description=plugin.t(member.guild, "leave", profile=member.mention, joined=joined, ago=ago)
    )
    e.set_author(name=f"{member} ({member.id})")
    e.set_thumbnail(url=member.avatar_url)
    e.set_footer(text="User left")
    await plugin.action_logger.log(
        member.guild, 
        "member_leave",
        _embed=e
    )