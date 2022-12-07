# type: ignore

import discord
from discord.ui import View



class RoleChannelSelect(View):
    def __init__(
        self, 
        _type: str, 
        *args, 
        **kwargs
    ) -> None:
        super().__init__(*args, **kwargs)
        self.add_item(discord.ui.RoleSelect(
            custom_id=f"{_type}:roles",
            placeholder="Select Roles",
            min_values=1,
            max_values=25
        ))
        self.add_item(discord.ui.ChannelSelect(
            custom_id=f"{_type}:channels",
            placeholder="Select Channels",
            min_values=1,
            max_values=25
        ))