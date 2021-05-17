


async def caseDelete(plugin, ctx, case):
    case_id = f"{ctx.guild.id}-{case}"
    if not plugin.db.inf.exists(case_id):
        return await ctx.send(plugin.t(ctx.guild, "case_not_found", _emote="WARN"))

    confirm = await ctx.prompt(f"Are you sure you want to delete case **#{case}**? This actions can't be reverted.", timeout=15)
    if not confirm:
        return await ctx.send(plugin.t(ctx.guild, "aborting"))

    plugin.db.inf.delete(case_id)
    await ctx.send(plugin.t(ctx.guild, "case_deleted", _emote="YES", case=case))