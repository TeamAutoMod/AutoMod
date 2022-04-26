import discord
from discord.ui import View

from .buttons import CallbackBtn



bot_obj = None
def inject_bot_obj(bot):
    global bot_obj; bot_obj = bot
    

async def get_cases_from_cache(i: discord.Interaction, diff):
    data = bot_obj.case_cmd_cache.get(i.message.id, None)
    if data == None: return await i.response.send_message("No longer valid")

    c = len(data["pages"])
    pages = data["pages"]
    page_n = data["page_number"] + diff

    if page_n >= c:
        page_n = 0
    elif page_n < 0:
        page_n = c - 1
    
    embed = pages[page_n]
    data["page_number"] = page_n
    bot_obj.case_cmd_cache.update({
        i.message.id: data
    })

    return embed, c, page_n


class MultiPageView(View):
    def __init__(self, page, pages):
        super().__init__(timeout=None)
        self.id = ""

        self.add_item(CallbackBtn(
            "", self.first_page, "cases:first_page", disabled=page==0, emoji="⏪"
        ))

        self.add_item(CallbackBtn(
            "", self.prev_page, "cases:prev_page", disabled=page==0, emoji="◀️"
        ))
        self.add_item(CallbackBtn(
            "", self.delete, "cases:delete", disabled=False, style=discord.ButtonStyle.red, emoji="🗑️"
        ))
        self.add_item(CallbackBtn(
            "", self.next_page, "cases:next_page", disabled=page>=pages-1, emoji="▶️"
        ))

        self.add_item(CallbackBtn(
            "", self.last_page, "cases:last_page", disabled=page>=pages-1, emoji="⏩"
        ))


    @staticmethod
    async def first_page(i: discord.Interaction):
        embed, pages, page_count = await get_cases_from_cache(i, 100)
        await i.response.edit_message(
            embed=embed,
            view=MultiPageView(page=page_count, pages=pages)
        )


    @staticmethod
    async def prev_page(i: discord.Interaction):
        embed, pages, page_count = await get_cases_from_cache(i, -1)
        await i.response.edit_message(
            embed=embed,
            view=MultiPageView(page=page_count, pages=pages)
        )


    @staticmethod
    async def delete(i: discord.Interaction):
        await i.message.delete()
        if i.message.id in bot_obj.case_cmd_cache:
            del bot_obj.case_cmd_cache[i.message.id]

    
    @staticmethod
    async def next_page(i: discord.Interaction):
        embed, pages, page_count = await get_cases_from_cache(i, 1)
        await i.response.edit_message(
            embed=embed,
            view=MultiPageView(page=page_count, pages=pages)
        )


    @staticmethod
    async def last_page(i: discord.Interaction):
        embed, pages, page_count = await get_cases_from_cache(i, -100)
        await i.response.edit_message(
            embed=embed,
            view=MultiPageView(page=page_count, pages=pages)
        )