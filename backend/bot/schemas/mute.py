# type: ignore

import datetime
from typing import Union, Dict



def Mute(guild_id: int, user_id: str, until: datetime.datetime) -> Dict[str, Union[str, datetime.datetime]]:
    return {
        "id": f"{guild_id}-{user_id}",
        "until": until
    }