import discord
from ....utils.Views import ConfirmView



async def run(plugin, ctx):
    message = None
    async def cancel(interaction):
        await interaction.response.edit_message(content=plugin.i18next.t(ctx.guild, "aborting"), view=None)

    async def timeout():
        if message is not None:
            await message.edit(content=plugin.i18next.t(ctx.guild, "aborting"), view=None)

    def check(interaction):
        return interaction.user.id == ctx.author.id and interaction.message.id == message.id

    async def confirm(interaction):
        await interaction.response.edit_message(content=plugin.i18next.t(ctx.guild, "start_automod", _emote="YES"), view=None)
        msg = interaction.message

        punishments = plugin.db.configs.get(ctx.guild.id, "punishments")
        if not "5" in punishments:
            punishments.update({
                "5": "kick"
            })
        
        automod = {
            "invites": {"warns": 1},
            "everyone": {"warns": 1},

            "mention": {"threshold": 10},
            "lines": {"threshold": 15},

            "raid": {"status": False, "threshold": ""},

            "caps": {"warns": 1},
            "files": {"warns": 1},
            "zalgo": {"warns": 1},
            "censor": {"warns": 1},
            "spam": {"status": True, "warns": 3}
        }

        plugin.db.configs.update(ctx.guild.id, "punishments", punishments)
        plugin.db.configs.update(ctx.guild.id, "automod", automod)

        prefix = plugin.bot.get_guild_prefix(ctx.guild)
        await msg.edit(content=plugin.i18next.t(ctx.guild, "automod_done", _emote="YES", prefix=prefix))

    
    message = await ctx.send(
        f"This will setup the basic automod config. If you've already setup a few settings, those will be overwritten.",
        view=ConfirmView(
            ctx.guild.id, 
            on_confirm=confirm, 
            on_cancel=cancel, 
            on_timeout=timeout,
            check=check
        )
    )