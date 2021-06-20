from ..functions.UpdateLogMessage import updateLogMessage



async def run(plugin, ctx, case, reason):
    if case is None:
        recent = sorted([x for x in plugin.db.inf.find({"guild": f"{ctx.guild.id}"}) if x["reason"] == plugin.t(ctx.guild, "no_reason")], key=lambda k: int(k['id'].split('-')[1]))
        if len(recent) < 1:
            return await ctx.send(plugin.t(ctx.guild, "no_recent_case", _emote="WARN"))
        else:
            return await updateLogMessage(plugin, ctx, recent[-1]["log_id"], recent[-1]["id"].split("-")[1], reason)
    else:
        case = case.split("#")[1] if len(case.split("#")) == 2 else case
        if not plugin.db.inf.exists(f"{ctx.guild.id}-{case}"):
            return await ctx.send(plugin.t(ctx.guild, "case_not_found", _emote="WARN"))

        log_id = plugin.db.inf.get(f"{ctx.guild.id}-{case}", "log_id")
        await updateLogMessage(plugin, ctx, log_id, case, reason)