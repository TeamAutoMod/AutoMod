import discord
from discord.ext import commands

from toolbox import S as Object
import logging; log = logging.getLogger()

from . import AutoModPlugin
from ..schemas import Tag
from ..types import Embed



class TagsPlugin(AutoModPlugin):
    """Plugin for tags (custom commands)"""
    def __init__(self, bot):
        super().__init__(bot)
        self._tags = {}
        self.cache_tags()


    def add_tag(self, ctx, name, content):
        data = {
            name: {
                "content": content,
                "author": ctx.author.id
            }
        }
        if not ctx.guild.id in self._tags:
            self._tags[ctx.guild.id] = data
        else:
            self._tags[ctx.guild.id].update(data)
        self.db.tags.insert(Tag(ctx, name, content))


    def remove_tag(self, guild, name):
        self._tags[guild.id].pop(name)
        self.db.tags.delete(f"{guild.id}-{name}")


    def cache_tags(self):
        for e in self.db.tags.find({}):
            _id = int(e["id"].split("-")[0])
            if "name" in e:
                data = {
                    e["name"]: {
                        "content": e["content"],
                        "author": int(e["author"])
                    }
                }
                if not _id in self._tags:
                    self._tags[_id] = data
                else:
                    self._tags[_id].update(data)


    def update_uses(self, _id):
        cur = self.db.tags.get(_id, "uses")
        self.db.tags.update(_id, "uses", cur+1)


    @commands.group()
    async def tags(self, ctx):
        """tags_help"""
        if ctx.invoked_subcommand is None:
            if ctx.guild.id in self._tags:
                tags = self._tags[ctx.guild.id]
                prefix = self.get_prefix(ctx.guild)
                if len(tags) > 0:
                    await ctx.send("**Available tags in {}** \n```\n{}\n```".format(
                        ctx.guild.name,
                        "\n".join(
                            [f"{prefix}{x}" for x in tags]
                        )
                    ))
                else:
                    await ctx.send(self.locale.t(ctx.guild, "no_tags", _emote="NO"))
            else:
                await ctx.send(self.locale.t(ctx.guild, "no_tags", _emote="NO"))

    
    @tags.command(aliases=["create", "new"])
    async def add(self, ctx, name: str, *, content: str):
        """tags_add_help"""
        if len(name) > 30:
            return await ctx.send(self.locale.t(ctx.guild, "name_too_long", _emote="NO"))
        if len(content) > 1900:
            return await ctx.send(self.locale.t(ctx.guild, "content_too_long", _emote="NO"))

        name = name.lower()
        if ctx.guild.id in self._tags:
            if name in self._tags[ctx.guild.id]:
                return await ctx.send(self.locale.t(ctx.guild, "tag_alr_exists", _emote="NO"))

        self.add_tag(ctx, name, content)
        await ctx.send(self.locale.t(ctx.guild, "tag_added", _emote="YES", tag=name, prefix=self.get_prefix(ctx.guild)))


    @tags.command(aliases=["delete", "del"])
    async def remove(self, ctx, name: str):
        """tags_remove_help"""
        name = name.lower()
        if ctx.guild.id in self._tags:
            if not name in self._tags[ctx.guild.id]:
                await ctx.send(self.locale.t(ctx.guild, "tag_doesnt_exists", _emote="NO"))
            else:
                self.remove_tag(ctx.guild, name)
                await ctx.send(self.locale.t(ctx.guild, "tag_removed", _emote="YES"))
        else:
            await ctx.send(self.locale.t(ctx.guild, "no_tags", _emote="NO"))



    @AutoModPlugin.listener()
    async def on_message(self, msg: discord.Message):
        if msg.guild == None \
            or msg.author.bot \
            or msg.webhook_id != None \
            or msg.author.id == self.bot.user.id: return
        if not msg.guild.id in self._tags: return
        if not msg.guild.chunked:
            await msg.guild.chunk(cache=True)

        prefix = self.get_prefix(msg.guild)
        if msg.content.startswith(prefix, 0) and len(self._tags[msg.guild.id]) > 0:
            for name in self._tags[msg.guild.id]:
                if msg.content.lower() == prefix + name or (msg.content.lower().startswith(name, len(prefix)) and msg.content.lower()[len(prefix + name)] == " "):
                    tag = Object(self._tags[msg.guild.id][name])
                    self.update_uses(f"{msg.guild.id}-{name}")

                    resp = Embed(
                        color=0x202225,
                        description=tag.content
                    )
                    
                    author = msg.guild.get_member(tag.author)
                    if author != None:
                        resp.set_footer(
                            text="Created by {0.name}#{0.discriminator} ({0.id})".format(author),
                            icon_url=author.display_avatar
                        )

                    await msg.channel.send(embed=resp)


def setup(bot): bot.register_plugin(TagsPlugin(bot))