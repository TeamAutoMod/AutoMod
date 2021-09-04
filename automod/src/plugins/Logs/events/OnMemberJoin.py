import time
import datetime
import humanize

from ...Types import Embed



async def run(plugin, member):
    if plugin.db.configs.get(member.guild.id, "member_logging") is False:
        return

    prior_cases = [f"``#{x['id'].split('-')[1]}``" for x in list(filter(lambda x: x['guild'] == str(member.guild.id) and x['target_id'] == str(member.id), list(plugin.db.inf.find({}))))]
    
    e = Embed()
    e.set_author(name=f"{member} ({member.id})")
<<<<<<< HEAD
    e.set_thumbnail(url=member.display_avatar)
=======
    e.set_thumbnail(url=member.avatar.url)
>>>>>>> fadbb019af2ff9681468f33deab270b740801566
    if len(prior_cases) > 0:
        e.color = 0xffdc5c
        e.description = plugin.i18next.t(member.guild, "prior_cases", cases=" | ".join(prior_cases), profile=member.mention, created=round(member.created_at.timestamp()))
        e.set_footer(text="User with prior cases joined")
        await plugin.action_logger.log(
            member.guild, 
            "member_join_cases",
            _embed=e
        )
    else:
        e.color = 0x5cff9d
        e.description = plugin.i18next.t(member.guild, "normal_join", profile=member.mention, created=round(member.created_at.timestamp()))
        e.set_footer(text="User joined")
        await plugin.action_logger.log(
            member.guild, 
            "member_join",
            _embed=e
        )