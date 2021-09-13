import discord

from ...Types import Embed
from ....utils.Views import ConfirmView



async def run(plugin, ctx):
    role_id = plugin.db.configs.get(ctx.guild.id, "mute_role")
    if role_id == "":
        text = plugin.i18next.t(ctx.guild, "setup_muted_description_1")
    else:
        text = plugin.i18next.t(ctx.guild, "setup_muted_description_2")

    message = None
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

    async def confirm(interaction):
        await interaction.response.edit_message(
            content=plugin.i18next.t(ctx.guild, "start_mute", _emote="WAIT"), 
            embed=None, 
            view=None
        )
        msg = interaction.message

        global role
        if role_id != "":
            role = await plugin.bot.utils.getRole(ctx.guild, int(role_id))
        else:
            try:
                role = await ctx.guild.create_role(name="Muted")
            except Exception as ex:
                return await msg.edit(content=plugin.i18next.t(ctx.guild, "role_fail", _emote="NO", exc=ex))

        await msg.edit(content=f"{msg.content} \n{plugin.emotes.get('YES')} Role initialized!")
        try:
            for c in ctx.guild.categories:
                ov = c.overwrites
                ov.update({
                    role: discord.PermissionOverwrite(send_messages=False)
                })
                await c.edit(overwrites=ov)
        except Exception as ex:
            return await msg.edit(content=plugin.i18next.t(ctx.guild, "category_fail", _emote="NO", category=c.name, exc=ex))
        
        await msg.edit(content=f"{msg.content} \n{plugin.emotes.get('YES')} Category overwrites complete!")
        try:
            for c in ctx.guild.text_channels:
                ov = c.overwrites
                ov.update({
                    role: discord.PermissionOverwrite(send_messages=False)
                })
                await c.edit(overwrites=ov)
        except Exception as ex:
            return await msg.edit(content=plugin.i18next.t(ctx.guild, "text_fail", _emote="NO", channel=c.name, exc=ex))

        await msg.edit(content=f"{msg.content} \n{plugin.emotes.get('YES')} Text channel overwrites complete!")
        try:
            for c in ctx.guild.voice_channels:
                ov = c.overwrites
                ov.update({
                    role: discord.PermissionOverwrite(send_messages=False)
                })
                await c.edit(overwrites=ov)
        except Exception as ex:
            return await msg.edit(content=plugin.i18next.t(ctx.guild, "voice_fail", _emote="NO", channel=c.name, exc=ex))

        await msg.edit(content=f"{msg.content} \n{plugin.emotes.get('YES')} Voice channel overwrites complete!")
        if role_id == "":
            plugin.db.configs.update(ctx.guild.id, "mute_role", f"{role.id}")
        await msg.edit(content=plugin.i18next.t(ctx.guild, "mute_done", _emote="YES"))
    
    e = Embed(
        title="Muted role setup",
        description=text
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