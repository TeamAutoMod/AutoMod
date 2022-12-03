# type: ignore

import discord
from discord.ui import View



class RoleSelect(View):
    def __init__(
        self, 
        min_v: int,
        max_v: int,
        cid: str, 
        *args, 
        **kwargs
    ) -> None:
        super().__init__(*args, **kwargs)
        self.add_item(discord.ui.RoleSelect(
            custom_id=cid,
            placeholder=f"Select role{'' if max_v == 1 else 's'}",
            min_values=min_v,
            max_values=max_v
        ))