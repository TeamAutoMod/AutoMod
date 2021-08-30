import discord
import datetime
import traceback
import time

from ...Types import Embed
from ....utils.Views import MultiPageView

from ..sub.GetLogForCase import getLogForCase




def create_embed(option, user):
    main_embed = Embed(
        title="Recent cases"
    )
    if option == "guild":
        if user.icon != None:
            main_embed.set_thumbnail(
                url=user.icon.url
            )
    else:
        main_embed.set_thumbnail(
            url=user.display_avatar
        )
    main_embed.add_field(
        name="❯ History",
        value=""
    )
    return main_embed


def update_embed(main_embed, inp):
    main_embed._fields[0]["value"] = main_embed._fields[0]["value"] + f"\n{inp}"
    return None


options = {
    "guild": "guild",
    "user": "user",
    "mod": "mod"
}
async def userCases(plugin, ctx, user):
    message = await ctx.send(embed=Embed(description=plugin.i18next.t(ctx.guild, "searching", _emote="SEARCH")))
    # Check what we should search by
    option = None
    if isinstance(user, discord.Guild):
        option = options["guild"]
    if isinstance(user, discord.user.User) or isinstance(user, discord.User) or isinstance(user, discord.user.ClientUser):
        member = ctx.guild.get_member(user.id)
        if member is None:
            option = options["user"]
        elif member.guild_permissions.kick_members:
            option = options["mod"]
        else:
            option = options["user"]
    else:
        option = options["guild"]

    raw = [
        plugin.db.inf.get_doc(f"{ctx.guild.id}-{k}") for k, v in plugin.db.configs.get(ctx.guild.id, "case_ids").items() if v[option] == f"{user.id}"
    ]
    results = sorted(
        raw, 
        key=lambda e: int(e['id'].split("-")[-1]), 
        reverse=True
    )
    if len(results) < 1:
        return await message.edit(embed=Embed(description=plugin.i18next.t(ctx.guild, "no_cases_found", _emote="NO")))

    out = list()
    counts = {
        "warn": 0,
        "mute": 0,
        "kick": 0,
        "ban": 0
    }
    for e in results:
        if e["type"].lower() in counts:
            counts.update({
                e["type"].lower(): (counts[e["type"].lower()] + 1)
            })

        case = e['id'].split("-")[-1]

        reason = e["reason"]
        reason = reason if len(reason) < 40 else f"{reason[:40]}..."

        case_type = e["type"]
        if "restriction" in case_type.lower():
            case_type = "restriction"

        timestamp = e["timestamp"]
        if isinstance(timestamp, str):
            if not timestamp.startswith("<t"):
                dt = datetime.datetime.strptime(timestamp, "%d/%m/%Y %H:%M")
                timestamp = f"<t:{round(dt.timestamp())}>"
            # else:
                # timestamp = timestamp.replace(">", ":d>")
        else:
            timestamp = f"<t:{round(timestamp.timestamp())}>"


        log_url = await getLogForCase(plugin, ctx, e)

        out.append(
            "• {} ``{}`` {} {}"\
            .format(
                timestamp,
                case_type.upper(),
                f"[#{case}]({log_url})" if log_url is not None else f"#{case}",
                reason
            )
        )


    main_embed = create_embed(option, user)

    pages = []
    lines = 0
    max_lines = 5 if len(out) >= 5 else len(out)
    max_lines -= 1
    for i, inp in enumerate(out):
        if lines >= max_lines:
            update_embed(main_embed, inp)
            pages.append(main_embed)
            main_embed = create_embed(option, user)
            lines = 0
        else:
            lines += 1
            if len(out) <= i+1:
                update_embed(main_embed, inp)
                pages.append(main_embed)
            else:
                update_embed(main_embed, inp)
    
    text = []
    for k, v in counts.items():
        text.append(f"{v} {k if v == 1 else f'{k}s'}")
    text = ", ".join(text[:3]) + f" & {text[-1]}"

    for em in pages:
        em.set_footer(text=text)

    if len(pages) > 1:
        data = {
            "pages": pages,
            "page_number": 0
        }
        plugin.bot.case_cache.update({
            message.id: data
        })
        view = MultiPageView(0, len(pages))
        await message.edit(content=None, embed=pages[0], view=view)
    else:
        await message.edit(content=None, embed=pages[0])