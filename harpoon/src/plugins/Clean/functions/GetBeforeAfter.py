import discord



def getBeforeAfter(ctx, before=None, after=None):
    if before is None:
        before = ctx.message
    else:
        before = discord.Object(id=before)
    if after is not None:
        after = discord.Object(id=after)
    return before, after
