import time
import datetime


async def run(plugin, member):
    if plugin.db.configs.get(member.guild.id, "member_logging") is False:
        return

    prior_cases = [f"#{x['id'].split('-')[0]}" for x in list(filter(lambda x: x['guild'] == str(member.guild.id) and x['target_id'] == str(member.id), list(plugin.db.inf.find({}))))]
    kwargs = {
        "user": member,
        "user_id": member.id
    }
    if len(prior_cases) < 1:
        kwargs.update({
            "cases": "\n".join(prior_cases)
        })
        await plugin.action_logger.log(
            member.guild, 
            "member_join_cases",
            **kwargs
        )
    else:
        kwargs.update({
            "age": (datetime.datetime.fromtimestamp(time.time()) - member.created_at).days
        })
        await plugin.action_logger.log(
            member.guild, 
            "member_join",
            **kwargs
        )