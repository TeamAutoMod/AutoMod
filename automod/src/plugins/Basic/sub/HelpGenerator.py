import discord
from discord.ext.commands import GroupMixin

from ...Types import Embed
from ....utils.Views import HelpView



async def getHelpForAllCommands(plugin, ctx):
    plugin.bot.help_command.context = ctx
    prefix = plugin.bot.get_guild_prefix(ctx.guild)
    actual_plugin_names = {
        "AutomodPlugin": f"❯ Automod Commands",
        "BasicPlugin": f"❯ Basic Commands",
        "ModerationPlugin": f"❯ Moderation Commands",
        "WarnsPlugin": f"❯ Warn Commands",
        "CasesPlugin": f"❯ Case Commands",
        "ConfigPlugin": f"❯ Configuration Commands",
        "TagsPlugin": f"❯ Tag Commands",
        "FiltersPlugin": f"❯ Filter Commands"
    }

    valid_plugins = [plugin.bot.get_cog(x) for x in plugin.bot.cogs if x in plugin.bot.config.enabled_plugins_with_commands]
    e = Embed(
        title="Commands",
        description=f"This is a list of all available commands. \nTo get more info about a command, use ``{prefix}help <command>``"
    )
    for p in valid_plugins:
        e.add_field(
            name=actual_plugin_names[p.qualified_name],
            value=" | ".join([f"``{prefix}{x}``" for x in p.get_commands()])
        )
    return e

actual_plugin_names = {
    "AutomodPlugin": f"🛡️ Automod Commands",
    "BasicPlugin": f"🎉 Basic Commands",
    "ModerationPlugin": f"🔨 Moderation Commands",
    "WarnsPlugin": f"📌 Warn Commands",
    "CasesPlugin": f"🔎 Case Commands",
    "ConfigPlugin": f"⚙️ Configuration Commands",
    "TagsPlugin": f"📝 Tag Commands",
    "FiltersPlugin": f"📦 Filter Commands"
}

async def getHelpForPlugin(bot, _plugin, i: discord.Interaction):
    guild = bot.get_guild(i.guild_id)
    prefix = bot.get_guild_prefix(guild)

    if _plugin == None:
        e = Embed(
            title=bot.i18next.t(guild, "help_title"),
            description=bot.i18next.t(guild, "help_description", prefix=prefix)
        )
        e.set_thumbnail(
            url=bot.user.display_avatar
        )
        view = HelpView(guild, bot, "None")
        return e, view
    
    plugin = {v: k for k, v in actual_plugin_names.items()}.get(_plugin)
    actual_plugin = bot.get_cog(plugin)
    e = Embed(
        title=" ".join(actual_plugin_names[plugin].split(" ")[1:]).replace("Commands", "Plugin"),
        description=bot.i18next.t(guild, f"{plugin.lower()}_long_description", prefix=prefix)
    )
    e.add_field(
        name=f"❯ Commands",
        value="\n".join([f"``{prefix}{str(x)}`` - {bot.i18next.t(guild, x.help)}" for x in actual_plugin.get_commands()])
    )

    view = HelpView(guild, bot, actual_plugin.qualified_name)
    return e, view






async def generateHelpForCommand(plugin, ctx, command):
    plugin.bot.help_command.context = ctx
    name = ctx.bot.help_command.get_command_signature(command)
    help_message = plugin.i18next.t(ctx.guild, f"{command.help}")
    if name[-1] == " ":
        name = name[:-1]

    e = Embed(title=f"``{name.replace('...', '')}``")
    e.add_field(name="❯ Description", value=help_message)
    
    if isinstance(command, GroupMixin) and hasattr(command, "all_commands"):
        actual_subcommands = {}
        for k, v in command.all_commands.items():
            if not v in actual_subcommands.values():
                actual_subcommands[k] = v

        if len(actual_subcommands.keys()) > 0:
            e.add_field(name="❯ Subcommands", value=" | ".join([f"``{x}``" for x in actual_subcommands.keys()]), inline=True)

    return e



async def getHelpForCommand(plugin, ctx, query):
    t = plugin.bot
    layers = query.split(" ")
    while len(layers) > 0:
        layer = layers.pop(0)
        if hasattr(t, 'all_commands') and layer in t.all_commands.keys():
            t = t.all_commands[layer]
        else:
            t = None
            break
    if t is not None and t is not plugin.bot.all_commands:
        return await generateHelpForCommand(plugin, ctx, t)
    return None