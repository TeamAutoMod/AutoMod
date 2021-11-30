import discord
from discord.ext import commands

import itertools
import re

from .PluginBlueprint import PluginBlueprint
from .Types import Embed
from .Automod.sub.ShouldPerformAutomod import shouldPerformAutomod



def parseFilter(_filter):
    normal = list()
    wildcards = list()

    for i in _filter:
        i = i.replace("*", "", (i.count("*") - 1)) # remove multiple wildcards
        if i.endswith("*"):
            wildcards.append(i.replace("*", ".+"))
        else:
            normal.append(i)
    
    return re.compile(r"|".join([*normal, *wildcards]))


class FiltersPlugin(PluginBlueprint):
    def __init__(self, bot):
        super().__init__(bot)


    async def cog_check(self, ctx):
        return ctx.author.guild_permissions.ban_members


    @commands.Cog.listener()
    async def on_filter_event(
        self,
        message
    ):
        if not shouldPerformAutomod(self, message):
            return

        filters = self.db.configs.get(message.guild.id, "filters")
        if len(filters) < 1:
            return

        content = message.content.replace("\\", "")
        for name in filters:
            f = filters[name]
            parsed = parseFilter(f["words"])
            found = parsed.findall(content)
            if found:
                self.bot.ignore_for_event.add("messages", message.id)
                try:
                    await message.delete()
                except discord.NotFound:
                    pass

                await self.action_validator.add_warns(
                    message, 
                    message.author,
                    int(f["warns"]),
                    moderator=self.bot.user,
                    moderator_id=self.bot.user.id,
                    user=message.author,
                    user_id=message.author.id,
                    reason=f"Triggered filter '{name}' with '{', '.join(found)}'"
                )


    @commands.group(name="filter")
    async def _filter(
        self, 
        ctx
    ):
        """filter_help"""
        if ctx.subcommand_passed is None:
            prefix = self.db.configs.get(ctx.guild.id, "prefix")
            e = Embed(
                title="How to use filters",
                description=f"• Adding a filter: ``{prefix}filter add <name> <warns> <words>`` \n• Deleting a filter: ``{prefix}filter remove <name>``"
            )
            e.add_field(
                name="❯ Arguments",
                value="``<name>`` - *Name of the filter* \n``<warns>`` - *Warns users get when using a word within the filter* \n``<words>`` - *Words contained in the filter, seperated by commas*"
            )
            e.add_field(
                name="❯ Wildcards",
                value="You can also use an astrix (``*``) as a wildcard. E.g. \nIf you set one of the words to be ``tes*``, then things like ``test`` or ``testtt`` would all be filtered."
            )
            e.add_field(
                name="❯ Example",
                value=f"``{prefix}filter add test_filter 1 oneword, two words, wildcar*``"
            )
            await ctx.send(embed=e)


    @_filter.command()
    async def add(
        self,
        ctx,
        name,
        warns: int,
        *,
        words
    ):
        """filter_add_help"""
        name = name.lower()
        filters = self.db.configs.get(ctx.guild.id, "filters")

        if len(name) > 30:
            return await ctx.send(self.i18next.t(ctx.guild, "name_too_long", _emote="NO"))

        if name in filters:
            return await ctx.send(self.i18next.t(ctx.guild, "filter_exists", _emote="WARN"))
        
        if warns < 1:
            return await ctx.send(self.i18next.t(ctx.guild, "min_warns", _emote="NO"))

        if warns > 100:
            return await ctx.send(self.i18next.t(ctx.guild, "max_warns", _emote="NO"))

        new_filter = {
            "warns": warns,
            "words": words.split(", ")
        }
        filters[name] = new_filter
        self.db.configs.update(ctx.guild.id, "filters", filters)

        await ctx.send(self.i18next.t(ctx.guild, "filter_added", _emote="YES", name=name))


    @_filter.command()
    async def remove(
        self,
        ctx,
        name
    ):
        """filter_remove_help"""
        name = name.lower()
        filters = self.db.configs.get(ctx.guild.id, "filters")

        if len(filters) < 1:
            return await ctx.send(self.i18next.t(ctx.guild, "no_filters", _emote="NO"))

        if name not in filters:
            return await ctx.send(self.i18next.t(ctx.guild, "filter_doesnt_exist", _emote="NO"))
        
        del filters[name]
        self.db.configs.update(ctx.guild.id, "filters", filters)

        await ctx.send(self.i18next.t(ctx.guild, "filter_removed", _emote="YES", name=name))


    @_filter.command(aliases=["list"])
    async def show(
        self,
        ctx
    ):
        """filter_show_help"""
        filters = self.db.configs.get(ctx.guild.id, "filters")

        if len(filters) < 1:
            return await ctx.send(self.i18next.t(ctx.guild, "no_filters", _emote="NO"))

        e = Embed()
        footer = f"And {len(filters)-len(dict(itertools.islice(filters.items(), 10)))} more filters" if len(filters) > 10 else None
        for name in dict(itertools.islice(filters.items(), 10)):
            i = filters[name]
            e.add_field(name=f"❯ {name} ({i['warns']} {'warn' if int(i['warns']) == 1 else 'warns'})", value="```fix\n{}\n```".format("\n".join([x for x in i["words"]])))

        if footer is not None:
            e.set_footer(text=footer)
        
        await ctx.send(embed=e)




def setup(bot): bot.add_cog(FiltersPlugin(bot))