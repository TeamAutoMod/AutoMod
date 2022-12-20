# type: ignore

import discord
from discord.ext import commands

from ...__obj__ import TypeHintedToolboxObject as Object
from typing import Literal, Dict, Any
import datetime
import re
import logging; log = logging.getLogger()

from .. import ShardedBotInstance
from ...schemas import CustomCommand
from ...types import Embed, E
from ...modals import CommandCreateModal, CommandEditModal
from ..responder.plugin import AutoResponderPlugin



class TagsPlugin(AutoResponderPlugin):
    """Plugin for tags (custom commands)"""
    def __init__(self, bot: ShardedBotInstance) -> None:
        super().__init__(bot)
        self._commands = {}
        self._cached_from_api = {}
        self.bot.loop.create_task(self.cache_commands())


    async def custom_callback(self, ctx: discord.Interaction) -> None:
        if ctx.guild_id in self._commands:
            data = self._commands[ctx.guild_id].get(
                ctx.command.qualified_name.lower(),
                None
            )
            if data != None:
                cmd = Object(data)
                self.update_uses(f"{ctx.guild_id}-{ctx.command.qualified_name.lower()}")

                content = str(cmd.content)
                for k, v in {
                    "{user}": f"<@{ctx.user.id}>",
                    "{username}": f"{ctx.user.name}",
                    "{avatar}": f"{ctx.user.avatar.url if ctx.user.avatar != None else ctx.user.display_avatar.url}",
                    "{server}": f"{ctx.guild.name}",
                    "{channel}": f"{ctx.channel.name}"
                }.items():
                    content = content.replace(k, v)

                return await ctx.response.send_message(
                    content=content,
                    ephemeral=cmd.ephemeral
                )
        

    def add_command(self, ctx: discord.Interaction, name: str, content: str, description: str, ephemeral: bool) -> None:
        try:
            self.bot.tree.add_command(
                discord.app_commands.Command(
                    name=name,
                    description=description,
                    callback=self.custom_callback,
                    guild_ids=[ctx.guild_id]
                )
            )
        except Exception as ex:
            return ex
        else:
            data = {
                name: {
                    "content": content,
                    "author": ctx.user.id,
                    "ephemeral": ephemeral,
                    "description": description
                }
            }
            if not ctx.guild.id in self._commands:
                self._commands[ctx.guild.id] = data
            else:
                self._commands[ctx.guild.id].update(data)

            self.db.tags.insert(CustomCommand(ctx, name, content, ephemeral, description))
            return None


    def remove_command(self, guild: discord.Guild, name: str) -> None:
        try:
            self.bot.tree.remove_command(
                name,
                guild=guild
            )
        except Exception as ex:
            return ex
        else:
            self._commands[guild.id].pop(name)
            self.db.tags.delete(f"{guild.id}-{name}")
            return None


    def update_command(self, ctx: discord.Interaction, name: str, content: str, ephemeral: bool ) -> None:
        self._commands[ctx.guild.id][name].update({
            "content": content,
            "ephemeral": ephemeral
        })
        self.db.tags.multi_update(f"{ctx.guild.id}-{name}", {
            "content": content,
            "editor": f"{ctx.user.id}",
            "edited": datetime.datetime.now(),
            "ephemeral": ephemeral
        })


    async def cache_commands(self) -> None:
        _ = True
        while _:
            _ = False
            needs_sync = {}
            for e in self.db.tags.find({}):
                _id = int(e["id"].split("-")[0])
                if "name" in e:
                    data = {
                        e["name"]: {
                            "content": e["content"],
                            "author": int(e["author"]),
                            "ephemeral": e.get("ephemeral", False),
                            "description": e["description"]
                        }
                    }
                else: # migration bs
                    data = {
                        "-".join(e["id"].split("-")[1:]): {
                            "content": e["reply"],
                            "author": int(e["author"]),
                            "ephemeral": e.get("ephemeral", False),
                            "description": e["description"]
                        }
                    }
                
                if self.validate_name(list(data.keys())[0]):
                    if not _id in self._commands:
                        self._commands[_id] = data
                    else:
                        self._commands[_id].update(data)
                    
                    try:
                        self.bot.tree.add_command(
                            discord.app_commands.Command(
                                name=e["name"] if "name" in e else "-".join(e["id"].split("-")[1:]),
                                description=e["description"],
                                callback=self.custom_callback,
                                guild_ids=[int(e["id"].split("-")[0])]
                            )
                        )
                    except Exception:
                        pass
                    else:
                        g = self.bot.get_guild(int(e["id"].split("-")[0]))
                        if g != None:
                            if g.id not in needs_sync:
                                needs_sync.update({
                                    g.id: g
                                })

            for _, v in needs_sync.items():
                try: await self.bot.tree.sync(guild=v)
                except Exception: pass


    def update_uses(self, _id: str) -> None:
        self.bot.used_customs += 1
        self.bot.update_custom_stats()
        cur = self.db.tags.get(_id, "uses")
        if cur == None:
            self.db.tags.update(_id, "uses", 1)
        else:
            self.db.tags.update(_id, "uses", cur+1)


    def validate_name(self, name: str) -> bool:
        for c in name:
            if c == "-" or c == "_":
                pass
            else:
                if re.compile(r"^[a-zA-Z]+$").match(c) or c.isdigit():
                    pass
                else:
                    return False
        return True


    async def get_tags(self, guild: discord.Guild, raw: Dict[str, Any]) -> Dict[str, Any]:
        pre_cached = self._cached_from_api.get(guild.id, [])
        for e in raw:
            if e not in pre_cached:
                re_cache = await self.bot.tree.fetch_commands(guild=guild)
                self._cached_from_api.update({
                    guild.id: {x.name: x.id for x in re_cache}
                })
                return self._cached_from_api[guild.id]
        return self._cached_from_api[guild.id]

    
    _commands = discord.app_commands.Group(
        name="custom-commands",
        description="📝 Manage custom slash commands",
        default_permissions=discord.Permissions(manage_messages=True)
    )
    @_commands.command(
        name="list",
        description="📝 Shows a list of all custom commands"
    )
    async def custom_commands(self, ctx: discord.Interaction) -> None:
        """
        commands_show_help
        examples:
        -custom-commands list
        """
        cmd = f"</custom-commands add:{self.bot.internal_cmd_store.get('custom-commands')}>"
        if ctx.guild.id in self._commands:
            tags = await self.get_tags(ctx.guild, self._commands[ctx.guild.id])
            if len(tags) > 0:
                e = Embed(
                    ctx,
                    title="Custom Slash Commands",
                    description="{}".format(", ".join([f"</{name}:{cid}>" for name, cid in tags.items()]))
                )
                await ctx.response.send_message(embed=e)
            else:
                await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "no_tags", _emote="INFO", cmd=cmd), 2), ephemeral=True)
        else:
            await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "no_tags", _emote="INFO", cmd=cmd), 2), ephemeral=True)

    
    @_commands.command(
        name="add",
        description="✅ Creates a new custom slash command"
    )
    @discord.app_commands.default_permissions(manage_messages=True)
    async def addcom(self, ctx: discord.Interaction) -> None:
        """
        commands_add_help
        examples:
        -custom-commands add
        """
        async def callback(
            i: discord.Interaction
        ) -> None:
            name, content, description = self.bot.extract_args(i, "name", "content", "description")

            if len(name) > 30: return await i.response.send_message(embed=E(self.locale.t(i.guild, "name_too_long", _emote="NO"), 0), ephemeral=True)
            if len(content) > 1900: return await i.response.send_message(embed=E(self.locale.t(i.guild, "content_too_long", _emote="NO"), 0), ephemeral=True)
            if len(description) > 50: return await i.response.send_message(embed=E(self.locale.t(i.guild, "description_too_long", _emote="NO"), 0), ephemeral=True)

            if self.validate_name(name.lower()) == False:
                return await i.response.send_message(embed=E(self.locale.t(i.guild, "invalid_name", _emote="NO"), 0), ephemeral=True)

            if len(self._commands.get(i.guild_id, [])) > 40:
                return await i.response.send_message(embed=E(self.locale.t(i.guild, "max_commands", _emote="NO"), 0), ephemeral=True)

            name = name.lower()
            for p in [
                self.bot.get_plugin(x) for x in [
                    "ConfigPlugin",
                    "AutomodPlugin",
                    "ModerationPlugin",
                    "UtilityPlugin",
                    "TagsPlugin",
                    "CasesPlugin",
                    "ReactionRolesPlugin",
                    "FilterPlugin"
                ]
            ]:
                if p != None:
                    for cmd in p.__cog_app_commands__:
                        if cmd.qualified_name.lower() == name:
                            return await i.response.send_message(embed=E(self.locale.t(i.guild, "tag_has_cmd_name", _emote="NO"), 0), ephemeral=True)

            if i.guild.id in self._commands:
                if name in self._commands[i.guild.id]:
                    return await i.response.send_message(embed=E(self.locale.t(i.guild, "tag_alr_exists", _emote="NO"), 0), ephemeral=True)

            r = self.add_command(i, name, content, description, False)
            if r != None:
                await i.response.send_message(embed=E(self.locale.t(i.guild, "fail", _emote="NO", exc=r), 0), ephemeral=True)
            else:
                await self.bot.tree.sync(guild=i.guild)
                await i.response.send_message(embed=E(self.locale.t(i.guild, "tag_added", _emote="YES", tag=name), 1))

        modal = CommandCreateModal(self.bot, "Create Slash Command", callback)
        await ctx.response.send_modal(modal)
    

    @_commands.command(
        name="delete",
        description="❌ Deletes the given custom slash command"
    )
    @discord.app_commands.describe(
        name="Name of the custom command",
    )
    @discord.app_commands.default_permissions(manage_messages=True)
    async def delcom(self, ctx: discord.Interaction, name: str) -> None:
        """
        commands_delete_help
        examples:
        -custom-commands delete test_command
        """
        name = name.lower()
        if ctx.guild.id in self._commands:
            if not name in self._commands[ctx.guild.id]:
                await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "tag_doesnt_exists", _emote="NO"), 0), ephemeral=True)
            else:
                r = self.remove_command(ctx.guild, name)
                if r != None:
                    await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "fail", _emote="NO", exc=r), 0), ephemeral=True)
                else:
                    await self.bot.tree.sync(guild=ctx.guild)
                    await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "tag_removed", _emote="YES"), 1))
        else:
            await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "no_tags", _emote="INFO"), 2), ephemeral=True)


    @_commands.command(
        name="edit",
        description="🔀 Edits an existing custom slash command"
    )
    @discord.app_commands.describe(
        name="Name of the custom command you want to edit",
        ephemeral="Whether the command should respond with an ephemeral reply"
    )
    @discord.app_commands.default_permissions(manage_messages=True)
    async def editcom(self, ctx: discord.Interaction, name: str, ephemeral: Literal["True", "False"] = "False") -> None:
        """
        commands_edit_help
        examples:
        -custom-commands edit test_cmd
        """
        name = name.lower()
        
        cmd = f"</custom-commands add:{self.bot.internal_cmd_store.get('custom-commands')}>"
        if ctx.guild.id in self._commands:
            if not name in self._commands[ctx.guild.id]:
                await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "tag_doesnt_exists", _emote="NO"), 0), ephemeral=True)
            else:
                data = self._commands[ctx.guild.id][name]

                async def callback(i: discord.Interaction) -> None:
                    content, _ = self.bot.extract_args(i, "content", "vars")
                    if ephemeral == None:
                        _ephemeral = data.get("ephemeral", False)
                    else:
                        if ephemeral == "True":
                            _ephemeral = True
                        else:
                            _ephemeral = False
                    
                    self.update_command(i, name, content, _ephemeral)
                    await i.response.send_message(embed=E(self.locale.t(i.guild, "tag_updated", _emote="YES"), 1))
                
                modal = CommandEditModal(
                    self.bot, 
                    f"Edit Commanad {name}", 
                    data.get("content"),
                    callback
                )
                await ctx.response.send_modal(modal)
        else:
            await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "no_tags", _emote="INFO", cmd=cmd), 2), ephemeral=True)


    @_commands.command(
        name="info",
        description="📌 Shows some info about a custom slash command"
    )
    @discord.app_commands.describe(
        name="Name of the custom command",
    )
    @discord.app_commands.default_permissions(manage_messages=True)
    async def infocom(self, ctx: discord.Interaction, name: str) -> None:
        """
        commands_info_help
        examples:
        -commands info test_cmd
        """
        name = name.lower()
        cmd = f"</custom-commands add:{self.bot.internal_cmd_store.get('custom-commands')}>"
        if ctx.guild.id in self._commands:
            if not name in self._commands[ctx.guild.id]:
                await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "tag_doesnt_exists", _emote="NO"), 0), ephemeral=True)
            else:
                data = Object(self.db.tags.get_doc(f"{ctx.guild.id}-{name}"))
                y = self.bot.emotes.get("YES")
                n = self.bot.emotes.get("NO")

                e = Embed(
                    ctx,
                    title=f"/{name}"
                )
                e.add_fields([
                    {
                        "name": "__Content__",
                        "value": f"```\n{data.content}\n```",
                        "inline": False
                    },
                    {
                        "name": "__Description__",
                        "value": f"```\n{data.description}\n```",
                        "inline": False
                    },
                    {
                        "name": "__Ephemeral__",
                        "value": f"{y if data.ephemeral == True else n}",
                        "inline": True
                    },
                    e.blank_field(True, 6),
                    {
                        "name": "__Uses__",
                        "value": f"{data.uses}",
                        "inline": True
                    },
                    {
                        "name": "__Creator__",
                        "value": f"<@{data.author}> \n(<t:{round(data.created.timestamp())}>)",
                        "inline": True
                    }
                ])
                if data.edited != None:
                    e.add_fields([
                        e.blank_field(True),
                        {
                            "name": "__Editor__",
                            "value": f"<@{data.editor}> \n(<t:{round(data.edited.timestamp())}>)",
                            "inline": True
                        }
                    ])

                await ctx.response.send_message(embed=e)
        else:
            await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "no_tags", _emote="INFO", cmd=cmd), 2), ephemeral=True)


    # @_commands.command(
    #     name="disable",
    #     description="📌 Disables the given command"
    # )
    # @discord.app_commands.describe(
    #     name="Name of the custom command",
    # )
    # @discord.app_commands.default_permissions(manage_messages=True)
    # async def disablecom(self, ctx: discord.Interaction, name: str) -> None:
    #     """
    #     commands_disable_help
    #     examples:
    #     -commands disable test_cmd
    #     """
    #     name = name.lower()
    #     if ctx.guild.id in self._commands:
    #         if not name in self._commands[ctx.guild.id]:
    #             await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "tag_doesnt_exists", _emote="NO"), 0), ephemeral=True)
    #         else:
    #             self.disable_command(ctx, name)
    #             await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "disabled_tag", _emote="YES", cmd=name), 1))
    #     else:
    #         await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "no_tags", _emote="INFO", cmd=cmd), 2))


    # @_commands.command(
    #     name="enable",
    #     description="📌 Enables the given command"
    # )
    # @discord.app_commands.describe(
    #     name="Name of the custom command",
    # )
    # @discord.app_commands.default_permissions(manage_messages=True)
    # async def enablecom(self, ctx: discord.Interaction, name: str) -> None:
    #     """
    #     commands_disable_help
    #     examples:
    #     -commands enable test_cmd
    #     """
    #     name = name.lower()
    #     if ctx.guild.id in self._commands:
    #         if not name in self._commands[ctx.guild.id]:
    #             await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "tag_doesnt_exists", _emote="NO"), 0), ephemeral=True)
    #         else:
    #             self.disable_command(ctx, name)
    #             await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "disabled_tag", _emote="YES", cmd=name), 1))
    #     else:
    #         await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "no_tags", _emote="INFO", cmd=cmd), 2))


async def setup(bot: ShardedBotInstance) -> None: 
    await bot.register_plugin(TagsPlugin(bot))