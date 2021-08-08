import datetime
import humanize
import time

from ...Types import Embed



async def run(plugin, ctx, user):
    if user is None:
        user = member = ctx.author
    else:
        member = None if ctx.guild is None else await plugin.bot.utils.getUser(user.id)

    e = Embed(
        color=None if member is None else member.color
    )
    e.set_thumbnail(
        url=user.avatar_url_as()
    )
    e.add_field(
        name="❯ Information",
        value="• ID: {} \n• Profile: {} \n• Created at: <t:{}>"\
        .format(
            user.id,
            user.mention, 
            round(member.created_at.timestamp())
        )
    )
    if member is not None:
        roles = [r.mention for r in reversed(member.roles) if r != ctx.guild.default_role]
        e.add_field(
            name="❯ Server Information",
            value="• Joined at: <t:{}> \n• Roles: {}"\
            .format(
                round(member.joined_at.timestamp()),
                len(roles)
            )
        )
    warns = plugin.db.warns.get(f"{ctx.guild.id}-{user.id}", "warns")
    cases = list(filter(lambda x: x["guild"] == str(ctx.guild.id) and x["target_id"] == str(user.id), plugin.db.inf.find()))
    e.add_field(
        name="❯ Infractions",
        value="• Warns: {} \n• Cases: {}"\
        .format(
            warns if warns != None else "0",
            len(cases)
        )
    )
    await ctx.send(embed=e)