from datetime import datetime
import discord

import datetime
from typing import Union



def Case(case: int, _type: str, msg: discord.Message, mod: discord.Member, user: Union[discord.Member, discord.User], reason: str, ts: datetime.datetime) -> dict:
    return {
        "id": f"{msg.guild.id}-{case}",
        "case": f"{case}",
        "guild": f"{msg.guild.id}",
        "user": f"{user.name}#{user.discriminator}",
        "user_id": f"{user.id}",
        "mod": f"{mod.name}#{mod.discriminator}",
        "mod_id": f"{mod.id}",
        "timestamp": ts,
        "type": f"{_type}",
        "reason": f"{reason}",
        "user_av": f"{user.display_avatar}",
        "mod_av": f"{mod.display_avatar}",
        "log_id": "",
        "jump_url": ""
    }