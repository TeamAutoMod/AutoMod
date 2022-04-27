import discord

import asyncio
from typing import Union

from ...types import Embed
from ...bot import ShardedBotInstance



class DMProcessor(object):
    def __init__(self, bot: ShardedBotInstance) -> None:
        self.bot = bot
        self.colors = {
            "kick": 0xf79554,
            "ban": 0xff5c5c,
            "tempban": 0xff5c5c,
            "mute": 0xffdc5c,
            "warn": 0xffdc5c,
            "automod_rule_triggered": 0x2b80b8
        }
        self.queue = []
        self.bot.loop.create_task(self.dm_users())


    async def dm_users(self) -> None:
        while True:
            await asyncio.sleep(0.3)
            if len(self.queue) > 0:
                for kw in self.queue:
                    self.queue.remove(kw)
                    await self.actual_execute(**kw)

    
    def execute(self, msg: discord.Message, _type: str, _user: Union[discord.Member, discord.User], **opt) -> None:
        self.queue.append(
            {
                "msg": msg,
                "_type": _type,
                "_user": _user,
                **opt
            }
        )

    
    async def actual_execute(self, msg: discord.Message, _type: str, _user: Union[discord.Member, discord.User], **opt) -> None:
        try:
            e = Embed(
                color=self.colors[_type],
                description=self.bot.locale.t(msg.guild, f"dm_{_type}", **opt)
            )
            await _user.send(embed=e)
        except Exception:
            pass