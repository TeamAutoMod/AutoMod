# type: ignore

import discord

from typing import Optional
import asyncio
import logging; log = logging.getLogger(__name__)

from ..schemas import GuildConfig


class LogQueue:
    def __init__(self, bot) -> None:
        self.bot = bot
        self.db = bot.db


    async def send_logs(self) -> None:
        while True: 
            await asyncio.sleep(2)
            for g, opt in self.bot.log_queue.copy().items():
                if sum([len(x) for x in opt.values()]) > 0:
                    for channel_type, entries in opt.items():
                        if len(entries) > 0:
                            chunk = entries[:max(min(3, len(entries)), 0)]
                            guild = self.bot.get_guild(g)

                            self.bot.log_queue[g][channel_type] = [x for x in entries if x not in chunk]
                            if guild != None:

                                log_channel_id = self.db.configs.get(guild.id, channel_type)
                                if log_channel_id != "":
                                    if log_channel_id != None:

                                        log_channel = guild.get_channel(int(log_channel_id))
                                        if log_channel != None:

                                            await self._execute(
                                                guild,
                                                channel_type,
                                                log_channel,
                                                chunk
                                            )
                                    else:
                                        if not self.db.configs.exists(guild.id):
                                            self.db.configs.insert(GuildConfig(guild, self.bot.config.default_prefix))
                                        else:
                                            self.db.configs.update(guild.id, channel_type, "")


    async def default_log(self, channel: discord.TextChannel, chunk: list) -> dict:
        msgs = {}
        for entry in chunk:
            msg = await channel.send(
                embed=entry["embed"],
                view=entry["embed"]._view if hasattr(entry["embed"], "_view") else None
            )
            if entry["has_case"] != False:
                msgs.update(
                    {
                        entry["has_case"]: msg
                    }
                )
        return msgs


    async def fetch_webhook(self, wid: int) -> Optional[discord.Webhook]:
        try:
            w = await self.bot.fetch_webhook(wid)
        except Exception:
            return None
        else:
            return w


    async def get_webhook(self, guild: discord.Guild, wid: int, channel_type: str) -> Optional[discord.Webhook]:
        if not guild.id in self.bot.webhook_cache:
            w = await self.fetch_webhook(wid)
            if w == None: 
                return None
            else:
                self.bot.webhook_cache.update({
                    guild.id: {
                        **{
                            k: None for k in ["mod_log", "server_log", "message_log", "join_log", "member_log", "voice_log", "report_log"] if k != channel_type
                        }, 
                        **{
                            channel_type: w
                        }
                    }
                })
                return w
        else:
            if self.bot.webhook_cache[guild.id][channel_type] == None:
                w = await self.fetch_webhook(wid)
                if w == None: 
                    return None
                else:
                    self.bot.webhook_cache[guild.id][channel_type] = w
                    return w
            else:
                if self.bot.webhook_cache[guild.id][channel_type] != wid:
                    w = await self.fetch_webhook(wid)
                    if w == None: 
                        return None
                    else:
                        self.bot.webhook_cache[guild.id][channel_type] = w
                        return w
                else:
                    return w
        
        
    async def _execute(self, guild: discord.Guild, channel_type: str, log_channel: discord.TextChannel, chunk: dict) -> None:
        log_messages = {}
        try:
            wid = self.bot.db.configs.get(guild.id, f"{channel_type}_webhook")
            if wid != "":
                webhook = await self.get_webhook(
                    guild,
                    int(wid),
                    channel_type
                )
                if webhook == None:
                    log_messages = await self.default_log(log_channel, chunk)
                else:
                    try:
                        with_case = {x["embed"]: x["has_case"] for x in chunk if x["has_case"] != False}
                        without_case = [x["embed"] for x in chunk if x["has_case"] == False]

                        if len(with_case) > 0:
                            log_message = await webhook.send(embeds=list(with_case.keys()), wait=True)

                            for case in with_case.values():
                                log_messages.update(
                                    {
                                        case: log_message
                                    }
                                )

                        if len(without_case) > 0:
                            with_view = [x for x in without_case if hasattr(x, "_view")]
                            for e in with_view: await webhook.send(embed=e, wait=True, view=e._view)
                            
                            without_view = [x for x in without_case if not hasattr(x, "_view")]
                            if len(without_view) > 0: await webhook.send(embeds=without_view, wait=True)
                    except Exception:
                        log_messages = await self.default_log(log_channel, chunk)
            else:
                log_messages = await self.default_log(log_channel, chunk)
        except Exception:
            pass
        else:
            if len(log_messages) > 0:
                for case, msg in log_messages.items():
                    self.db.cases.multi_update(f"{guild.id}-{case}", {
                        "log_id": f"{msg.id}",
                        "jump_url": f"{msg.jump_url}"
                    })