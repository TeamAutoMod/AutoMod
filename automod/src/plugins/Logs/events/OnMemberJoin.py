import time
import datetime
import humanize

from ...Types import Embed



async def run(plugin, member):
    if plugin.db.configs.get(member.guild.id, "member_logging") is False:
        return

    prior_cases = [f"``#{x['id'].split('-')[1]}``" for x in list(filter(lambda x: x['guild'] == str(member.guild.id) and x['target_id'] == str(member.id), list(plugin.db.inf.find({}))))]
    ago = humanize.naturaldelta((datetime.datetime.fromtimestamp(time.time()) - member.created_at))
    created = member.created_at.strftime("%Y-%m-%d %H:%M:%S")
    
    e = Embed()
    e.set_author(name=f"{member} ({member.id})")
    e.set_thumbnail(url=member.avatar_url)
    if len(prior_cases) > 0:
        e.color = 0xffff00
        e.description = plugin.t(member.guild, "prior_cases", cases=", ".join(prior_cases), profile=member.mention, created=created, ago=ago)
        e.set_footer(text="User with prior cases joined")
        await plugin.action_logger.log(
            member.guild, 
            "member_join_cases",
            _embed=e
        )
    else:
        e.color = 0x80f31f
        e.description = plugin.t(member.guild, "normal_join", profile=member.mention, created=created, ago=ago)
        e.set_footer(text="User joined")
        await plugin.action_logger.log(
            member.guild, 
            "member_join",
            _embed=e
        )