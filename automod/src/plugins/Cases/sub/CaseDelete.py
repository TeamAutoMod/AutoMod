from .DeleteLogMessage import deleteLogMessage

from ...Types import Embed
from ....utils.Views import ConfirmView



async def caseDelete(plugin, ctx, case):
    case_id = f"{ctx.guild.id}-{case}"
    if not plugin.db.inf.exists(case_id):
        return await ctx.send(plugin.i18next.t(ctx.guild, "case_not_found", _emote="NO"))

    message = None
    
    async def confirm(interaction):
        log_id = plugin.db.inf.get(case_id, "log_id")
        plugin.db.inf.delete(case_id)

        case_ids = plugin.db.configs.get(f"{ctx.guild.id}", "case_ids")
        del case_ids[case_id.split("-")[1]]
        plugin.db.configs.update(f"{ctx.guild.id}", "case_ids", case_ids)

        await deleteLogMessage(plugin, ctx, log_id)
        await interaction.response.edit_message(
            content=plugin.i18next.t(ctx.guild, "case_deleted", _emote="YES", case=case), 
            embed=None, 
            view=None
        )

    async def cancel(interaction):
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

    
    e = Embed(
        description=plugin.i18next.t(ctx.guild, "case_delete_description", case=case)
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