<<<<<<< HEAD
import discord
from discord.ui import View

from .buttons import DeleteBtn



class DeleteView(View):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
=======
import discord
from discord.ui import View

from .buttons import DeleteBtn



class DeleteView(View):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
>>>>>>> 049ddcde2a090ba7492f82b75ee62cc010bbc290
        self.add_item(DeleteBtn())