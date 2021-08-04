import asyncio
import datetime



async def unmuteTask(bot):
    while True:
        await asyncio.sleep(10)
        if len(list(bot.db.mutes.find({}))) > 0:
            for m in bot.db.mutes.find():
                if m["ending"] < datetime.datetime.utcnow():
                    guild = bot.get_guild(int(m["id"].split("-")[0]))
                    if guild is not None:

                        target = await bot.utils.getMember(guild, int(m["id"].split("-")[1]))
                        if target is None:
                            target = "Unknown#0000"
                        else:

                            try:
                                mute_role_id = bot.db.configs.get(guild.id, "mute_role")
                                mute_role = await bot.utils.getRole(guild, int(mute_role_id))

                                await target.remove_roles(mute_role)
                            except Exception:
                                pass
                        
                        await bot.action_logger.log(
                            guild,
                            "unmute",
                            user=target,
                            user_id=m["id"].split("-")[1]
                        )
                    bot.db.mutes.delete(m["id"])