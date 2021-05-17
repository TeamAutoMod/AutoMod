from ..functions.SetupAddSelfrole import setupAddSelfrole



async def run(plugin, ctx, name, role):
    roles = plugin.db.configs.get(ctx.guild.id, "selfroles")

    await setupAddSelfrole(plugin, ctx, name, role, roles)