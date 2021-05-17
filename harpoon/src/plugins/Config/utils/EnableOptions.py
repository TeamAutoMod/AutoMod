from ...Types import Embed



async def run(plugin, ctx):
    prefix = plugin.bot.get_guild_prefix(ctx.guild)
    normal = [f"{prefix}config enable {x}" for x in ["automod", "antispam", "persist"]]
    with_channel = [f"{prefix}config enable {x} <channel>" for x in ["message_logging", "welcome_logging", "voice_logging"]]
    e = Embed(
        title="Valid Modules", 
        description="```\n{}\n```".format("\n".join([*normal, *with_channel]))
    )
    await ctx.send(embed=e)
