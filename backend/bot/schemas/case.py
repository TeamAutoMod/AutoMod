# type: ignore

from datetime import datetime
import discord

import datetime
from typing import Union, Dict



def Case(
    case: int, 
    _type: str, 
    msg: Union[discord.Message, discord.Interaction], 
    mod: discord.Member, 
    user: Union[discord.Member, discord.User], 
    reason: str, 
    ts: datetime.datetime, 
    warns_added: int = 0, 
    until: datetime.datetime = None
) -> Dict[str, str]:
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
        "warns_added": warns_added,
        "until": f"<t:{round(until.timestamp())}>" if until != None else "",
        "log_id": "",
        "jump_url": ""
    }