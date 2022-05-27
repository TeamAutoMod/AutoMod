import discord

import logging; log = logging.getLogger()
import json
import asyncio

from typing import Union



class Translator(object):
    def __init__(
        self, 
        bot
    ) -> None:
        self.bot = bot

        self._langs = {}
        self._lang_cache = {}

        for l in bot.config.langs:
            with open(f"i18n/{l}.json", "r", encoding="utf8", errors="ignore") as f:
                self._langs[l] = json.load(f)
                log.info(f"📝 Loaded strings for language {l}")
    
    
    def t(
        self, 
        guild: discord.Guild, 
        key: str, 
        _emote: str = None, 
        **kwargs
    ) -> str:
        if not guild.id in self._lang_cache:
            try:
                lang = self.bot.db.configs.get(guild.id, "lang")
            except KeyError:
                self.bot.db.configs.update(f"{guild.id}", "lang", "en_US")
                lang = "en_US"
            self._lang_cache[guild.id] = lang
        else:
            lang = self._lang_cache[guild.id]
        global string
        try:
            string = self._langs[lang][key]
        except KeyError:
            channel = self.bot.get_channel(self.bot.config.error_channel)
            asyncio.run_coroutine_threadsafe(
                channel.send(f"{key} not found | {lang} | {guild.name} | {guild.id}"), 
                loop=self.bot.loop
            )

            string = self._langs["en_US"][key]
        finally:
            if "{emote}" in string:
                return str(string).format(emote=str(self.bot.emotes.get(_emote)), **kwargs)
            else:
                return str(string).format(**kwargs)


    def get(
        self, 
        key: str, 
        lang: str = "en_US", 
        **kwargs
    ) -> Union[str, None]:
        try:
            string = self._langs[lang][key]
        except KeyError:
            return None
        else:
            return string.format(**kwargs)
