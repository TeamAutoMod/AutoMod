


async def run(plugin, member):
    guild = member.guild
    if guild is None:
        return
    
    if plugin.db.configs.get(guild.id, "persist") is False:
        return

    _id = f"{guild.id}-{member.id}"
    if not plugin.db.persists.exists(_id):
        return

    roles = plugin.db.persists.get(_id, "roles")
    nick = plugin.db.persists.get(_id, "nick")

    can_add = []
    for x in roles:
        role_obj = await plugin.bot.utils.getRole(guild, x)
        if role_obj is None:
            pass
        elif role_obj.position >= guild.me.top_role.position:
            pass
        elif role_obj in member.roles:
            pass
        else:
            can_add.append(role_obj)

    plugin.db.persists.delete(_id)    
    
    if len(can_add) < 1:
        return

    try:
        await member.edit(nick=nick)
    except Exception:
        pass

    try:
        await member.add_roles(*can_add)
    except Exception:
        pass