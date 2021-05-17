import asyncio
import traceback



async def multiPage(plugin, ctx, message, pages: list, timeout=60):
    page_count = len(pages)
    cur_page = 1

    for e in ("◀️", "▶️"):
        await message.add_reaction(str(e))

    def check(reaction, user):
        return user == ctx.author and str(reaction.emoji) in ("◀️", "▶️")
    while True:
        try:
            reaction, user = await plugin.bot.wait_for("reaction_add", timeout=timeout, check=check)

            if str(reaction.emoji) == "▶️" and cur_page != page_count:
                cur_page += 1
                await message.edit(embed=pages[cur_page-1])
                await message.remove_reaction(reaction, user)

            elif str(reaction.emoji) == "◀️" and cur_page > 1:
                cur_page -= 1
                await message.edit(embed=pages[cur_page-1])
                await message.remove_reaction(reaction, user)

            else:
                await message.remove_reaction(reaction, user)
            
        except asyncio.TimeoutError:
            await message.clear_reactions()
            break