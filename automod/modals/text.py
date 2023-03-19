# type: ignore

import discord
from discord.ui import Modal

from typing import Callable, Optional



class TextModalBase(Modal):
    def __init__(self, bot, title: str, callback: Callable, *args, **kwargs) -> None:
        super().__init__(*args, title=title, **kwargs)
        self.bot = bot
        self.callback = callback


    async def on_submit(self, i: discord.Interaction) -> None:
        await self.callback(i)

    
    async def on_error(self, i: discord.Interaction, exc: Exception) -> None:
        await i.response.send_message(self.bot.locale.t(i.guild, "fail", _emote="NO", exc=exc))


class FilterCreateModal(TextModalBase):
    def __init__(self, bot, title: str, callback: Callable) -> None:
        super().__init__(bot, title, callback)
    

    name = discord.ui.TextInput(
        custom_id="name",
        label="Name",
        style=discord.TextStyle.short,
        placeholder="Name of the filter",
        required=True,
        max_length=20
    )


    warns = discord.ui.TextInput(
        custom_id="warns",
        label="Warns",
        style=discord.TextStyle.long,
        placeholder="Warns given upon violation. Use 0 to just have the message deleted",
        required=True,
        max_length=3
    )


    words = discord.ui.TextInput(
        custom_id="words",
        label="Words",
        style=discord.TextStyle.long,
        placeholder="Words and phrases for this filter, seperated by commas",
        required=True,
        max_length=2000
    )


    channels = discord.ui.TextInput(
        custom_id="channels",
        label="Channels",
        style=discord.TextStyle.long,
        placeholder="IDs of channels this filter should be active in. Leave blank for server-wide enforcement",
        required=False,
        max_length=3000
    )


class RegexCreateModal(TextModalBase):
    def __init__(self, bot, title: str, callback: Callable) -> None:
        super().__init__(bot, title, callback)
    

    name = discord.ui.TextInput(
        custom_id="name",
        label="Name",
        style=discord.TextStyle.short,
        placeholder="Name of the filter",
        required=True,
        max_length=20
    )


    warns = discord.ui.TextInput(
        custom_id="warns",
        label="Warns",
        style=discord.TextStyle.long,
        placeholder="Warns given upon violation. Use 0 to just have the message deleted",
        required=True,
        max_length=3
    )


    pattern = discord.ui.TextInput(
        custom_id="pattern",
        label="Regex Pattern",
        style=discord.TextStyle.long,
        placeholder="The regex pattern for this filter",
        required=True,
        max_length=500
    )


    channels = discord.ui.TextInput(
        custom_id="channels",
        label="Channels",
        style=discord.TextStyle.long,
        placeholder="IDs of channels this filter should be active in. Leave blank for server-wide enforcement",
        required=False,
        max_length=3000
    )


class FilterEditModal(TextModalBase):
    def __init__(self, bot, title: str, warns: int, words: str, channels: str, callback: Callable) -> None:
        super().__init__(bot, title, callback)
        self.warns = warns
        self.words = words
        self.channels = channels
        self.add_items()


    def add_items(self) -> None:
        self.add_item(discord.ui.TextInput(
            custom_id="warns",
            default=str(self.warns),
            label="Warns",
            style=discord.TextStyle.long,
            placeholder="Warns given upon violation. Use 0 to just have the message deleted",
            required=True,
            max_length=3
        ))

        self.add_item(discord.ui.TextInput(
            custom_id="words",
            default=self.words,
            label="Words",
            style=discord.TextStyle.long,
            placeholder="Words and phrases for this filter, seperated by commas",
            required=True,
            max_length=2000
        ))

        self.add_item(discord.ui.TextInput(
            custom_id="channels",
            default=self.channels,
            label="Channels",
            style=discord.TextStyle.long,
            placeholder="IDs of channels this filter should be active in. Leave blank for server-wide enforcement",
            required=False,
            max_length=3000
        ))


class RegexEditModal(TextModalBase):
    def __init__(self, bot, title: str, warns: int, pattern: str, channels: str, callback: Callable) -> None:
        super().__init__(bot, title, callback)
        self.warns = warns
        self.pattern = pattern
        self.channels = channels
        self.add_items()


    def add_items(self) -> None:
        self.add_item(discord.ui.TextInput(
            custom_id="warns",
            default=str(self.warns),
            label="Warns",
            style=discord.TextStyle.long,
            placeholder="Warns given upon violation. Use 0 to just have the message deleted",
            required=True,
            max_length=2
        ))

        self.add_item(discord.ui.TextInput(
            custom_id="pattern",
            default=self.pattern,
            label="Regex Pattern",
            style=discord.TextStyle.long,
            placeholder="The regex pattern for this filter",
            required=True,
            max_length=500
        ))

        self.add_item(discord.ui.TextInput(
            custom_id="channels",
            default=self.channels,
            label="Channels",
            style=discord.TextStyle.long,
            placeholder="IDs of channels this filter should be active in. Leave blank for server-wide enforcement",
            required=False,
            max_length=3000
        ))


