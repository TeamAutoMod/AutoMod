from ..sub.UserCases import userCases



async def run(plugin, ctx, user):
    # If nothing is passed, we check for all the guilds cases
    if user is None:
        user = ctx.guild
    
    await userCases(plugin, ctx, user)