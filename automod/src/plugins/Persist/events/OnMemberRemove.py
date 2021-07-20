


async def run(plugin, member):
    guild = member.guild
    if guild is None:
        return
    
    if plugin.db.configs.get(guild.id, "persist") is False:
        return

    if plugin.db.persists.exists(f"{guild.id}-{member.id}"):
        return
    
    old_roles = [x.id for x in member.roles if x != guild.default_role and x.position < member.guild.me.top_role.position]
    old_nick = member.nick if member.nick is not None else ""

    if len(old_roles) < 1 and old_nick == "":
        return

    plugin.db.persists.insert(plugin.schemas.Persist(guild.id, member.id, old_roles, old_nick))