from ...Types import Embed



async def run(plugin, ctx):
    prefix = plugin.bot.get_guild_prefix(ctx.guild)
    normal = [f"{prefix}config disable {x}" for x in ["automod", "antispam", "persist", "message_logging", "welcome_logging", "voice_logging"]]
    e = Embed(
        title="Valid Modules", 
        description="```\n{}\n```".format("\n".join(normal))
    )
    await ctx.send(embed=e)