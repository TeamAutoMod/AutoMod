# type: ignore

import discord
from discord.ext import commands as _commands

from typing import TypeVar
from toolbox import S as Object

from ..bot import ShardedBotInstance
from ..types import Embed



T = TypeVar("T")


class AutoModPluginBlueprint(_commands.Cog):
    def __init__(
        self, 
        bot: ShardedBotInstance,
        requires_premium: bool = False
    ):
        self.bot = bot
        self.db = bot.db
        self.config = bot.config
        self.locale = bot.locale
        self._requires_premium = requires_premium


    def get_prefix(
        self, 
        guild: discord.Guild
    ) -> str:
        if guild == None:
            return self.bot.config.default_prefix
        else:
            p = self.db.configs.get(guild.id, "prefix")
            return p if p != None else self.bot.config.default_prefix
    

    def error(
        self,
        ctx: discord.Interaction,
        error: T
    ) -> None:
        self.bot.dispatch("command_error", ctx, error)


    def before_load(
        self, 
        *args, 
        **kwargs
    ) -> None:
        super().cog_load(*args, **kwargs)

    
    def after_load(
        self, 
        *args, 
        **kwargs
    ) -> None:
        super().cog_unload(*args, **kwargs)


    def build_embed(
        self, 
        msg: discord.Message, 
        inp: dict
    ) -> Embed:
        inp = Object(inp)
        e = Embed(
            None,
            title=inp.title if hasattr(inp, "title") else None,
            description=inp.description if hasattr(inp, "description") else None
        )

        if hasattr(inp, "color"):
            try:
                color = int(inp.color, 16)
            except Exception:
                pass
            else:
                e.color = color
        
        if hasattr(inp, "timestamp"):
            e.timestamp = msg.created_at
        
        if hasattr(inp, "footer"):
            kwargs = {
                "text": inp.footer.text if hasattr(inp.footer, "text") else "",
                "icon_url": inp.footer.icon_url if hasattr(inp.footer, "icon_url") else ""
            }
            if len([x for x in list(kwargs.values()) if x == ""]) != 2:
                try: 
                    e.set_footer(**kwargs)
                except Exception: 
                    pass
        
        if hasattr(inp, "author"):
            kwargs = {
                "name": inp.author.text if hasattr(inp.author, "name") else "",
                "url": inp.author.url if hasattr(inp.author, "url") else "",
                "icon_url": inp.author.icon_url if hasattr(inp.author, "icon_url") else ""
            }
            if len([x for x in list(kwargs.values()) if x == ""]) != 3:
                try: 
                    e.set_author(**kwargs)
                except Exception: 
                    pass
        
        if hasattr(inp, "image"):
            kwargs = {
                "url": inp.image.url if hasattr(inp.image, "url") else "",
                "width": inp.image.width if hasattr(inp.image, "width") else None,
                "height": inp.image.height if hasattr(inp.image, "height") else None
            }
            if kwargs["url"] != "":
                try: 
                    e.set_image(**kwargs)
                except Exception:
                    pass

        if hasattr(inp, "thumbnail"):
            kwargs = {
                "url": inp.thumbnail.url if hasattr(inp.thumbnail, "url") else "",
                "width": inp.thumbnail.width if hasattr(inp.thumbnail, "width") else None,
                "height": inp.thumbnail.height if hasattr(inp.thumbnail, "height") else None
            }
            if kwargs["url"] != "":
                try: 
                    e.set_thumbnail(**kwargs)
                except Exception: 
                    pass
        
        if hasattr(inp, "fields"):
            if isinstance(inp.fields, list):
                for f in inp.fields:
                    field = Object(f)
                    inline = False
                    if hasattr(field, "name") and hasattr(field, "value"):
                        if hasattr(field, "value"):
                            if isinstance(field.value, bool):
                                inline = field.value
                        try: 
                            e.add_field(field.name, field.value, inline)
                        except Exception: 
                            pass
        return e