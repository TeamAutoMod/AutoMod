import datetime



def Tag(ctx, name, content):
    return {
        "id": f"{ctx.guild.id}-{name}",
        "uses": 0,

        "name": name,
        "content": content,

        "author": f"{ctx.author.id}",
        "editor": None,

        "created": datetime.datetime.utcnow(),
        "edited": None,
    }