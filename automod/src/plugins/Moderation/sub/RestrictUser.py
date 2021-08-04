


restrictions = {
    "embed": {
        "role": "embed_role",
        "action": "Embed restriction",
        "success": "embed restricted"
    },
    "emoji": {
        "role": "emoji_role",
        "action": "Emoji restriction",
        "success": "emoji restricted"
    },
    "tag": {
        "role": "tag_role",
        "action": "Tag restriction",
        "success": "tag restricted"
    }
}
async def restrictUser(plugin, ctx, restriction, user, reason):
    restriction = restriction.lower()
    prefix = plugin.bot.get_guild_prefix(ctx.guild)

    if restriction not in restrictions:
        return await ctx.send(plugin.t(ctx.guild, "invalid_restriction"))
    
    d = restrictions[restriction]
    role_id = plugin.db.configs.get(ctx.guild.id, d["role"])
    if role_id == "":
        return await ctx.send(plugin.t(ctx.guild, "no_restrict_role", prefix=prefix))

    role = await plugin.bot.utils.getRole(ctx.guild, int(role_id))
    if role is None:
        return await ctx.send(plugin.t(ctx.guild, "no_restrict_role", prefix=prefix))

    if role in user.roles:
        return await ctx.send(plugin.t(ctx.guild, "already_restricted", _emote="NO", success=d["success"]))

    try:
        await user.add_roles(role)
    except Exception as ex:
        return await ctx.send(plugin.t(ctx.guild, "restrict_failed", _emote="NO", error=ex))
    else:
        case = plugin.bot.utils.newCase(ctx.guild, d["action"], user, ctx.author, reason)

        dm_result = await plugin.bot.utils.dmUser(ctx.message, "restrict", user, _emote="RESTRICT", guild_name=ctx.guild.name, success=d["success"], reason=reason)
        await ctx.send(plugin.t(ctx.guild, "user_restricted", _emote="YES", user=user, success=d["success"], case=case, dm=dm_result))

        await plugin.action_logger.log(
            ctx.guild, 
            "restrict", 
            moderator=ctx.message.author, 
            moderator_id=ctx.message.author.id,
            user=user,
            user_id=user.id,
            action=d["action"],
            reason=reason, 
            case=case,
            dm=dm_result
        )