<<<<<<< HEAD
import datetime



def Mute(guild_id: int, user_id: int, until: datetime.datetime) -> dict:
    return {
        "id": f"{guild_id}-{user_id}",
        "until": until
=======
import datetime



def Mute(guild_id: int, user_id: int, until: datetime.datetime) -> dict:
    return {
        "id": f"{guild_id}-{user_id}",
        "until": until
>>>>>>> 049ddcde2a090ba7492f82b75ee62cc010bbc290
    }