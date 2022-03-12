import discord



class Embed(discord.Embed):
    #0x504f73
    def __init__(self, color=0x5764f0, **kwargs):
        super().__init__(color=color, **kwargs)
    

    def add_field(self, name, value, inline=False):
        super().add_field(name=name, value=value, inline=inline)

    
    def add_fields(self, fields: list):
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
        return {
            "name": "⠀",
            "value": "⠀",
            "inline": inline
        }