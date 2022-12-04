# type: ignore

import discord
from discord.ext import commands

import logging; log = logging.getLogger()
import itertools
from typing import List, Literal
import re
import io

from .. import AutoModPluginBlueprint, ShardedBotInstance
from ...types import Embed, E
from ...modals import FilterCreateModal, RegexCreateModal, FilterEditModal, RegexEditModal



class FilterPlugin(AutoModPluginBlueprint):
    """Plugin for all filter commands"""
    def __init__(
        self, 
        bot: ShardedBotInstance
    ) -> None:
        super().__init__(bot)

    
    def parse_channels(
        self,
        channels: str
    ) -> List[
        int
    ]:
        final = []
        for s in channels.split(", "):
            if s.isdigit():
                final.append(int(s))
        return final


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


    _filter = discord.app_commands.Group(
        name="filter",
        description="🔀 Configure word filters",
        default_permissions=discord.Permissions(manage_messages=True)
    )
    @_filter.command(
        name="list",
        description="⛔️ Shows all active word filters"
    )
    @discord.app_commands.default_permissions(manage_messages=True)
    async def show_filter(
        self, 
        ctx: discord.Interaction
    ) -> None:
        """
        filter_show_help
        examples:
        -filter list
        """
        filters = self.db.configs.get(ctx.guild.id, "filters")
        if len(filters) < 1: return await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "no_filters", _emote="NO"), 0))

        e = Embed(
            ctx,
            title="Filters"
        )
        for indx, name in enumerate(dict(itertools.islice(filters.items(), 10))):
            i = filters[name]
            action = str(i["warns"]) + " warn" if i["warns"] == 1 else str(i["warns"]) + " warns" if i["warns"] > 0 else "delete message"
            channels = "all channels" if len(i["channels"]) < 1 else ", ".join([f'#{ctx.guild.get_channel(int(x))}' for x in i["channels"]])

            e.add_field(
                name=f"**__{name}__**",
                value=f"**• Action:** {action} \n**• Channels:** {channels} \n**• Words:** \n```\n{', '.join([f'{x}' for x in i['words']])}\n```",
                inline=True
            )
            if indx % 2 == 0: e.add_fields([e.blank_field(True, 2)])

            footer = f"And {len(filters)-len(dict(itertools.islice(filters.items(), 10)))} more filters" if len(filters) > 10 else None
            if footer != None: e.set_footer(text=footer)

        await ctx.response.send_message(embed=e)
    

    @_filter.command(
        name="add",
        description="✅ Creates a new word filter"
    )
    @discord.app_commands.default_permissions(manage_messages=True)
    async def add_filter(
        self, 
        ctx: discord.Interaction
    ) -> None:
        """
        filter_add_help
        examples:
        -filter add
        """
        async def callback(
            i: discord.Interaction
        ) -> None:
            name, warns, words, channels = self.bot.extract_args(i, "name", "warns", "words", "channels")

            name = name.lower()
            filters = self.db.configs.get(i.guild.id, "filters")

            if len(name) > 30: return await i.response.send_message(embed=E(self.locale.t(i.guild, "filter_name_too_long", _emote="NO"), 0))
            if name in filters: return await i.response.send_message(embed=E(self.locale.t(i.guild, "filter_exists", _emote="NO"), 0))
            
            try: warns = int(warns)
            except Exception as ex: return await i.response.send_message(embed=E(self.locale.t(i.guild, "must_be_int", _emote="NO", arg="warns"), 0))

            if warns < 0: return await i.response.send_message(embed=E(self.locale.t(i.guild, "min_warns_esp", _emote="NO"), 0))
            if warns > 100: return await i.response.send_message(embed=E(self.locale.t(i.guild, "max_warns", _emote="NO"), 0))

            filters[name] = {
                "warns": warns,
                "words": words.split(", "),
                "channels": [] if channels == None else self.parse_channels(channels)
            }
            self.db.configs.update(i.guild.id, "filters", filters)
            await i.response.send_message(embed=E(self.locale.t(i.guild, "added_filter", _emote="YES"), 1))

        modal = FilterCreateModal(self.bot, "Create Filter", callback)
        await ctx.response.send_modal(modal)

    
    @_filter.command(
        name="remove",
        description="❌ Deletes an exisiting word filter"
    )
    @discord.app_commands.describe(
        name="Name of the filter",
    )
    @discord.app_commands.default_permissions(manage_messages=True)
    async def remove_filter(
        self, 
        ctx: discord.Interaction, 
        name: str
    ) -> None:
        """
        filter_remove_help
        examples:
        -filter remove test_filter
        """
        name = name.lower()
        filters = self.db.configs.get(ctx.guild.id, "filters")

        if len(filters) < 1: return await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "no_filters", _emote="NO"), 0))
        if not name in filters: return await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "no_filter", _emote="NO"), 0))

        del filters[name]
        self.db.configs.update(ctx.guild.id, "filters", filters)

        await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "removed_filter", _emote="YES"), 1))

    
    @_filter.command(
        name="edit",
        description="🔀 Edits an exisiting word filter"
    )
    @discord.app_commands.describe(
        name="Name of the filter",
    )
    @discord.app_commands.default_permissions(manage_messages=True)
    async def edit_filter(
        self, 
        ctx: discord.Interaction, 
        name: str, 
    ) -> None:
        """
        filter_edit_help
        examples:
        -filter edit test_filter
        """
        name = name.lower()
        filters = self.db.configs.get(ctx.guild.id, "filters")

        if len(name) > 30: return await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "filter_name_too_long", _emote="NO"), 0))
        if not name in filters: return await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "no_filter", _emote="NO"), 0))

        async def callback(
            i: discord.Interaction
        ) -> None:
            warns, words, channels = self.bot.extract_args(i, "warns", "words", "channels")

            try: warns = int(warns)
            except Exception as ex: return await i.response.send_message(embed=E(self.locale.t(i.guild, "must_be_int", _emote="NO", arg="warns"), 0))

            if warns < 0: return await i.response.send_message(embed=E(self.locale.t(i.guild, "min_warns_esp", _emote="NO"), 0))
            if warns > 100: return await i.response.send_message(embed=E(self.locale.t(i.guild, "max_warns", _emote="NO"), 0))

            filters[name] = {
                "warns": warns,
                "words": words.split(", "),
                "channels": [] if channels == None else self.parse_channels(channels)
            }
            self.db.configs.update(i.guild.id, "filters", filters)

            await i.response.send_message(embed=E(self.locale.t(i.guild, "edited_filter", _emote="YES"), 1))
        
        modal = FilterEditModal(
            self.bot, 
            f"Edit Filter {name}", 
            filters[name].get("warns"),
            ", ".join(filters[name].get("words")),
            ", ".join(filters[name].get("channels")),
            callback
        )
        await ctx.response.send_modal(modal)


    @_filter.command(
        name="export",
        description="📤 Exports all words from a filter to a text file for sharing"
    )
    @discord.app_commands.describe(
        name="Name of the filter",
        seperator="Whether to seperate each word by a comma or by a line split"
    )
    @discord.app_commands.default_permissions(manage_messages=True)
    async def export_filter(
        self, 
        ctx: discord.Interaction, 
        name: str,
        seperator: Literal[
            "Comma (,)",
            "Line Split"
        ] = "Comma (,)"
    ) -> None:
        """
        filter_export_help
        examples:
        -filter export test_filter
        """
        name = name.lower()
        filters = self.db.configs.get(ctx.guild.id, "filters")

        if not name in filters: 
            await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "no_filter", _emote="NO"), 0))
        else:
            await ctx.response.defer(thinking=True)

            if seperator.lower() != "line split":
                seperator = ", "
            else:
                seperator = "\n"

            istr = seperator.join(filters[name]["words"])
            fp = io.BytesIO(istr.encode("utf-8"))
            await ctx.followup.send(embed=E(self.locale.t(ctx.guild, "exported", _emote="YES"), 1), file=discord.File(fp, f"{name}-export.txt"))

    
    regex = discord.app_commands.Group(
        name="regex",
        description="🔀 Configure regex filters",
        default_permissions=discord.Permissions(manage_messages=True)
    )
    @regex.command(
        name="list",
        description="⛔️ Shows a list of active regex filters"
    )
    @discord.app_commands.default_permissions(manage_messages=True)
    async def show_regex(
        self, 
        ctx: discord.Interaction
    ) -> None:
        r"""
        regex_help
        examples:
        -regex list
        """
        regexes = self.db.configs.get(ctx.guild.id, "regexes")
        if len(regexes) < 1: return await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "no_regexes", _emote="NO"), 0))

        e = Embed(
            ctx,
            title="Regexes"
        )
        for indx, name in enumerate(dict(itertools.islice(regexes.items(), 10))):
            data = regexes[name]
            action = str(data["warns"]) + " warn" if data["warns"] == 1 else str(data["warns"]) + " warns" if data["warns"] > 0 else "delete message"
            channels = "all channels" if len(data["channels"]) < 1 else ", ".join([f"#{ctx.guild.get_channel(int(x))}" for x in data["channels"]])

            e.add_field(
                name=f"**__{name}__**",
                value=f"**• Action:** {action} \n**• Channels:** {channels} \n**• Pattern:** \n```\n{data['regex']}\n```",
                inline=True
            )
            if indx % 2 == 0: e.add_fields([e.blank_field(True, 2)])

            footer = f"And {len(regexes)-len(dict(itertools.islice(regexes.items(), 10)))} more filters" if len(regexes) > 10 else None
        if footer != None: e.set_footer(text=footer)
        
        await ctx.response.send_message(embed=e)


    @regex.command(
        name="add",
        description="✅ Adds a new regex filter with the given name, warns, pattern and channels"
    )
    async def add_regex(
        self, 
        ctx: discord.Interaction, 
    ) -> None:
        r"""
        regex_add_help
        examples:
        -regex add
        """
        async def callback(
            i: discord.Interaction
        ) -> None:
            name, warns, regex, channels = self.bot.extract_args(i, "name", "warns", "pattern", "channels")
            regexes = self.db.configs.get(i.guild.id, "regexes")
            name = name.lower()

            if len(name) > 30: return await i.response.send_message(embed=E(self.locale.t(i.guild, "regex_name_too_long", _emote="NO"), 0))
            if name in regexes: return await i.response.send_message(embed=E(self.locale.t(i.guild, "regex_exists", _emote="NO"), 0))

            try: warns = int(warns)
            except Exception as ex: return await i.response.send_message(embed=E(self.locale.t(i.guild, "must_be_int", _emote="NO", arg="warns"), 0))

            if warns < 0: return await i.response.send_message(embed=E(self.locale.t(i.guild, "min_warns_esp", _emote="NO"), 0))
            if warns > 100: return await i.response.send_message(embed=E(self.locale.t(i.guild, "max_warns", _emote="NO"), 0))

            if self.validate_regex(regex) == False: return await i.response.send_message(embed=E(self.locale.t(i.guild, "invalid_regex", _emote="NO"), 0))

            regexes[name] = {
                "warns": warns,
                "regex": regex,
                "channels": [] if channels == None else self.parse_channels(channels)
            }
            self.db.configs.update(i.guild.id, "regexes", regexes)

            await i.response.send_message(embed=E(self.locale.t(i.guild, "added_regex", _emote="YES"), 1))
        
        modal = RegexCreateModal(self.bot, "Create Regex Filter", callback)
        await ctx.response.send_modal(modal)


    @regex.command(
        name="remove",
        description="❌ Deletes an exisiting regex filter"
    )
    @discord.app_commands.describe(
        name="Name of the filter",
    )
    @discord.app_commands.default_permissions(manage_messages=True)
    async def remove_regex(
        self, 
        ctx: discord.Interaction, 
        name: str
    ) -> None:
        """
        regex_remove_help
        examples:
        -regex remove test_regex
        """
        regexes = self.db.configs.get(ctx.guild.id, "regexes")
        name = name.lower()

        if not name in regexes: return await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "regex_doesnt_exist", _emote="NO"), 0))

        del regexes[name]
        self.db.configs.update(ctx.guild.id, "regexes", regexes)

        await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "removed_regex", _emote="YES"), 1))


    @regex.command(
        name="edit",
        description="🔀 Edits an existing regex filter"
    )
    @discord.app_commands.describe(
        name="Name of the regex filter you want to edit",
    )
    @discord.app_commands.default_permissions(manage_messages=True)
    async def edit_regex(
        self, 
        ctx: discord.Interaction, 
        name: str
    ) -> None:
        r"""
        regex_edit_help
        examples:
        -regex edit test_regex
        """
        name = name.lower()
        regexes = self.db.configs.get(ctx.guild.id, "regexes")

        if len(name) > 30: return await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "regex_name_too_long", _emote="NO"), 0))
        if not name in regexes: return await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "regex_doesnt_exist", _emote="NO"), 0))

        async def callback(
            i: discord.Interaction
        ) -> None:
            warns, regex, channels = self.bot.extract_args(i, "warns", "pattern", "channels")

            try: warns = int(warns)
            except Exception as ex: return await i.response.send_message(embed=E(self.locale.t(i.guild, "must_be_int", _emote="NO", arg="warns"), 0))

            if warns < 0: return await i.response.send_message(embed=E(self.locale.t(i.guild, "min_warns_esp", _emote="NO"), 0))
            if warns > 100: return await i.response.send_message(embed=E(self.locale.t(i.guild, "max_warns", _emote="NO"), 0))

            if self.validate_regex(regex) == False: return await i.response.send_message(embed=E(self.locale.t(i.guild, "invalid_regex", _emote="NO"), 0))

            regexes[name] = {
                "warns": warns,
                "regex": regex,
                "channels": [] if channels == None else self.parse_channels(channels)
            }
            self.db.configs.update(i.guild.id, "regexes", regexes)

            await i.response.send_message(embed=E(self.locale.t(i.guild, "edited_regex", _emote="YES"), 1))

        modal = RegexEditModal(
            self.bot, 
            f"Edit Regex {name}", 
            regexes[name].get("warns"),
            regexes[name].get("regex"),
            ", ".join(regexes[name].get("channels")),
            callback
        )
        await ctx.response.send_modal(modal)


async def setup(
    bot: ShardedBotInstance
) -> None: await bot.register_plugin(FilterPlugin(bot))