import discord
from discord.ui import Button, View, Select

from . import BotUtils


class Confirm(Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.green, label="Confirm")
    
    async def callback(self, interaction):
        try:
            await self.view.confirm_callback(interaction)
        except discord.NotFound:
            pass
    


class Cancel(Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.red, label="Cancel")
    
    async def callback(self, interaction):
        await self.view.cancel_callback(interaction)   



class ConfirmView(View):
    def __init__(self, guild_id, on_confirm, on_cancel, on_timeout, check, timeout=30):
        super().__init__(timeout=timeout)
        self.add_item(Confirm())
        self.add_item(Cancel())

        self.guild_id = guild_id

        self.on_confirm = on_confirm
        self.on_cancel = on_cancel
        self.timeout_callback = on_timeout
        self.check = check

    async def on_timeout(self):
        await self.timeout_callback()
    
    async def confirm_callback(self, interaction):
        if await self.exec_check(interaction):
            await self.on_confirm(interaction)
            self.stop()

    async def cancel_callback(self, interaction):
        if await self.exec_check(interaction):
            await self.on_cancel(interaction)
            self.stop()

    async def exec_check(self, interaction):
        if not self.check:
            return True
        if self.check(interaction):
            return True
        await self.refuse(interaction)
        return False

    async def refuse(self, interaction):
        interaction.response.send_message("Invalid interactor", ephermal=True)



class Link(Button):
    def __init__(self, _url, _label, *args, **kwargs):
        super().__init__(*args, style=discord.ButtonStyle.link, url=_url, label=_label, **kwargs)



class LinkView(View):
    def __init__(self, _guild, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_item(Link(_url=f"https://localhost:3000/guilds/{_guild.id}", _label="View dashboard"))


class AboutView(View):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_item(Link(_url="https://discord.com/oauth2/authorize?client_id=697487580522086431&permissions=403041534&scope=bot+applications.commands", _label="Invite"))
        self.add_item(Link(_url="https://discord.gg/S9BEBux", _label="Support"))
        self.add_item(Link(_url="https://top.gg/bot/697487580522086431/vote", _label="Top.gg"))
        self.add_item(Link(_url="https://discords.com/bots/bot/697487580522086431/vote", _label="discords.com"))


class CallbackButton(Button):
    def __init__(self, label, callback, cid=None, disabled=False, emoji=None, style=discord.ButtonStyle.blurple):
        super().__init__(style=style, label=label, custom_id=cid, disabled=disabled, emoji=emoji)
        self._callback = callback

    async def callback(self, interaction: discord.Interaction):
        await self._callback(interaction)


class MultiPageView(View):
    def __init__(self, page, pages):
        super().__init__(timeout=None)
        self.id = ""

        self.add_item(CallbackButton(
            "First Page", self.first_page, "cases:first_page", disabled=page==0
        ))

        self.add_item(CallbackButton(
            "Previous Page", self.prev_page, "cases:prev_page", disabled=page==0
        ))
        self.add_item(CallbackButton(
            "Next Page", self.next_page, "cases:next_page", disabled=page>=pages-1
        ))

        self.add_item(CallbackButton(
            "Last Page", self.last_page, "cases:last_page", disabled=page>=pages-1
        ))

    @staticmethod
    async def first_page(i: discord.Interaction):
        embed, pages, page_count = await get_cases_from_cache(i, 100)
        await i.response.edit_message(
            embed=embed,
            view=MultiPageView(page=page_count, pages=pages)
        )

    @staticmethod
    async def prev_page(i: discord.Interaction):
        embed, pages, page_count = await get_cases_from_cache(i, -1)
        await i.response.edit_message(
            embed=embed,
            view=MultiPageView(page=page_count, pages=pages)
        )

    
    @staticmethod
    async def next_page(i: discord.Interaction):
        embed, pages, page_count = await get_cases_from_cache(i, 1)
        await i.response.edit_message(
            embed=embed,
            view=MultiPageView(page=page_count, pages=pages)
        )


    @staticmethod
    async def last_page(i: discord.Interaction):
        embed, pages, page_count = await get_cases_from_cache(i, -100)
        await i.response.edit_message(
            embed=embed,
            view=MultiPageView(page=page_count, pages=pages)
        )



async def get_cases_from_cache(i: discord.Interaction, diff):
    data = BotUtils._bot.case_cache.get(i.message.id, None)
    if data is None:
        return await i.response.send_message("No longer valid.")

    c = len(data["pages"])
    pages = data["pages"]
    page_n = data["page_number"] + diff

    if page_n >= c:
        page_n = 0
    elif page_n < 0:
        page_n = c - 1
    embed = pages[page_n]
    data["page_number"] = page_n
    BotUtils._bot.case_cache.update({
        i.message.id: data
    })
    return embed, c, page_n



def set_select(v: View, guild, bot, cur_plugin):
    actual_plugin_names = {
        "AutomodPlugin": "Automod",
        "BasicPlugin": "Basic",
        "ModerationPlugin": "Moderation",
        "WarnsPlugin": "Warning",
        "CasesPlugin": "Cases",
        "ConfigPlugin": "Configuration",
        "TagsPlugin": "Tags",
        "FiltersPlugin": "Filters",
        "StarboardPlugin": "Starboard"
    }
    plugins = [bot.get_cog(x) for x in bot.cogs if x in bot.config.enabled_plugins_with_commands]

    options = []
    options.append(discord.SelectOption(
        label="Select a category",
        value="None",
        default=cur_plugin == "None"
    ))
    for plugin in plugins:
        options.append(discord.SelectOption(
            label=actual_plugin_names[plugin.qualified_name],
            value=actual_plugin_names[plugin.qualified_name], 
            description=bot.i18next.t(guild, f"{plugin.qualified_name.lower()}_short_description"),
            default=cur_plugin.lower() == plugin.qualified_name.lower(),
            emoji=bot.emotes.get("HELP")
        ))

    v.add_item(Select(custom_id="help:select", options=options))



class HelpView(View):
    def __init__(self, guild, bot, plugin):
        super().__init__(timeout=None)
        set_select(self, guild, bot, plugin)
        self.stop()