class CommandCreateModal(TextModalBase):
    def __init__(self, bot, title: str, callback: Callable) -> None:
        super().__init__(bot, title, callback)
        self._vars_text = "{user}  ━ The mention of the user, e.g. @paul \n{username}  ━ The name of the user, e.g. paul \n{avatar}  ━ The avatar URL of the user\n{channel}  ━ The channel name \n{server}  ━ The server name"

        self.add_item(discord.ui.TextInput(
            custom_id="name",
            label="Name",
            style=discord.TextStyle.short,
            placeholder="Name of the command",
            required=True,
            max_length=20
        ))
        self.add_item(discord.ui.TextInput(
            custom_id="content",
            label="Reply",
            style=discord.TextStyle.long,
            placeholder="What the bot should reply with",
            required=True,
            max_length=2000
        ))
        self.add_item(discord.ui.TextInput(
            custom_id="description",
            label="Description",
            style=discord.TextStyle.long,
            placeholder="Command description displayed in the chat input",
            required=True,
            max_length=75
        ))
        self.add_item(discord.ui.TextInput(
            custom_id="vars",
            label="Variable Reference",
            style=discord.TextStyle.long,
            placeholder="Putting something here won't have any effects. This field is just to show the available variables",
            default=self._vars_text,
            required=False,
            max_length=len(self._vars_text)
        ))


class CommandEditModal(TextModalBase):
    def __init__(self, bot, title: str, content: str, callback: Callable) -> None:
        super().__init__(bot, title, callback)
        self._vars_text = "{user}  ━ The mention of the user, e.g. @paul \n{username}  ━ The name of the user, e.g. paul \n{avatar}  ━ The avatar URL of the user\n{channel}  ━ The channel name \n{server}  ━ The server name"

        self.add_item(discord.ui.TextInput(
            custom_id="content",
            label="Reply",
            style=discord.TextStyle.long,
            placeholder="What the bot should reply with",
            default=content,
            required=True,
            max_length=2000
        ))
        self.add_item(discord.ui.TextInput(
            custom_id="vars",
            label="Variable Reference",
            style=discord.TextStyle.long,
            placeholder="Putting something here won't have any effects. This field is just to show the available variables",
            default=self._vars_text,
            required=False,
            max_length=len(self._vars_text)
        ))


class AutomodRuleModal(TextModalBase):
    def __init__(self, bot, title: str, _type: str, amount: str, response: Optional[str], reason: Optional[str], callback: Callable) -> None:
        super().__init__(bot, title, callback)
        self._vars_text = "{user}  ━ The mention of the user, e.g. @paul \n{username}  ━ The name of the user, e.g. paul \n{avatar}  ━ The avatar URL of the user\n{channel}  ━ The channel name \n{server}  ━ The server name"

        self.add_item(discord.ui.TextInput(
            custom_id="amount",
            label=_type.capitalize(),
            style=discord.TextStyle.short,
            default=amount if amount == None else str(amount),
            placeholder="Warns upon violation (0 to just delete the message)" if _type == "warns" else "Max allowed amount for this rule",
            required=True,
            max_length=2 if title.split(" ")[1].lower() != "length" else 4
        ))
        self.add_item(discord.ui.TextInput(
            custom_id="response",
            label="Custom Response",
            style=discord.TextStyle.long,
            default=response,
            placeholder="An optional response the bot will send (leave blank for no response at all)",
            required=False,
            max_length=2000
        ))
        self.add_item(discord.ui.TextInput(
            custom_id="reason",
            label="Custom Reason",
            style=discord.TextStyle.long,
            default=reason,
            placeholder="An optional custom reason for logs (leave blank for default reason for this rule)",
            required=False,
            max_length=2000
        ))
        self.add_item(discord.ui.TextInput(
            custom_id="vars",
            label="Variable Reference",
            style=discord.TextStyle.long,
            placeholder="Putting something here won't have any effects. This field is just to show the available variables",
            default=self._vars_text,
            required=False,
            max_length=len(self._vars_text)
        ))


class DefaultReasonModal(TextModalBase):
    def __init__(self, bot, title: str, default: str, callback: Callable) -> None:
        super().__init__(bot, title, callback)
        self.add_item(discord.ui.TextInput(
            custom_id="reason",
            label=title,
            style=discord.TextStyle.long,
            default=default,
            placeholder="The default reason when none is given in commands",
            required=True,
            max_length=250,
            min_length=4
        ))


