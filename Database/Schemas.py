from Utils.Constants import default_censored_words


def command_schema(guild, trigger, reply, author):
    schema = {
        "cmdId": f"{guild.id}-{trigger}",
        "reply": f"{reply}",
        "author": f"{author.id}"
    }
    return schema


def warn_schema(warn_id, warns: int):
    schema = {
        "warnId": f"{warn_id}",
        "warns": warns,
        "check": True,
        "kicked": False,
        "banned": False
    }
    return schema




def guild_schema(guild):
    schema = { 
        "guildId": f"{guild.id}", 
        "prefix": "+", 
        "muteRole": "",
        "memberLogChannel": "", 
        "messageLogChannel": "",
        "joinLogChannel": "", 
        "antispam": False,
        "automod": False, 
        "lvlsystem": False, 
        "memberLogging": False,
        "messageLogging": False,
        "welcomeChannel": "", 
        "welcomeMessage": "",
        "censored_words": default_censored_words,
        "level_roles": [],
        "ignored_users": [],
        "lang": "en_US"
        "guildName": f"{guild.name}"
    }
    return schema



def level_schema(guild_id, user_id):
    schema = {
        "levelId": f"{guild_id}-{user_id}",
        "lvl": 1,
        "xp": 0
    }
    return schema


def mute_schema(guild_id, user_id, ending_date):
    schema = {
        "mute_id": f"{guild_id}-{user_id}",
        "ending": ending_date
    }
    return schema


def new_infraction(inf_id, guild_id, target, moderator, timestamp, inf_type, reason):
    schema = {
        "case": f"{inf_id}",
        "guild": f"{guild_id}",
        "target": f"{target.name}#{target.discriminator}",
        "target_id": f"{target.id}",
        "moderator": f"{moderator.name}#{moderator.discriminator}",
        "moderator_id": f"{moderator.id}",
        "timestamp": timestamp,
        "type": f"{inf_type}",
        "reason": f"{reason}",
        "target_av": f"{target.avatar_url_as()}",
        "moderator_av": f"{moderator.avatar_url_as()}"
    }
    return schema
