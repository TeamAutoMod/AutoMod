from .DeleteLogMessage import deleteLogMessage

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
        await interaction.response.edit_message(content=plugin.i18next.t(ctx.guild, "case_deleted", _emote="YES", case=case), view=None)

    async def cancel(interaction):
        await interaction.response.edit_message(content=plugin.i18next.t(ctx.guild, "aborting"), view=None)

    async def timeout():
        if message is not None:
            await message.edit(content=plugin.i18next.t(ctx.guild, "aborting"), view=None)

    def check(interaction):
        return interaction.user.id == ctx.author.id and interaction.message.id == message.id

    
    message = await ctx.send(
        f"Are you sure you want to delete case **#{case}**? This actions can't be reverted.",
        view=ConfirmView(
            ctx.guild.id, 
            on_confirm=confirm, 
            on_cancel=cancel, 
            on_timeout=timeout,
            check=check
        )
    )