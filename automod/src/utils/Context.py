import discord
from discord.ext import commands
import asyncio
import io


yes = "<:greenTick:751915988143833118>" # green tick
no = "<:redTick:751916874522034239>" # red tick


class Context(commands.Context):
    """A custom class for commands.Context"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


    async def prompt(self, message, *, timeout=60.0, delete_after=True, author_id=None):
        if not self.channel.permissions_for(self.me).add_reactions:
            raise RuntimeError("Harpoon doesn't have add_reactions perms.")

        author_id = author_id or self.author.id
        msg = await self.send(message)

        confirm = None

        def check(payload):
            nonlocal confirm

            if payload.message_id != msg.id or payload.user_id != author_id:
                return False
            
            c_point = str(payload.emoji)

            if c_point == yes:
                confirm = True
                return True
            elif c_point == no:
                confirm = False
                return True
            return False

        for e in (yes, no):
            await msg.add_reaction(e)

        try:
            await self.bot.wait_for("raw_reaction_add", check=check, timeout=timeout)
        except asyncio.TimeoutError:
            confirm = None
        
        try:
            if delete_after:
                await msg.delete()
        finally:
            return confirm
    

    async def ensure_sending(self, content, *, escape_mentions=True, **kwargs):
        if escape_mentions:
            content = discord.utils.escape_mentions(content)

        if len(content) > 2000:
            f = io.BytesIO(content.encode())
            kwargs.pop("file", None)
            return await self.send(file=discord.File(f, filename="msg_too_long.txt"), **kwargs)
        else:
            return await self.send(content)
