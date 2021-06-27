import unicodedata


def toStr(char):
    digit = f"{ord(char):x}".upper()
    name = unicodedata.name(char, "Name not found")
    return f"{char} - {digit:>04} | {name.upper()}"


async def run(plugin, ctx, chars):
    msg = "\n".join(map(toStr, chars))
    await ctx.ensure_sending("```\n{}\n```".format(msg))
