import discord
from discord.ext import commands

from toolbox import S as Object
import datetime
from typing import Literal
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
        self.cache_tags()


    def add_tag(
        self, 
        ctx: discord.Interaction, 
        name: str, 
        content: str,
        del_invoke: bool
    ) -> None:
        data = {
            name: {
                "content": content,
                "author": ctx.user.id,
                "del_invoke": del_invoke
            }
        }
        if not ctx.guild.id in self._tags:
            self._tags[ctx.guild.id] = data
        else:
            self._tags[ctx.guild.id].update(data)
        self.db.tags.insert(Tag(ctx, name, content, del_invoke))


    def remove_tag(
        self, 
        guild: discord.Guild, 
        name: str
    ) -> None:
        self._tags[guild.id].pop(name)
        self.db.tags.delete(f"{guild.id}-{name}")


    def update_tag(
        self, 
        ctx: discord.Interaction, 
        name: str, 
        content: str,
        del_invoke: bool
    ) -> None:
        self._tags[ctx.guild.id][name].update({
            "content": content,
            "del_invoke": del_invoke
        })
        self.db.tags.multi_update(f"{ctx.guild.id}-{name}", {
            "content": content,
            "editor": f"{ctx.user.id}",
            "edited": datetime.datetime.now(),
            "del_invoke": del_invoke
        })


    def cache_tags(
        self
    ) -> None:
        for e in self.db.tags.find({}):
            _id = int(e["id"].split("-")[0])
            if "name" in e:
                data = {
                    e["name"]: {
                        "content": e["content"],
                        "author": int(e["author"]),
                        "del_invoke": e.get("del_invoke", False)
                    }
                }
            else: # migration bs
                data = {
                    "-".join(e["id"].split("-")[1:]): {
                        "content": e["reply"],
                        "author": int(e["author"]),
                        "del_invoke": e.get("del_invoke", False)
                    }
                }
            if not _id in self._tags:
                self._tags[_id] = data
            else:
                self._tags[_id].update(data)


    def update_uses(
        self, 
        _id: str
    ) -> None:
        self.bot.used_tags += 1
        cur = self.db.tags.get(_id, "uses")
        self.db.tags.update(_id, "uses", cur+1)


    @discord.app_commands.command(
        name="commands",
        description="Shows a list of all custom commands"
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
                    title="Custom Commands",
                    description="> {}".format(", ".join([f"``{x}``" for x in tags]))
                )
                e.set_footer(text=f"Use these as commands (e.g. {prefix}{list(tags.keys())[0]})")
                await ctx.response.send_message(embed=e)
            else:
                await ctx.response.send_message(self.locale.t(ctx.guild, "no_tags", _emote="NO"))
        else:
            await ctx.response.send_message(self.locale.t(ctx.guild, "no_tags", _emote="NO"))

    
    @discord.app_commands.command(
        name="addcom",
        description="Creates a new custom command"
    )
    @discord.app_commands.describe(
        name="Name of the custom command",
        content="Content of the output",
        del_invoke="Whether to delete the invocation message"
    )
    @discord.app_commands.default_permissions(manage_messages=True)
    async def addcom(
        self, 
        ctx: discord.Interaction, 
        name: str,  
        content: str,
        del_invoke: Literal[
            "True"
        ] = None
    ) -> None:
        """
        addcom_help
        examples:
        -addcom test_cmd This is a test command
        -addcom test_cmd2 This is a test command del_invoke:True
        """
        if len(name) > 30:
            return await ctx.response.send_message(self.locale.t(ctx.guild, "name_too_long", _emote="NO"))
        if len(content) > 1900:
            return await ctx.response.send_message(self.locale.t(ctx.guild, "content_too_long", _emote="NO"))

        if del_invoke == None:
            del_invoke = False
        else:
            del_invoke = True

        name = name.lower()
        if ctx.guild.id in self._tags:
            if name in self._tags[ctx.guild.id]:
                return await ctx.response.send_message(self.locale.t(ctx.guild, "tag_alr_exists", _emote="NO"))

        self.add_tag(ctx, name, content, del_invoke)
        await ctx.response.send_message(self.locale.t(ctx.guild, "tag_added", _emote="YES", tag=name, prefix=self.get_prefix(ctx.guild)))


    @discord.app_commands.command(
        name="delcom",
        description="Deletes the given custom command"
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
                self.remove_tag(ctx.guild, name)
                await ctx.response.send_message(self.locale.t(ctx.guild, "tag_removed", _emote="YES"))
        else:
            await ctx.response.send_message(self.locale.t(ctx.guild, "no_tags", _emote="NO"))


    @discord.app_commands.command(
        name="editcom",
        description="Edits an existing custom command"
    )
    @discord.app_commands.describe(
        name="Name of the custom command",
        content="Content of the output",
        del_invoke="Whether to delete the invocation message"
    )
    @discord.app_commands.default_permissions(manage_messages=True)
    async def editcom(
        self, 
        ctx: discord.Interaction, 
        name: str, 
        content: str,
        del_invoke: Literal[
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
                if del_invoke == None:
                    del_invoke = self._tags[ctx.guild.id][name].get("del_invoke", False)
                else:
                    if del_invoke == "True":
                        del_invoke = True
                    else:
                        del_invoke = False
                
                self.update_tag(ctx, name, content, del_invoke)
                await ctx.response.send_message(self.locale.t(ctx.guild, "tag_updated", _emote="YES"))
        else:
            await ctx.response.send_message(self.locale.t(ctx.guild, "no_tags", _emote="NO"))


    @discord.app_commands.command(
        name="infocom",
        description="Shows some info about a custom command"
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
                        "name": "🗑 __**Delete Invoke**__",
                        "value": f"``▶`` {'yes' if data.del_invoke == True else 'no'}"
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



    @AutoModPluginBlueprint.listener()
    async def on_message(
        self, 
        msg: discord.Message
    ) -> None:
        if msg.guild == None \
            or msg.author.bot \
            or msg.author.id == self.bot.user.id: return
        if not msg.guild.id in self._tags: return
        if not msg.guild.chunked:
            await self.bot.chunk_guild(msg.guild)

        prefix = self.get_prefix(msg.guild)
        if msg.content.startswith(prefix, 0) and len(self._tags[msg.guild.id]) > 0:
            for name in self._tags[msg.guild.id]:
                if msg.content.lower() == prefix + name or (msg.content.lower().startswith(name, len(prefix)) and msg.content.lower()[len(prefix + name)] == " "):
                    tag = Object(self._tags[msg.guild.id][name])
                    self.update_uses(f"{msg.guild.id}-{name}")

                    if tag.del_invoke == True:
                        try:
                            await msg.delete()
                        except Exception:
                            pass

                    try:
                        await msg.channel.send(f"{tag.content}")
                    except Exception:
                        pass
                    finally:
                        self.bot.dispatch("custom_command_completion", msg, name)


async def setup(
    bot: ShardedBotInstance
) -> None: await bot.register_plugin(TagsPlugin(bot))