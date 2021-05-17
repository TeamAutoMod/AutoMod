import discord

from ...Types import Embed
from ....utils import MessageUtils



options = {
    "guild": "guild",
    "user": "target_id",
    "mod": "moderator_id"
}
async def userCases(plugin, ctx, user):
    # Check what we shoudl search by
    option = None
    if isinstance(user, discord.Guild):
        option = options["guild"]
    if isinstance(user, discord.User):
        member = ctx.guild.get_member(user.id)
        if member is None:
            option = options["user"]
        elif member.guild_permissions.kick_members:
            option = options["mod"]
        else:
            option = options["mod"]
    else:
        option = options["guild"]

    results = sorted([x for x in plugin.db.inf.find({option: f"{user.id}"})], key=lambda e: int(e['id'].split("-")[-1]), reverse=True)
    if len(results) < 1:
        return await ctx.send(plugin.t(ctx.guild, "no_cases_found", _emote="WARN"))

    out = list()
    for e in results:
        case = e['id'].split("-")[-1]

        target = await plugin.bot.utils.getUser(e["target_id"])
        target = target if target is not None else "Unknown#0000"

        mod = await plugin.bot.utils.getUser(e["moderator_id"])
        mod = mod if mod is not None else "Unknown#0000"

        reason = e["reason"]
        reason = reason if len(reason) < 50 else f"{reason[:50]}..."

        timestamp = e["timestamp"]
        case_type = e["type"]
        out.append({
            f"Case #{case}": "```\n• Target: {} \n• Mod: {} \n• Timestamp: {} \n• Type: {} \n• Reason: {} \n```"\
                .format(
                target,
                mod,
                timestamp,
                case_type,
                reason
            )
        })



    kwargs = {
        "title": "Recent Cases",
        "description": f"Showing results for ``{user.name}`` \nYou can also get more info about a case by using the ``case <case>`` command"
    }
    main_embed = Embed(**kwargs)

    pages = []
    fields = 0
    max_fields = 5 if len(out) >= 5 else len(out)
    max_fields -= 1
    for i, inp in enumerate(out):
        field_kwargs = {
            "name": list(inp.keys())[0],
            "value": list(inp.values())[0]
        }
        if fields >= max_fields:
            main_embed.add_field(**field_kwargs)
            pages.append(main_embed)
            main_embed = Embed(**kwargs)
            fields = 0
        else:
            fields += 1
            if len(out) <= i+1:
                main_embed.add_field(**field_kwargs)
                pages.append(main_embed)
            else:
                main_embed.add_field(**field_kwargs)
    
    for i, em in enumerate(pages):
        em.set_footer(text="Page: {}/{}".format(i+1, len(pages)))

    msg = await ctx.send(embed=pages[0])
    await MessageUtils.multiPage(plugin, ctx, msg, pages)