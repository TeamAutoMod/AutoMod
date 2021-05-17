from ...Types import Embed



async def caseInfo(plugin, ctx, case):
    case_id = f"{ctx.guild.id}-{case}"
    if not plugin.db.inf.exists(case_id):
        return await ctx.send(plugin.t(ctx.guild, "case_not_found", _emote="WARN"))
    
    _case = [x for x in plugin.db.inf.find({"id": case_id})][0]

    target = await plugin.bot.utils.getUser(_case["target_id"])
    target = target if target is not None else "Unknown#0000"

    mod = await plugin.bot.utils.getUser(_case["moderator_id"])
    mod = mod if mod is not None else "Unknown#0000"

    reason = _case["reason"]
    reason = reason if len(reason) < 50 else f"{reason[:50]}..."

    timestamp = _case["timestamp"]
    case_type = _case["type"]

    icon_url = _case["target_av"]

    e = Embed(title=f"Case Info #{case}")
    e.set_thumbnail(url=icon_url)
    e.add_field(
        name="Type",
        value=f"```\n{case_type} \n```"
    )
    e.add_field(
        name="Target",
        value=f"```\n{target} ({_case['target_id']}) \n```"
    )
    e.add_field(
        name="Moderator",
        value=f"```\n{mod} ({_case['moderator_id']}) \n```"
    )
    e.add_field(
        name="Reason",
        value=f"```\n{reason} \n```"
    )
    e.add_field(
        name="Timestamp",
        value=f"```\n{timestamp} \n```"
    )

    await ctx.send(embed=e)