from ...Types import Embed



async def run(plugin, ctx):
    prefix = plugin.bot.get_guild_prefix(ctx.guild)
    normal = [f"{prefix}config punishment {x}" for x in ["invite_censor", "word_censor", "file_censor", "zalgo_censor", "caps_censor", "spam_detection", "mention_spam", "max_warns"]]
    e = Embed(
        title="Valid Options", 
        description="```\n{}\n```".format("\n".join(normal))
    )
    await ctx.send(embed=e)