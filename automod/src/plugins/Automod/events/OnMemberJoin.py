import datetime
import time

from ..functions.Raid import enableRaidMode, disableRaidMode
from ....utils import Permissions



def pop_and_add(plugin, member):
    plugin.last_joiners[member.guild.id].pop(0)
    plugin.last_joiners[member.guild.id].append(member)


async def run(plugin, member):
    if member.guild is None:
        return
    
    if not "raid" in plugin.db.configs.get(member.guild.id, "automod"):
        return
    
    if Permissions.is_mod(member):
        return

    if member.discriminator == "0000":
        return

    if member.id == plugin.bot.user.id:
        return

    cfg = plugin.db.configs.get(member.guild.id, "automod")["raid"]
    if cfg["status"] is False:
        return

    if cfg["threshold"] is "":
        return

    try:
        _ = plugin.last_joiners[member.guild.id]
    except KeyError:
        plugin.last_joiners[member.guild.id] = list()
    else:
        per = int(cfg["threshold"].split("/")[1])
        allowed = int(cfg["threshold"].split("/")[0])

        if len(_) < allowed:
            plugin.last_joiners[member.guild.id].append(member)
        
        else:
            in_raid = plugin.raids[member.guild.id]["in_raid"] if member.guild.id in plugin.raids else False
            last_join = plugin.last_joiners[member.guild.id][-1].joined_at
            pop_and_add(plugin, member)
            if in_raid:
                if abs((member.joined_at - last_join).total_seconds()) >= 25:
                    await disableRaidMode(plugin, member.guild, plugin.bot.user, "Raid is over")
                else:
                    try:
                        await member.send(f"Hey **{member.name}**! \nThe server you just tried to join (**{member.guild.name}**) is currently under lockdown due to a raid. I'd suggest trying to join the server later on!")
                    except Exception:
                        pass
                    else:
                        try:
                            await member.kick(reason="Raid")
                        except Exception:
                            pass
            else:
                if abs((member.joined_at - last_join).total_seconds()) <= per:
                    await enableRaidMode(plugin, member.guild, plugin.bot.user, f"Max join raid exceeded ({allowed}/{per})")
