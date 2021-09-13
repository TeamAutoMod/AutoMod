import datetime
import time
import pytz
utc = pytz.UTC

from ...Types import Embed
from ....utils import Permissions
from ....utils.Views import ConfirmView



async def run(plugin, ctx, join, age):
    if ctx.guild.id in plugin.running_cybernukes:
        return await ctx.send(plugin.i18next.t(ctx.guild, "cybernuke_running", _emote="NO"))

    if join.unit is None:
        join.unit = "m"
    if age.unit is None:
        age.unit = "m"

    join = utc.localize(datetime.datetime.utcfromtimestamp(time.time() - join.to_seconds(ctx)))
    age = utc.localize(datetime.datetime.utcfromtimestamp(time.time() - age.to_seconds(ctx)))

    targets = list(filter(lambda x: x.joined_at >= join and x.created_at >= age, ctx.guild.members))
    if len(targets) < 1:
        return await ctx.send(plugin.i18next.t(ctx.guild, "no_targets", _emote="NO"))
    if len(targets) > 100:
        return await ctx.send(plugin.i18next.t(ctx.guild, "too_many_targets", _emote="NO"))


    message = None
    async def cancel(interaction):
        plugin.running_cybernukes.remove(ctx.guild.id)
        e = Embed(
            description=plugin.i18next.t(ctx.guild, "aborting")
        )
        await interaction.response.edit_message(embed=e, view=None)

    async def timeout():
        if message is not None:
            e = Embed(
                description=plugin.i18next.t(ctx.guild, "aborting")
            )
            await message.edit(embed=e, view=None)

    def check(interaction):
        return interaction.user.id == ctx.author.id and interaction.message.id == message.id

    async def confirm(interaction):
        case = plugin.bot.utils.newCase(ctx.guild, "Cybernuke", targets[0], ctx.author, f"Cybernuke ({len(targets)})")
        banned = 0
        for i, t in enumerate(targets):
            reason = f"Cybernuke ``({i+1}/{len(targets)})``"

            if not Permissions.is_allowed(ctx, ctx.author, t):
                pass
            else:
                try:
                    await ctx.guild.ban(t, reason=reason)
                except Exception:
                    pass
                else:
                    banned += 1
                    dm_result = await plugin.bot.utils.dmUser(
                        ctx.message, 
                        "cybernuke", 
                        t, 
                        _emote="HAMMER", 
                        color=0xff5c5c,
                        moderator=ctx.message.author, 
                        guild_name=ctx.guild.name, 
                        reason=reason
                    )

                    await plugin.action_logger.log(
                        ctx.guild,
                        "cybernuke",
                        moderator=ctx.message.author, 
                        moderator_id=ctx.message.author.id,
                        user=t,
                        user_id=t.id,
                        reason=reason,
                        case=case,
                        dm=dm_result
                    )
        
        plugin.running_cybernukes.remove(ctx.guild.id)
        await interaction.response.edit_message(
            content=plugin.i18next.t(ctx.guild, "users_cybernuked", _emote="YES", banned=banned, total=len(targets), case=case), 
            embed=None, 
            view=None
        )

    plugin.running_cybernukes.append(ctx.guild.id)
    e = Embed(
        description=plugin.i18next.t(ctx.guild, "cybernuke_description", targets=len(targets))
    )
    message = await ctx.send(
        embed=e,
        view=ConfirmView(
            ctx.guild.id, 
            on_confirm=confirm, 
            on_cancel=cancel, 
            on_timeout=timeout,
            check=check
        )
    )