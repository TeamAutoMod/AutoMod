from ..functions.SetupRemoveSelfrole import setupRemoveSelfrole



async def run(plugin, ctx, name):
    roles = plugin.db.configs.get(ctx.guild.id, "selfroles")

    await setupRemoveSelfrole(plugin, ctx, name, roles)