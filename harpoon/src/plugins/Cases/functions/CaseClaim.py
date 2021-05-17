


async def caseClaim(plugin, ctx, case):
    case_id = f"{ctx.guild.id}-{case}"
    if not plugin.db.inf.exists(case_id):
        return await ctx.send(plugin.translator.translate(ctx.guild, "case_not_found", _emote="WARN"))

    _case = [x for x in plugin.db.inf.find({"id": case_id})][0]
    if _case["moderator_id"] == str(ctx.author.id):
        return await ctx.send(plugin.translator.translate(ctx.guild, "case_already_owned", _emote="WARN"))

    if _case["target_id"] == str(ctx.author.id):
        return await ctx.send(plugin.translator.translate(ctx.guild, "case_target", _emote="WARN"))

    plugin.db.inf.update(case_id, "moderator_id", f"{ctx.author.id}")
    plugin.db.inf.update(case_id, "moderator_av", f"{ctx.author.avatar_url}")
    await ctx.send(plugin.translator.translate(ctx.guild, "case_claimed", _emote="YES", case=case))