# type: ignore

import discord
from discord.ext import commands

from toolbox import S as Object
import datetime
from typing import Literal, Union
import re
import logging; log = logging.getLogger()

from .. import AutoModPluginBlueprint, ShardedBotInstance
from ...schemas import Responder
from ...types import Embed, E
from ...modals import ResponseCreateModal, ResponseEditModal



MAX_RESPONDERS_PER_GUILD = 15


class AutoResponderPlugin(AutoModPluginBlueprint):
    """Plugin for autoresponders"""
    def __init__(
        self, 
        bot: ShardedBotInstance
    ) -> None:
        super().__init__(bot)
        self._r = {}
        self._position_funcs = {
            "startswith": lambda msg, triggers: (
                msg.lower().startswith(tuple([_.lower() for _ in triggers]))
            ),
            "endswith": lambda msg, triggers: (
                msg.lower().endswith(tuple([_.lower() for _ in triggers]))
            ),
            "contains": lambda msg, triggers: (
                any(trigger.lower() in msg.lower() for trigger in triggers)
            ),
            "regex": lambda msg, regex: (
                re.search(re.compile(regex, re.IGNORECASE), msg)
            )
        }
        self.bot.loop.create_task(self.cache_responders())
        

    def add_responder(
        self, 
        ctx: discord.Interaction, 
        name: str, 
        content: str,
        trigger: Union[
            str,
            list
        ],
        position: str,
        ignore_mods: bool
    ) -> None:
        data = {
            name: {
                "content": content,
                "author": ctx.user.id,
                "trigger": trigger,
                "position": position,
                "ignore_mods": ignore_mods
            }
        }
        if not ctx.guild.id in self._r:
            self._r[ctx.guild.id] = data
        else:
            self._r[ctx.guild.id].update(data)

        self.db.responders.insert(Responder(ctx, name, content, trigger, position, ignore_mods))
        return None


    def remove_responder(
        self, 
        guild: discord.Guild, 
        name: str
    ) -> None:
        self._r[guild.id].pop(name)
        self.db.responders.delete(f"{guild.id}-{name}")
        return None


    def update_responder(
        self, 
        ctx: discord.Interaction, 
        name: str, 
        content: str,
        trigger: str
    ) -> None:
        self._r[ctx.guild.id][name].update({
            "content": content,
            "trigger": trigger
        })
        self.db.responders.multi_update(f"{ctx.guild.id}-{name}", {
            "content": content,
            "editor": f"{ctx.user.id}",
            "edited": datetime.datetime.now(),
            "trigger": trigger
        })


    async def cache_responders(
        self
    ) -> None:
        _ = True
        while _:
            _ = False
            for e in self.db.responders.find({}):
                _id = int(e["id"].split("-")[0])
                data = {
                    e["name"]: {
                        "content": e["content"],
                        "author": int(e["author"]),
                        "trigger": e["trigger"],
                        "position": e["position"],
                        "ignore_mods": e.get("ignore_mods", True)
                    }
                }
                
                if self.validate_name(list(data.keys())[0]):
                    if not _id in self._r:
                        self._r[_id] = data
                    else:
                        self._r[_id].update(data)


    def update_uses(
        self, 
        _id: str
    ) -> None:
        self.bot.used_tags += 1
        cur = self.db.responders.get(_id, "uses")
        if cur == None:
            self.db.responders.update(_id, "uses", 1)
        else:
            self.db.responders.update(_id, "uses", cur+1)


    def validate_name(
        self,
        name: str
    ) -> bool:
        for c in name:
            if c == "-" or c == "_":
                pass
            else:
                if re.compile(r"^[a-zA-Z]+$").match(c) or c.isdigit():
                    pass
                else:
                    return False
        return True
    

    def validate_regex(
        self, 
        regex: str
    ) -> bool:
        try:
            re.compile(regex)
        except re.error:
            return False
        else:
            return True


    def get_responders(
        self,
        guild: discord.Guild,
    ) -> dict:
        return self._r[guild.id]
    

    def is_mod(
        self,
        user: discord.Member
    ) -> bool:
        return (
            user.guild_permissions.ban_members == True \
            or user.guild_permissions.kick_members == False \
            or user.guild_permissions.manage_messages == False
        )

    
    _responders = discord.app_commands.Group(
        name="auto-responders",
        description="📝 Manage text based responses",
        default_permissions=discord.Permissions(manage_messages=True)
    )
    @_responders.command(
        name="list",
        description="📝 Shows a list of all auto responders"
    )
    async def auto_responders(
        self, 
        ctx: discord.Interaction
    ) -> None:
        """
        autoresponders_show_help
        examples:
        -auto-responders list
        """
        if ctx.guild.id in self._r:
            responders = self.get_responders(ctx.guild)
            if len(responders) > 0:
                e = Embed(
                    ctx,
                    title=f"Auto Responders ({len(responders)}/{MAX_RESPONDERS_PER_GUILD})",
                )
                for i, (name, obj) in enumerate(responders.items()):
                    if (i+1) % 2 == 0: e.add_fields([e.blank_field(True, 5)])
                    e.add_field(
                        name=f"**__{name}__**",
                        value="**• Search position:** {} \n**• Ignore mods:** {} \n**• Trigger:** {} \n**• Response:** \n```{}\n```".format(
                            {
                                "startswith": "Starts with",
                                "endswith": "Ends with",
                                "contains": "Contains", 
                                "regex": "RegEx"
                            }[obj["position"]],
                            self.bot.emotes.get("YES") if obj.get("ignore_mods", True) == True else self.bot.emotes.get("NO"),
                            f"``{obj['trigger']}``" if not isinstance(obj["trigger"], list) else ', '.join([f"``{_}``" for _ in obj["trigger"]]),
                            obj["content"]
                        ),
                        inline=True
                    )
                await ctx.response.send_message(embed=e)
            else:
                await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "no_responders", _emote="NO"), 0))
        else:
            await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "no_responders", _emote="NO"), 0))

    
    @_responders.command(
        name="add",
        description="✅ Creates a new auto responder"
    )
    @discord.app_commands.describe(
        position="Where or how  to search messages for triggers",
        ignore_mods="Whether to ignore mods for this responder"
    )
    @discord.app_commands.default_permissions(manage_messages=True)
    async def addresponder(
        self, 
        ctx: discord.Interaction,
        position: Literal[
            "Starts with",
            "Ends with",
            "Contains",
            "RegEx"
        ],
        ignore_mods: Literal[
            "True",
            "False"
        ] = "True"
    ) -> None:
        """
        autoresponders_add_help
        examples:
        -auto-responders position:Starts with
        -auto-responders position:RegEx
        """
        position = position.replace(" ", "").lower()
        ignore_mods = ignore_mods.lower()
        async def callback(
            i: discord.Interaction
        ) -> None:
            name, content, trigger, _ = self.bot.extract_args(i, "name", "content", "trigger", "vars")

            if self.validate_name(name.lower()) == False:
                return await i.response.send_message(embed=E(self.locale.t(i.guild, "invalid_name", _emote="NO"), 0))

            if position == "regex":
                if self.validate_regex(trigger) == False:
                    return await i.response.send_message(embed=E(self.locale.t(i.guild, "invalid_regex_responder", _emote="NO"), 0))
            else:
                trigger = trigger.split(", ")

            if len(self._r.get(i.guild_id, [])) > MAX_RESPONDERS_PER_GUILD:
                return await i.response.send_message(embed=E(self.locale.t(i.guild, "max_responders", _emote="NO", max_responders=MAX_RESPONDERS_PER_GUILD), 0))

            name = name.lower()
            if i.guild.id in self._r:
                if name in self._r[i.guild.id]:
                    return await i.response.send_message(embed=E(self.locale.t(i.guild, "response_alr_exists", _emote="NO"), 0))
            
            if ignore_mods == "true":
                _ignore_mods = True
            else:
                _ignore_mods = False

            self.add_responder(i, name, content, trigger, position, _ignore_mods)
            await i.response.send_message(embed=E(self.locale.t(i.guild, "response_added", _emote="YES", name=name), 1))
        
        modal = ResponseCreateModal(self.bot, "Create Auto Responder", position, callback)
        await ctx.response.send_modal(modal)


    @_responders.command(
        name="delete",
        description="❌ Deletes the given auto responder"
    )
    @discord.app_commands.describe(
        name="Name of the auto responder",
    )
    @discord.app_commands.default_permissions(manage_messages=True)
    async def delresponder(
        self, 
        ctx: discord.Interaction, 
        name: str
    ) -> None:
        """
        autoresponders_delete_help
        examples:
        -auto-responders delete test_responder
        """
        name = name.lower()
        if ctx.guild.id in self._r:
            if not name in self._r[ctx.guild.id]:
                await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "response_doesnt_exists", _emote="NO"), 0))
            else:
                self.remove_responder(ctx.guild, name)
                await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "response_removed", _emote="YES"), 1))
        else:
            await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "no_responders", _emote="NO"), 0))


    @_responders.command(
        name="edit",
        description="🔀 Edits an existing auto responder"
    )
    @discord.app_commands.describe(
        name="Name of the auto responder"
    )
    @discord.app_commands.default_permissions(manage_messages=True)
    async def editresponder(
        self, 
        ctx: discord.Interaction, 
        name: str, 
    ) -> None:
        """
        autoresponder_edit_help
        examples:
        -auto-responders edit test_responder
        """
        name = name.lower()
        if ctx.guild.id in self._r:
            if not name in self._r[ctx.guild.id]:
                await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "response_doesnt_exists", _emote="NO"), 0))
            else:
                obj = self._r[ctx.guild.id][name]
                async def callback(
                    i: discord.Interaction
                ) -> None:
                    content, trigger, _ = self.bot.extract_args(i, "content", "trigger", "vars")
                    if obj["position"] == "regex":
                        if self.validate_regex(trigger) == False:
                            return await i.response.send_message(embed=E(self.locale.t(i.guild, "invalid_regex_responder", _emote="NO"), 0))
                    else:
                        trigger = trigger.split(", ")

                    self.update_responder(i, name, content, trigger)
                    await i.response.send_message(embed=E(self.locale.t(i.guild, "response_edited", _emote="YES", name=name), 1))

                modal = ResponseEditModal(
                    self.bot, 
                    f"Edit Auto Responder {name}", 
                    obj["position"], 
                    obj["trigger"] if not isinstance(obj["trigger"], list) else ", ".join(obj["trigger"]),
                    obj["content"],
                    callback
                )
                await ctx.response.send_modal(modal)
        else:
            await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "no_responders", _emote="NO"), 0))


    @AutoModPluginBlueprint.listener()
    async def on_message(
        self,
        msg: discord.Message
    ) -> None:
        if msg.author.bot == True: return
        if msg.guild == None: return
        if not msg.guild.id in self._r: return

        if not msg.guild.chunked:
            await msg.guild.chunk(cache=True)
        
        for name, obj in self.get_responders(msg.guild).items():
            if obj.get("ignore_mods", True) == True:
                if self.is_mod(msg.author): continue
                
            if (self._position_funcs[obj["position"]])(msg.content, obj["trigger"]) == True:
                try:
                    await msg.channel.send(content=str(obj["content"]).format(
                        user=f"<@{msg.author.id}>",
                        username=f"{msg.author.name}",
                        avatar=f"{msg.author.avatar.url if msg.author.avatar != None else msg.author.display_avatar.url}",
                        server=f"{msg.guild.name}",
                        channel=f"{msg.channel.name}"
                    ))
                except Exception:
                    pass
                else:
                    self.update_uses(f"{msg.guild.id}-{name}")

        
