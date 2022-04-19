import discord



bot_obj = None
def inject_bot_obj(bot):
    global bot_obj; bot_obj = bot


class Embed(discord.Embed):
    #0x5764f1
    def __init__(self, color=None, **kwargs):
        if color != None:
            self.imu = False
        else:
            self.imu = True
        super().__init__(color=color, **kwargs)


    def _add_color(self):
        if self.imu == True:
            self.color = int(bot_obj.config.embed_color, 16)

    
    def set_thumbnail(self, url):
        self._add_color()
        super().set_thumbnail(url=url)
    

    def add_field(self, name, value, inline=False):
        self._add_color()
        super().add_field(name=name, value=value, inline=inline)

    
    def add_fields(self, fields: list):
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

    def blank_field(self, inline=False):
        self._add_color()
        return {
            "name": "⠀⠀", # This is a U+2800 char
            "value": "⠀⠀", # This is a U+2800 char
            "inline": inline
        }