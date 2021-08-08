import discord

import googletrans

from ...Types import Embed



async def run(plugin, ctx, text):
    if text is None:
        ref = ctx.message.reference
        if ref is not None and isinstance(ref.resolved, discord.Message):
            text = ref.resolved.content
        else:
            return await ctx.send(plugin.i18next.t(ctx.guild, "no_text", _emote="NO"))
    
    try:
        res = await plugin.bot.loop.run_in_executor(None, plugin.google.translate, text)
    except Exception as ex:
        return await ctx.send(plugin.i18next.t(ctx.guild, "translation_failed", _emote="NO", error=ex))
    
    e = Embed()
    e.add_field(
        name="❯ From {}".format(googletrans.LANGUAGES.get(res.src, "auto-detected").title()),
        value=res.origin
    )
    e.add_field(
        name="❯ To {}".format(googletrans.LANGUAGES.get(res.dest, "Unknown").title()),
        value=res.text
    )
    await ctx.send(embed=e)
