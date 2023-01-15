# type: ignore

import discord

from typing import Dict, Any, Union, Optional

from ..__obj__ import TypeHintedToolboxObject as Object



NAME_MAP = {
    "warn": "warn",
    "ban": "ban",
    "tempban": "tempban",
    "kick": "kick",
    "only delete": "delete",
    "grant role": "grant_role",
    "remove role": "remove_role"
}


class AutomodPunishment:
    def __init__(self, data: Dict[str, Any], action_processor: Any) -> None:
        self._transformed = Object(data)
        self._action_processor = action_processor

        self._oname = self._transformed.type
        self.name = NAME_MAP[self._transformed.type]

        self._functions_map = {
            "warn": self._action_processor.execute,
            "ban": self._action_processor.ban,
            "kick": self._action_processor.kick,
            "tempban": self._action_processor.tempban,
            "only_delete": None,
            "grant_role": self._action_processor.grant_role,
            "remove_role": self._action_processor.remove_role
        }

    
    async def execute(
        self, 
        msg: Union[discord.Message, discord.Interaction],
        mod: discord.Member, 
        user: Union[discord.Member, discord.User], 
        reason: str, 
        **special_log_kwargs
    ) -> Optional[Exception]:
        func = self._functions_map[self.name]
        if func != None:
            if self.name == "warn":
                return await func(msg, mod, user, reason, **special_log_kwargs)
            else:
                if "(" in reason:
                    raw_reason = reason.split("(")[0]
                else:
                    raw_reason = reason

                log_kwargs = {
                    "mod": mod,
                    "mod_id": mod.id,
                    "user": f"{user.name}#{user.discriminator}",
                    "user_id": user.id,
                    "reason": reason,
                    "raw_reason": raw_reason,
                    **special_log_kwargs
                }
                return await func(msg, mod, user, reason, **log_kwargs)
