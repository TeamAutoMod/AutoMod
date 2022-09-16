# type: ignore

import discord
from discord.ui import View

from .buttons import DeleteBtn, ActionedBtn



class DeleteView(View):
    def __init__(
        self, 
        *args, 
        **kwargs
    ) -> None:
        super().__init__(*args, **kwargs)
        self.add_item(DeleteBtn())


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
        *args, 
        **kwargs
    ) -> None:
        super().__init__(*args, **kwargs)
        self.add_item(ActionedBtn(bot))