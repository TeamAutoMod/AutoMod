from discord.ext.commands import GroupMixin

from ...Types import Embed



async def getHelpForAllCommands(plugin, ctx):
    out = []
    valid_plugins = [plugin.bot.get_cog(x) for x in plugin.bot.cogs if x in plugin.bot.config['enabled_plugins_with_commands']]
    actual_plugin_names = {
        "BasicPlugin": f"{ctx.bot.emotes.get('LINK')} Basic",
        "ModerationPlugin": f"{ctx.bot.emotes.get('HAMMER')} Moderation",
        "SelfrolesPlugin": f"{ctx.bot.emotes.get('PEN')} Selfroles",
        "CasesPlugin": f"{ctx.bot.emotes.get('FOLDER')} Cases",
        "ConfigPlugin": f"{ctx.bot.emotes.get('COG')} Configuration",
        "LocateUserPlugin": f"{ctx.bot.emotes.get('SEARCH')} Locate User",
        "CleanPlugin": f"{ctx.bot.emotes.get('CLEAN')} Clean Messages"
    }
    for plugin in valid_plugins:
        out.append({
            actual_plugin_names[plugin.qualified_name]: "```\n{}\n```".format("\n".join([x.name for x in plugin.get_commands()]))
        })
    
    prefix = plugin.bot.get_guild_prefix(ctx.guild)
    kwargs = {
        "title": plugin.translator.translate(ctx.guild, "help_page"),
        "description": plugin.translator.translate(ctx.guild, "help_description", prefix=prefix)
    }
    main_embed = Embed(**kwargs)

    pages = []
    fields = 0
    max_fields = 4
    max_fields -= 1
    for i, inp in enumerate(out):
        field_kwargs = {
            "name": list(inp.keys())[0],
            "value": list(inp.values())[0]
        }
        if fields >= max_fields:
            main_embed.add_field(**field_kwargs)
            pages.append(main_embed)
            main_embed = Embed(**kwargs)
            fields = 0
        else:
            fields += 1
            if len(out) <= i+1:
                main_embed.add_field(**field_kwargs)
                pages.append(main_embed)
            else:
                main_embed.add_field(**field_kwargs)
    
    for i, e in enumerate(pages):
        e.set_footer(text="Page: {}/{}".format(i+1, len(pages)))

    return pages



async def generateHelpForCommand(plugin, ctx, command):
    plugin.bot.help_command.context = ctx
    usage = ctx.bot.help_command.get_command_signature(command)
    help_message = plugin.translator.translate(ctx.guild, f"{command.help}")

    e = Embed(title=plugin.translator.translate(ctx.guild, "command_help"))
    e.add_field(name="Description", value=f"```\n{help_message}\n```")
    e.add_field(name="Usage", value=f"```\n{usage}\n```")

    commands = []
    if isinstance(command, GroupMixin) and hasattr(command, "all_commands"):
        commands = set([x.name for x in command.all_commands.values()])
    e.add_field(name="Subcommands", value="```\n{}\n```".format("\n".join(commands) if len(commands) > 0 else "None"))

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