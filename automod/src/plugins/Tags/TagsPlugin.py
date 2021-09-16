import discord
from discord.ext import commands

import datetime
import asyncio

from ..PluginBlueprint import PluginBlueprint
from ..Types import Embed
from .CacheTags import cacheTags



async def addTagToCache(plugin, ctx, trigger, reply):
    try:
        plugin.cached_tags[ctx.guild.id].append({"trigger": trigger, "reply": reply})
    except KeyError:
        plugin.cached_tags[ctx.guild.id] = [{"trigger": trigger, "reply": reply}]


async def editTag(plugin, ctx, tag, content):
    try:
        await removeTagFromCache(plugin, ctx, tag)
        await addTagToCache(plugin, ctx, tag, content)
    except Exception:
        pass
    finally:
        _id = f"{ctx.guild.id}-{tag}"
        plugin.db.tags.update(_id, "reply", f"{content}")
        plugin.db.tags.update(_id, "last_edited", datetime.datetime.utcnow())
        plugin.db.tags.update(_id, "edited_by", f"{ctx.message.author.id}")


def getTags(plugin, message):
    global tags
    tags = []
    try:
        tags = plugin.cached_tags[message.guild.id]
    except KeyError:
        _tags = [x for x in plugin.db.tags.find({}) if x["id"].split("-")[0] == str(message.guild.id)]
        tags = [{"trigger": "-".join(x["id"].split("-")[1:]), "reply": x["reply"]} for x in _tags]
    finally:
        return tags


async def removeTagFromCache(plugin, ctx, trigger):
    plugin.cached_tags[ctx.guild.id] = list(filter(lambda x: x["trigger"] != trigger, plugin.cached_tags[ctx.guild.id]))


