from random import randint



def UserLevel(guild, user):
    return {
        "id": f"{guild.id}-{user.id}",
        "guild": f"{guild.id}",
        "xp": randint(2, 7),
        "lvl": 1
    }