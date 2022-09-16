# type: ignore

import discord
from discord.ui import View

from typing import Tuple, TypeVar

from .buttons import CallbackBtn



T = TypeVar("T")


bot_obj = None
def inject_bot_obj(bot):
    global bot_obj; bot_obj = bot
    

async def get_cases_from_cache(
    plugin: T,
    i: discord.Interaction, 
    diff: int
) -> Tuple[
    discord.Embed, 
    int,
    int
]:
    _id = f"{i.guild.id}-{plugin._id_salt}"
    data = bot_obj.case_cmd_cache.get(_id, None)
    if data == None:
        await i.response.send_message("No longer valid")
        return None, None, None

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
        _id: data
    })

    return embed, c, page_n


class MultiPageView(View):
    def __init__(
        self, 
        page: int, 
        pages: int,
        id_salt: int
    ) -> None:
        super().__init__(timeout=None)
        self.id = ""
        self._id_salt = id_salt

        self.add_item(CallbackBtn(
            f"{page+1}/{pages}", self.none, "cases:none", disabled=True, style=discord.ButtonStyle.grey
        ))

        if page > 0:
            self.add_item(CallbackBtn(
                "◀", self.prev_page, "cases:prev_page", disabled=page==0
            ))

        if (page+1) < pages:
            self.add_item(CallbackBtn(
                "▶", self.next_page, "cases:next_page", disabled=page>=pages-1
            ))

    
    async def first_page(
        self,
        i: discord.Interaction
    ) -> None:
        embed, pages, page_count = await get_cases_from_cache(self, i, 100)
        if embed == None and pages == None and page_count == None: return
        await i.response.edit_message(
            embed=embed,
            view=MultiPageView(page=page_count, pages=pages, id_salt=self._id_salt)
        )


    async def prev_page(
        self,
        i: discord.Interaction
    ) -> None:
        embed, pages, page_count = await get_cases_from_cache(self, i, -1)
        if embed == None and pages == None and page_count == None: return
        await i.response.edit_message(
            embed=embed,
            view=MultiPageView(page=page_count, pages=pages, id_salt=self._id_salt)
        )


    async def delete(
        self,
        i: discord.Interaction
    ) -> None:
        await i.message.delete()
        if f"{i.guild.id}-{self._id_salt}" in bot_obj.case_cmd_cache:
            del bot_obj.case_cmd_cache[f"{i.guild.id}-{self._id_salt}"]


    @staticmethod
    async def none(
        _: discord.Interaction
    ) -> None:
        pass

    
    async def next_page(
        self,
        i: discord.Interaction
    ) -> None:
        embed, pages, page_count = await get_cases_from_cache(self, i, 1)
        if embed == None and pages == None and page_count == None: return
        await i.response.edit_message(
            embed=embed,
            view=MultiPageView(page=page_count, pages=pages, id_salt=self._id_salt)
        )


    async def last_page(
        self,
        i: discord.Interaction
    ) -> None:
        embed, pages, page_count = await get_cases_from_cache(self, i, -100)
        if embed == None and pages == None and page_count == None: return
        await i.response.edit_message(
            embed=embed,
            view=MultiPageView(page=page_count, pages=pages, id_salt=self._id_salt)
        )