from Database.Connector import Database


db = Database()


def get(collection, filter_field, filter_value, field_to_get):
    for _ in collection.find({f"{filter_field}": f"{filter_value}"}):
        return _[f"{field_to_get}"]


def update(collection, filter_field, filter_value, field_to_update, new_value):
    collection.update({f"{filter_field}": f'{filter_value}'}, {'$set': {f'{field_to_update}': new_value}}, upsert=False, multi=False)


def delete(collection, filter_field, filter_value):
    collection.delete_one({f"{filter_field}": f"{filter_value}"})

    
def insert(collection, schema):
    collection.insert(schema)


def new_case():
    current = get(db.counts, "id", "123", "mod_cases")
    new = int(current) + 1
    update(db.counts, "id", "123", "mod_cases", str(new))
    return str(new)



mod = {
    "antispam": "antispam",
    "automod": "automod",
    "lvlsystem": "lvlsystem",
    "memberLogging": "member_logging",
    "messageLogging": "message_logging"
}


def get_module_config(guild_id):
    enabled = []
    disabled = []
    for doc in db.configs.find({"guildId": f"{guild_id}"}):
        for _ in doc:
            if doc[_] is True:
                enabled.append("%s" % (mod[_]))
            if doc[_] is False:
                disabled.append("%s" % (mod[_]))
            else:
                pass
    return enabled, disabled


def get_log_channels(guild_id):
    general = ""
    messages = ""
    members = ""

    g = get(db.configs, "guildId", f"{guild_id}", "memberLogChannel")
    msg = get(db.configs, "guildId", f"{guild_id}", "messageLogChannel")
    m = get(db.configs, "guildId", f"{guild_id}", "joinLogChannel")

    if g != 0 or g != "" or g != None:
        general += "<#{}>".format(str(g))
    else:
        general += "Not set yet"
    
    if msg != 0 or msg != "" or msg != None:
        messages += "<#{}>".format(str(msg))
    else:
        messages += "Not set yet"

    if m != 0 or m != "" or m != None:
        members += "<#{}>".format(str(m))
    else:
        members += "Not set yet"

    return general, messages, members