class TagsPlugin(PluginBlueprint):
    def __init__(self, bot):
        super().__init__(bot)
        self.cached_tags = dict()
        self.bot.loop.create_task(cacheTags(self))

    
    @commands.group(aliases=["tag"])
    async def tags(
        self, 
        ctx
    ):
        """tags_help"""
        if ctx.subcommand_passed is None:
            tags = ["-".join(x["id"].split("-")[1:]) for x in self.db.tags.find({}) if x["id"].split("-")[0] == str(ctx.guild.id)]

            if len(tags) < 1:
                return await ctx.send(self.i18next.t(ctx.guild, "no_tags", _emote="NO"))

            prefix = self.bot.get_guild_prefix(ctx.guild)
            e = Embed()
            e.add_field(
                name="❯ Tags",
                value=" | ".join([f"``{prefix}{x}``" for x in tags])
            )
            await ctx.send(embed=e)


    @tags.command(aliases=["create"])
    @commands.has_permissions(manage_messages=True)
    async def add(
        self,
        ctx,
        trigger: str,
        *,
        reply: str
    ):
        """tags_add_help"""
        trigger = trigger.lower()
        if len(trigger) > 20:
            return await ctx.send(self.i18next.t(ctx.guild, "trigger_too_long", _emote="NO"))

        if len(reply) > 700:
            return await ctx.send(self.i18next.t(ctx.guild, "reply_too_long", _emote="NO"))
        
        _id = f"{ctx.guild.id}-{trigger}"
        if self.db.tags.exists(_id):
            return await ctx.send(self.i18next.t(ctx.guild, "tag_already_exists", _emote="WARN"))

        self.db.tags.insert(self.schemas.Tag(_id, reply, ctx.author, datetime.datetime.utcnow()))
        await addTagToCache(self, ctx, trigger, reply)

        prefix = self.bot.get_guild_prefix(ctx.guild)
        await ctx.send(self.i18next.t(ctx.guild, "tag_created", _emote="YES", prefix=prefix, tag=trigger))


    @tags.command(aliases=["delete", "del"])
    @commands.has_permissions(manage_messages=True)
    async def remove(
        self,
        ctx,
        trigger: str
    ):
        """tags_remove_help"""
        trigger = trigger.lower()

        tags = ["-".join(x["id"].split("-")[1:]) for x in self.db.tags.find({}) if x["id"].split("-")[0] == str(ctx.guild.id)]
        if len(tags) < 1:
            return await ctx.send(self.i18next.t(ctx.guild, "no_tags", _emote="NO"))

        _id = f"{ctx.guild.id}-{trigger}"
        if not self.db.tags.exists(_id):
            return await ctx.send(self.i18next.t(ctx.guild, "tag_doesnt_exist", _emote="NO"))

        self.db.tags.delete(_id)
        await removeTagFromCache(self, ctx, trigger)

        await ctx.send(self.i18next.t(ctx.guild, "tag_deleted", _emote="YES"))


    @tags.command(aliases=["about"])
    async def info(
        self,
        ctx,
        tag: str
    ):
        """tags_info_help"""
        tag = tag.lower()
        tags = ["-".join(x["id"].split("-")[1:]) for x in self.db.tags.find({}) if x["id"].split("-")[0] == str(ctx.guild.id)]
        if len(tags) < 1:
            return await ctx.send(self.i18next.t(ctx.guild, "no_tags", _emote="NO"))

        _id = f"{ctx.guild.id}-{tag}"
        if not self.db.tags.exists(_id):
            return await ctx.send(self.i18next.t(ctx.guild, "tag_doesnt_exist", _emote="NO"))

        entry = self.db.tags.get_doc(_id)
        e = Embed()
        e.add_field(
            name="❯ Name",
            value=f"``{tag}``"
        )

        user = await self.bot.utils.getUser(int(entry["author"]))
        e.add_field(
            name="❯ User",
            value=f"``{user if user is not None else 'Unknown#0000'}`` ({entry['author']})"
        )
        e.add_field(
            name="❯ Uses",
            value=f"{entry['uses']}"
        )
        e.add_field(
            name="❯ Created",
            value=f"<t:{round(entry['created'].timestamp())}>"
        )

        if entry["last_edited"] is not None:
            e.add_field(
                name="❯ Last edited",
                value=f"<t:{round(entry['last_edited'].timestamp())}>"
            )
            editor = await self.bot.utils.getUser(int(entry["edited_by"]))
            e.add_field(
                name="❯ Last edited by",
                value=f"``{editor if editor is not None else 'Unknown#0000'}`` ({entry['edited_by']})"
            )
        
        await ctx.send(embed=e)



    @tags.command()
    @commands.has_permissions(manage_messages=True)
    async def edit(
        self,
        ctx,
        tag: str,
        *,
        content: str
    ):
        """tags_edit_help"""
        tag = tag.lower()
        tags = ["-".join(x["id"].split("-")[1:]) for x in self.db.tags.find({}) if x["id"].split("-")[0] == str(ctx.guild.id)]
        if len(tags) < 1:
            return await ctx.send(self.i18next.t(ctx.guild, "no_tags", _emote="NO"))

        _id = f"{ctx.guild.id}-{tag}"
        if not self.db.tags.exists(_id):
            return await ctx.send(self.i18next.t(ctx.guild, "tag_doesnt_exist", _emote="NO"))

        if len(content) > 1500:
            return await ctx.send(self.i18next.t(ctx.guild, "tag_content_too_long", _emote="NO"))

        await editTag(self, ctx, tag, content)

        await ctx.send(self.i18next.t(ctx.guild, "tag_edited", _emote="YES", tag=tag))


    @commands.Cog.listener()
    async def on_message(
        self,
        message
    ):
        tags = getTags(self, message) 
        if len(tags) < 1:
            return
        if message.author.bot or message.webhook_id is not None or message.author.id == self.bot.user.id:
            return

        if message.guild is None or not isinstance(message.channel, discord.TextChannel):
            return

        role_id = self.db.configs.get(message.guild.id, "tag_role")
        if role_id != "":
            try:
                role = await self.bot.utils.getRole(message.guild, int(role_id))
            except Exception:
                pass
            else:
                if role is not None:
                    if role in message.author.roles:
                        return

        tags = getTags(self, message)
        prefix = self.bot.get_guild_prefix(message.guild)
        if prefix is None:
            return
        if message.content.startswith(prefix, 0) and len(tags) > 0:
            for tag in tags:
                trigger = tag["trigger"]
                if message.content.lower() == prefix + trigger or (message.content.lower().startswith(trigger, len(prefix)) and message.content.lower()[len(prefix + trigger)] == " "):
                    uses = self.db.tags.get(f"{message.guild.id}-{trigger}", "uses")
                    self.db.tags.update(f"{message.guild.id}-{trigger}", "uses", (uses+1))
                    reply = tag["reply"]
                    self.bot.used_tags += 1
                    try:
                        await message.reply(f"{reply}", mention_author=False)
                    except discord.NotFound:
                        # just in case
                        await message.channel.send(f"{reply}")
                    finally:
                        return




def setup(bot):
    pass