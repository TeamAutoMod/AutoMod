import string
import traceback
import unidecode



async def run(plugin, ctx, user):
    old = user.nick if user.nick is not None else user.name
    new = ''.join(filter(lambda x: x in list(string.ascii_letters) or x.isspace(), unidecode.unidecode(old).lower()))
    try:
        await user.edit(nick=new)
    except Exception as ex:
        await ctx.send(plugin.i18next.t(ctx.guild, "asciify_failed", _emote="NO", error=ex))
    else:
        await ctx.send(plugin.i18next.t(ctx.guild, "user_asciified", _emote="YES", old=old, new=new))