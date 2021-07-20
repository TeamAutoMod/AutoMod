import discord
from discord.ext import commands

from ..PluginBlueprint import PluginBlueprint
from .CacheTags import cacheTags
from .commands import Tags, TagsAdd, TagsRemove, TagsInfo, TagsEdit
from .events import OnMessage



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
            await Tags.run(self, ctx)


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
        await TagsAdd.run(self, ctx, trigger, reply)


    @tags.command(aliases=["delete", "del"])
    @commands.has_permissions(manage_messages=True)
    async def remove(
        self,
        ctx,
        trigger: str
    ):
        """tags_remove_help"""
        await TagsRemove.run(self, ctx, trigger)


    @tags.command(aliases=["about"])
    @commands.has_permissions(manage_messages=True)
    async def info(
        self,
        ctx,
        tag: str
    ):
        """tags_info_help"""
        await TagsInfo.run(self, ctx, tag)


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
        await TagsEdit.run(self, ctx, tag, content)


    @commands.Cog.listener()
    async def on_message(
        self,
        message
    ):
        await OnMessage.run(self, message)




def setup(bot):
    pass