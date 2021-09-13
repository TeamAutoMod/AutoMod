from ...Types import Embed



async def run(plugin, ctx, user):
    if user == None:
        user = ctx.author

    e = Embed(
        title="Avatar of {0.name}#{0.discriminator}".format(user)
    )
    e.set_image(
        url=user.display_avatar
    )

    await ctx.send(embed=e)