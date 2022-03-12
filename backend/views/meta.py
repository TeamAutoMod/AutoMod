import discord
from discord.ui import View

from .buttons import DeleteBtn



class DeleteView(View):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_item(DeleteBtn())