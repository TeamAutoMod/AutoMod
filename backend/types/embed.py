import discord



bot_obj = None
def inject_bot_obj(bot) -> None:
    global bot_obj; bot_obj = bot


class Embed(discord.Embed):
    #0x5764f1
    def __init__(self, color: int = None, **kwargs) -> None:
        if color != None:
            self.imu = False
        else:
            self.imu = True
        super().__init__(color=color, **kwargs)
        self._add_color()


    def _add_color(self) -> None:
        if self.imu == True:
            self.color = int(bot_obj.config.embed_color, 16)

    
    def set_thumbnail(self, url: str) -> None:
        self._add_color()
        super().set_thumbnail(url=url)

    
    def set_footer(self, *args, **kwargs):
        self._add_color()
        super().set_footer(*args, **kwargs)
    

    def add_field(self, name: str, value: str, inline: bool = False) -> None:
        self._add_color()
        super().add_field(name=name, value=value, inline=inline)

    
    def add_fields(self, fields: list) -> None:
        self._add_color()
        for field in fields:
            if not isinstance(field, dict):
                raise Exception("Fields have to be dicts")
            else:
                self.add_field(
                    name=field["name"],
                    value=field["value"],
                    inline=field.get("inline", False)
                )


    def blank_field(self, inline: bool = False, length: int = 2) -> dict:
        self._add_color()
        return {
            "name": "⠀" * length, # This is a U+2800 char
            "value": "⠀" * length, # This is a U+2800 char
            "inline": inline
        }

    
    def dash_field(self, length: int = 29) -> dict:
        self._add_color()
        return {
            "name": "​", # This is a U+200b char
            "value": "▬" * length,
            "inline": False
        }

    
    def credits(self) -> None:
        self.set_footer(
            text=f"Made with ❤ by paul#0009"
        )
