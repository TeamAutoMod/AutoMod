import datetime



def Case(case, _type, msg, mod, user, reason):
    return {
        "id": f"{msg.guild.id}-{case}",
        "case": f"{case}",
        "guild": f"{msg.guild.id}",
        "user": f"{user.name}#{user.discriminator}",
        "user_id": f"{user.id}",
        "mod": f"{mod.name}#{mod.discriminator}",
        "mod_id": f"{mod.id}",
        "timestamp": datetime.datetime.utcnow(),
        "type": f"{_type}",
        "reason": f"{reason}",
        "user_av": f"{user.display_avatar}",
        "mod_av": f"{mod.display_avatar}",
        "log_id": "",
        "jump_url": ""
    }