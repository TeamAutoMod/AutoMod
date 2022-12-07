# type: ignore

import discord
from discord.ui import View

from typing import Callable

from .buttons import DeleteBtn, ActionedBtn, DeleteHighlightBtn, LinkBtn



class DeleteView(View):
    def __init__(
        self, 
        user_id: int,
        *args, 
        **kwargs
    ) -> None:
        super().__init__(*args, **kwargs)
        self.add_item(DeleteBtn(lambda x: x == user_id))


class ChoiceView(View):
    def __init__(
        self, 
        placeholder: str, 
        guild: discord.Guild, 
        opt: list, 
        *args, 
        **kwargs
    ) -> None:
        super().__init__(*args, **kwargs)
        self.add_item(discord.ui.Select(
            custom_id=f"{guild.id}:replies",
            placeholder=placeholder,
            min_values=1,
            max_values=1,
            options=[
                discord.SelectOption(
                    label=x,
                    value=x
                ) for x in opt
            ]
        ))


class ActionedView(View):
    def __init__(
        self, 
        bot,
        user_id: int,
        *args, 
        **kwargs
    ) -> None:
        super().__init__(*args, **kwargs)
        self.add_item(ActionedBtn(bot, lambda x: x == user_id))


class HighlightDMView(View):
    def __init__(
        self, 
        bot,
        user_id: int,
        msg: discord.Message,
        delete_func: Callable,
        func_args: dict,
        *args, 
        **kwargs
    ) -> None:
        super().__init__(*args, **kwargs)
        self.add_item(LinkBtn(_url=f"{msg.jump_url}", _label="View Message"))
        self.add_item(DeleteHighlightBtn(bot, lambda x: x == user_id, delete_func, func_args))