from ..functions.SetPunishment import setPunishment



async def run(plugin, ctx):
    await setPunishment(plugin, ctx, "mention_spam")