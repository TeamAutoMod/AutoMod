import datetime

from ...Types import Embed



async def caseInfo(plugin, ctx, case):
    case_id = f"{ctx.guild.id}-{case}"
    if not plugin.db.inf.exists(case_id):
        return await ctx.send(plugin.i18next.t(ctx.guild, "case_not_found", _emote="NO"))
    
    _case = [x for x in plugin.db.inf.find({"id": case_id})][0]

    target = await plugin.bot.utils.getUser(_case["target_id"])
    target = target if target is not None else "Unknown#0000"

    mod = await plugin.bot.utils.getUser(_case["moderator_id"])
    mod = mod if mod is not None else "Unknown#0000"

    reason = _case["reason"]
    reason = reason if len(reason) < 50 else f"{reason[:50]}..."

    timestamp = _case["timestamp"]
    case_type = _case["type"]

    e = Embed()
    e.set_thumbnail(
        url=_case["target_av"]
    )
    e.add_field(
        name="❯ Case",
        value=f"``#{case}``"
    )
    e.add_field(
        name="❯ Type",
        value=f"``{case_type}``"
    )
    e.add_field(
        name="❯ Target",
        value=f"``{target}`` ({_case['target_id']})",
    )
    e.add_field(
        name="❯ Moderator",
        value=f"``{mod}`` ({_case['moderator_id']})",
    )
    e.add_field(
        name="❯ Reason",
        value=f"``{reason}``"
    )
    if not timestamp.startswith("<t"):
        dt = datetime.datetime.strptime(timestamp, "%d/%m/%Y %H:%M")
        timestamp = f"<t:{round(dt.timestamp())}>"
    e.add_field(
        name="❯ Timestamp",
        value=f"{timestamp}"
    )

    await ctx.send(embed=e)