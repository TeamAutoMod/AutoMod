from http import client
import discord
from discord.ext import commands

from toolbox import S as Object
import datetime
from typing import Literal
import re
import logging; log = logging.getLogger()

from .. import AutoModPluginBlueprint, ShardedBotInstance
from ...schemas import Tag
from ...types import Embed



class TagsPlugin(AutoModPluginBlueprint):
    """Plugin for tags (custom commands)"""
    def __init__(
        self, 
        bot: ShardedBotInstance
    ) -> None:
        super().__init__(bot)
        self._tags = {}
        self.bot.loop.create_task(self.cache_tags())


    async def custom_callback(
        self,
        ctx: discord.Interaction
    ) -> None:
        if ctx.guild_id in self._tags:
            data = self._tags[ctx.guild_id].get(
                ctx.command.qualified_name.lower(),
                None
            )
            if data != None:
                cmd = Object(data)
                self.update_uses(f"{ctx.guild_id}-{ctx.command.qualified_name.lower()}")
                return await ctx.response.send_message(
                    cmd.content,
                    ephemeral=cmd.ephemeral
                )
        

    def add_tag(
        self, 
        ctx: discord.Interaction, 
        name: str, 
        content: str,
        description: str,
        ephemeral: bool
    ) -> None:
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
            if not ctx.guild.id in self._tags:
                self._tags[ctx.guild.id] = data
            else:
                self._tags[ctx.guild.id].update(data)

            self.db.tags.insert(Tag(ctx, name, content, ephemeral, description))
            return None


    def remove_tag(
        self, 
        guild: discord.Guild, 
        name: str
    ) -> None:
        try:
            self.bot.tree.remove_command(
                name,
                guild=guild
            )
        except Exception as ex:
            return ex
        else:
            self._tags[guild.id].pop(name)
            self.db.tags.delete(f"{guild.id}-{name}")
            return None


    def update_tag(
        self, 
        ctx: discord.Interaction, 
        name: str, 
        content: str,
        ephemeral: bool
    ) -> None:
        self._tags[ctx.guild.id][name].update({
            "content": content,
            "ephemeral": ephemeral
        })
        self.db.tags.multi_update(f"{ctx.guild.id}-{name}", {
            "content": content,
            "editor": f"{ctx.user.id}",
            "edited": datetime.datetime.now(),
            "ephemeral": ephemeral
        })


    async def cache_tags(
        self
    ) -> None:
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
                    if not _id in self._tags:
                        self._tags[_id] = data
                    else:
                        self._tags[_id].update(data)
                    
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


    def update_uses(
        self, 
        _id: str
    ) -> None:
        self.bot.used_tags += 1
        cur = self.db.tags.get(_id, "uses")
        if cur == None:
            self.db.tags.update(_id, "uses", 1)
        else:
            self.db.tags.update(_id, "uses", cur+1)


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


    @discord.app_commands.command(
        name="commands",
        description="📝 Shows a list of all custom commands"
    )
    async def custom_commands(
        self, 
        ctx: discord.Interaction
    ) -> None:
        """
        commands_help
        examples:
        -commands
        """
        if ctx.guild.id in self._tags:
            tags = self._tags[ctx.guild.id]
            prefix = self.get_prefix(ctx.guild)
            if len(tags) > 0:
                e = Embed(
                    ctx,
                    title="Custom Slash Commands",
                    description="> {}".format(", ".join([f"``/{x}``" for x in tags]))
                )
                await ctx.response.send_message(embed=e)
            else:
                await ctx.response.send_message(self.locale.t(ctx.guild, "no_tags", _emote="NO"))
        else:
            await ctx.response.send_message(self.locale.t(ctx.guild, "no_tags", _emote="NO"))

    
    @discord.app_commands.command(
        name="addcom",
        description="✅ Creates a new custom slash command"
    )
    @discord.app_commands.describe(
        name="Name of the custom command",
        content="Content of the output",
        description="The command description that should be displayed",
        ephemeral="Whether the response should be ephemeral, meaning only the user can see it"
    )
    @discord.app_commands.default_permissions(manage_messages=True)
    async def addcom(
        self, 
        ctx: discord.Interaction, 
        name: str,  
        content: str,
        description: str,
        ephemeral: Literal[
            "True"
        ] = None
    ) -> None:
        """
        addcom_help
        examples:
        -addcom test_cmd This is a test command description:A cool test command
        -addcom test_cmd2 This is a test command description:A cool test command ephemeral:True
        """
        if len(name) > 30:
            return await ctx.response.send_message(self.locale.t(ctx.guild, "name_too_long", _emote="NO"))
        if len(content) > 1900:
            return await ctx.response.send_message(self.locale.t(ctx.guild, "content_too_long", _emote="NO"))
        if len(description) > 50:
            return await ctx.response.send_message(self.locale.t(ctx.guild, "description_too_long", _emote="NO"))

        if self.validate_name(name.lower()) == False:
            return await ctx.response.send_message(self.locale.t(ctx.guild, "invalid_name", _emote="NO"))

        if len(self._tags.get(ctx.guild_id, [])) > 40:
            return await ctx.response.send_message(self.locale.t(ctx.guild, "max_commands", _emote="NO"))

        if ephemeral == None:
            ephemeral = False
        else:
            ephemeral = True

        name = name.lower()
        for p in [
            self.bot.get_plugin(x) for x in [
                "ConfigPlugin",
                "AutoModPluginBlueprint",
                "ModerationPlugin",
                "UtilityPlugin",
                "TagsPlugin",
                "CasesPlugin",
                "ReactionRolesPlugin",
            ]
        ]:
            if p != None:
                for cmd in p.__cog_app_commands__:
                    if cmd.qualified_name.lower() == name:
                        return await ctx.response.send_message(self.locale.t(ctx.guild, "tag_has_cmd_name", _emote="NO"))

        if ctx.guild.id in self._tags:
            if name in self._tags[ctx.guild.id]:
                return await ctx.response.send_message(self.locale.t(ctx.guild, "tag_alr_exists", _emote="NO"))

        r = self.add_tag(ctx, name, content, description, ephemeral)
        if r != None:
            await ctx.response.send_message(self.locale.t(ctx.guild, "fail", _emote="NO", exc=r))
        else:
            await self.bot.tree.sync(guild=ctx.guild)
            await ctx.response.send_message(self.locale.t(ctx.guild, "tag_added", _emote="YES", tag=name))


    @discord.app_commands.command(
        name="delcom",
        description="❌ Deletes the given custom slash command"
    )
    @discord.app_commands.describe(
        name="Name of the custom command",
    )
    @discord.app_commands.default_permissions(manage_messages=True)
    async def delcom(
        self, 
        ctx: discord.Interaction, 
        name: str
    ) -> None:
        """
        delcom_help
        examples:
        -delcom test_command
        """
        name = name.lower()
        if ctx.guild.id in self._tags:
            if not name in self._tags[ctx.guild.id]:
                await ctx.response.send_message(self.locale.t(ctx.guild, "tag_doesnt_exists", _emote="NO"))
            else:
                r = self.remove_tag(ctx.guild, name)
                if r != None:
                    await ctx.response.send_message(self.locale.t(ctx.guild, "fail", _emote="NO", exc=r))
                else:
                    await self.bot.tree.sync(guild=ctx.guild)
                    await ctx.response.send_message(self.locale.t(ctx.guild, "tag_removed", _emote="YES"))
        else:
            await ctx.response.send_message(self.locale.t(ctx.guild, "no_tags", _emote="NO"))


    @discord.app_commands.command(
        name="editcom",
        description="🔀 Edits an existing custom slash command"
    )
    @discord.app_commands.describe(
        name="Name of the custom command",
        content="Content of the output",
        ephemeral="Whether the response should be ephemeral, meaning only the user can see it"
    )
    @discord.app_commands.default_permissions(manage_messages=True)
    async def editcom(
        self, 
        ctx: discord.Interaction, 
        name: str, 
        content: str,
        ephemeral: Literal[
            "True",
            "False"
        ] = None
    ) -> None:
        """
        editcom_help
        examples:
        -editcom test_cmd This is the new content
        """
        if len(content) > 1900:
            return await ctx.response.send_message(self.locale.t(ctx.guild, "content_too_long", _emote="NO"))

        name = name.lower()
        if ctx.guild.id in self._tags:
            if not name in self._tags[ctx.guild.id]:
                await ctx.response.send_message(self.locale.t(ctx.guild, "tag_doesnt_exists", _emote="NO"))
            else:
                if ephemeral == None:
                    ephemeral = self._tags[ctx.guild.id][name].get("ephemeral", False)
                else:
                    if ephemeral == "True":
                        ephemeral = True
                    else:
                        ephemeral = False
                
                self.update_tag(ctx, name, content, ephemeral)
                await ctx.response.send_message(self.locale.t(ctx.guild, "tag_updated", _emote="YES"))
        else:
            await ctx.response.send_message(self.locale.t(ctx.guild, "no_tags", _emote="NO"))


    @discord.app_commands.command(
        name="infocom",
        description="📌 Shows some info about a custom slash command"
    )
    @discord.app_commands.describe(
        name="Name of the custom command",
    )
    @discord.app_commands.default_permissions(manage_messages=True)
    async def infocom(
        self, 
        ctx: discord.Interaction, 
        name: str
    ) -> None:
        """
        infocom_help
        examples:
        -infocom test_cmd
        """
        name = name.lower()
        if ctx.guild.id in self._tags:
            if not name in self._tags[ctx.guild.id]:
                await ctx.response.send_message(self.locale.t(ctx.guild, "tag_doesnt_exists", _emote="NO"))
            else:
                data = Object(self.db.tags.get_doc(f"{ctx.guild.id}-{name}"))

                e = Embed(
                ctx,
                    title="Command Info"
                )
                e.add_fields([
                    {
                        "name": "📝 __**Name**__",
                        "value": f"``▶`` {name}"
                    },
                    {
                        "name": "💬 __**Content**__",
                        "value": f"```\n{data.content}\n```"
                    },
                    {
                        "name": "📌 __**Description**__",
                        "value": f"```\n{data.description}\n```"
                    },
                    {
                        "name": "👻 __**ephemeral**__",
                        "value": f"``▶`` {'yes' if data.ephemeral == True else 'no'}"
                    },
                    {
                        "name": "📈 __**Uses**__",
                        "value": f"``▶`` {data.uses}"
                    },
                    
                    {
                        "name": "👤 __**Creator**__",
                        "value": f"``▶`` <@{data.author}> (<t:{round(data.created.timestamp())}>)"
                    }
                ])
                if data.edited != None:
                    e.add_field(
                        name="✏️ __**Editor**__",
                        value=f"``▶`` <@{data.editor}> (<t:{round(data.edited.timestamp())}>)"
                    )

                await ctx.response.send_message(embed=e)
        else:
            await ctx.response.send_message(self.locale.t(ctx.guild, "no_tags", _emote="NO"))


async def setup(
    bot: ShardedBotInstance
) -> None: await bot.register_plugin(TagsPlugin(bot))