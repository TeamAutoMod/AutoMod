import discord
from discord.ui import Button



class ConfirmBtn(Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.green, label="Confirm")
    
    async def callback(self, interaction):
        try:
            await self.view.confirm_callback(interaction)
        except discord.NotFound:
            pass
    

class CancelBtn(Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.red, label="Cancel")
    
    async def callback(self, interaction):
        await self.view.cancel_callback(interaction)  


class LinkBtn(Button):
    def __init__(self, _url, _label, *args, **kwargs):
        super().__init__(*args, style=discord.ButtonStyle.link, url=_url, label=_label, **kwargs)