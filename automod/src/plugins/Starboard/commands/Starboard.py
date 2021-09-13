from ...Types import Embed
from ....utils.Views import ConfirmView



async def run(plugin, ctx):
    message = None
    async def confirm(interaction):
        config = plugin.db.configs.get(f"{ctx.guild.id}", "starboard")
        config["enabled"] = not config["enabled"]
        plugin.db.configs.update(f"{ctx.guild.id}", "starboard", config)
        if config["enabled"] == False:
            key = "disabled_starboard"
        else:
            key = "enabled_starboard"
        await interaction.response.edit_message(content=plugin.i18next.t(ctx.guild, key, _emote="YES"), embed=None, view=None)
        


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

    config = plugin.db.configs.get(f"{ctx.guild.id}", "starboard")
    if config["enabled"] == False:
        key = "starboard_disabled"
    else:
        key = "starboard_enabled"
    e = Embed(
        description=plugin.i18next.t(ctx.guild, key)
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