class EmbedBuilderModal(TextModalBase):
    def __init__(self, bot, title: str, callback: Callable) -> None:
        super().__init__(bot, title, callback)
    
        
    e_title = discord.ui.TextInput(
        custom_id="title",
        label="Title",
        style=discord.TextStyle.long,
        placeholder="Optional title of the embed",
        required=False,
        max_length=200
    )


    e_description = discord.ui.TextInput(
        custom_id="desc",
        label="Description",
        style=discord.TextStyle.long,
        placeholder="Optional description of the embed",
        required=False,
        max_length=2000
    )


    field_n_1 = discord.ui.TextInput(
        custom_id="fn1",
        label="Field Name",
        style=discord.TextStyle.long,
        placeholder="Name of the field",
        required=False,
        max_length=150
    )


    field_v_1 = discord.ui.TextInput(
        custom_id="fv1",
        label="Field Value",
        style=discord.TextStyle.long,
        placeholder="Value of the field",
        required=False,
        max_length=1024
    )


class ResponseCreateModal(TextModalBase):
    def __init__(self, bot, title: str, position: str, callback: Callable) -> None:
        super().__init__(bot, title, callback)
        self._placeholders = {
            "startswith": "Triggers for the response, seperated by commas (checks beginning of a message)",
            "endswith": "Triggers for the response, seperated by commas (checks end of a message)",
            "contains": "Triggers for the response, seperated by commas (checks anywhere within a message)",
            "regex": "RegEx that will trigger the response"
        }
        self._vars_text = "{user}  ━ The mention of the user, e.g. @paul \n{username}  ━ The name of the user, e.g. paul \n{avatar}  ━ The avatar URL of the user\n{channel}  ━ The channel name \n{server}  ━ The server name"

        self.add_item(discord.ui.TextInput(
            custom_id="name",
            label="Name",
            style=discord.TextStyle.short,
            placeholder="Name of the auto responder",
            required=True,
            max_length=20
        ))
        self.add_item(discord.ui.TextInput(
            custom_id="trigger",
            label="Trigger",
            style=discord.TextStyle.long,
            placeholder=self._placeholders[position],
            required=True,
            max_length=200 if position == "regex" else 1500
        ))
        self.add_item(discord.ui.TextInput(
            custom_id="content",
            label="Response",
            style=discord.TextStyle.long,
            placeholder="What the bot should respond with",
            required=True,
            max_length=2000
        ))
        self.add_item(discord.ui.TextInput(
            custom_id="vars",
            label="Variable Reference",
            style=discord.TextStyle.long,
            placeholder="Putting something here won't have any effects. This field is just to show the available variables",
            default=self._vars_text,
            required=False,
            max_length=len(self._vars_text)
        ))


class ResponseEditModal(TextModalBase):
    def __init__(self, bot, title: str, position: str, trigger: str, response: str, callback: Callable) -> None:
        super().__init__(bot, title, callback)
        self._placeholders = {
            "startswith": "Triggers for the response, seperated by commas (checks beginning of a message)",
            "endswith": "Triggers for the response, seperated by commas (checks end of a message)",
            "contains": "Triggers for the response, seperated by commas (checks anywhere within a message)",
            "regex": "RegEx that will trigger the response"
        }
        self._vars_text = "{user}  ━ The mention of the user, e.g. @paul \n{username}  ━ The name of the user, e.g. paul \n{avatar}  ━ The avatar URL of the user\n{channel}  ━ The channel name \n{server}  ━ The server name"

        self.add_item(discord.ui.TextInput(
            custom_id="trigger",
            label="Trigger",
            style=discord.TextStyle.long,
            placeholder=self._placeholders[position],
            default=trigger,
            required=True,
            max_length=200 if position == "regex" else 1500
        ))
        self.add_item(discord.ui.TextInput(
            custom_id="content",
            label="Response",
            style=discord.TextStyle.long,
            placeholder="What the bot should respond with",
            default=response,
            required=True,
            max_length=2000
        ))
        self.add_item(discord.ui.TextInput(
            custom_id="vars",
            label="Variable Reference",
            style=discord.TextStyle.long,
            placeholder="Putting something here won't have any effects. This field is just to show the available variables",
            default=self._vars_text,
            required=False,
            max_length=len(self._vars_text)
        ))


class WelcomeMessageModal(TextModalBase):
    def __init__(self, bot, title: str, current_message: str, callback: Callable) -> None:
        super().__init__(bot, title, callback)
        self._vars_text = "{user}  ━ The mention of the user, e.g. @paul \n{username}  ━ The name of the user, e.g. paul \n{avatar}  ━ The avatar URL of the user\n{server}  ━ The server name \n{user_count}  ━ New user count"
        
        self.add_item(discord.ui.TextInput(
            custom_id="message",
            label="Message",
            style=discord.TextStyle.short,
            placeholder="Message sent when users join",
            default=current_message if len(current_message) > 0 else None,
            required=True,
            max_length=2000
        ))
        self.add_item(discord.ui.TextInput(
            custom_id="vars",
            label="Variable Reference",
            style=discord.TextStyle.long,
            placeholder="Putting something here won't have any effects. This field is just to show the available variables",
            default=self._vars_text,
            required=False,
            max_length=len(self._vars_text)
        ))