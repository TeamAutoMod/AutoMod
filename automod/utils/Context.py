import discord
from discord.ext import commands
import asyncio
import io



class Context(commands.Context):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    

    async def ensure_sending(self, content, *, escape_mentions=True, **kwargs):
        if escape_mentions:
            content = discord.utils.escape_mentions(content)

        if len(content) > 2000:
            f = io.BytesIO(content.encode())
            kwargs.pop("file", None)
            return await self.send(file=discord.File(f, filename="msg_too_long.txt"), **kwargs)
        else:
            return await self.send(content)


    # async def send(self, *args, **kwargs):
    #     msg = None
    #     try:
    #         msg = await self.reply(*args, mention_author=False, **kwargs)
    #     except Exception:
    #         msg = await super().send(*args, **kwargs)
    #     finally:
    #         return msg