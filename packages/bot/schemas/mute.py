# type: ignore

import datetime



def Mute(
    guild_id: int, 
    user_id: str, 
    until: datetime.datetime
) -> dict:
    return {
        "id": f"{guild_id}-{user_id}",
        "until": until
    }