from .DeleteLogMessage import deleteLogMessage



async def caseDelete(plugin, ctx, case):
    case_id = f"{ctx.guild.id}-{case}"
    if not plugin.db.inf.exists(case_id):
        return await ctx.send(plugin.i18next.t(ctx.guild, "case_not_found", _emote="NO"))

    confirm = await ctx.prompt(f"Are you sure you want to delete case **#{case}**? This actions can't be reverted.", timeout=15)
    if not confirm:
        return await ctx.send(plugin.i18next.t(ctx.guild, "aborting"))

    log_id = plugin.db.inf.get(case_id, "log_id")
    plugin.db.inf.delete(case_id)

    case_ids = plugin.db.configs.get(f"{ctx.guild.id}", "case_ids")
    del case_ids[case_id.split("-")[1]]
    plugin.db.configs.update(f"{ctx.guild.id}", "case_ids", case_ids)

    await deleteLogMessage(plugin, ctx, log_id)
    await ctx.send(plugin.i18next.t(ctx.guild, "case_deleted", _emote="YES", case=case))