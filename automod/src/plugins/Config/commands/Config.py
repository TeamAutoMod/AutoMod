from ...Types import Embed



async def run(plugin, ctx):
    cfg = plugin.db.configs.get_doc(ctx.guild.id)

    e = Embed()
    e.set_thumbnail(url=ctx.guild.icon_url_as())
    e.add_field(
        name="❯ Configurations",
        value="• Prefix: ``{}`` \n• Mute Role: {} \n• Mod Log: {} \n• Message Log: {} \n• Server Log: {} \n• Voice Log: {} \n• Persist Mode: {} \n• DM on actions: {}"\
        .format(
            cfg["prefix"],
            f"<@&{cfg['mute_role']}>" if cfg['mute_role'] != "" else "``None``",

            f"<#{cfg['mod_log']}>" if cfg['mod_log'] != "" else "``None``",

            f"<#{cfg['message_log']}>" if cfg['message_log'] != "" else "``None``",

            f"<#{cfg['server_log']}>" if cfg['server_log'] != "" else "``None``",

            f"<#{cfg['voice_log']}>" if cfg['voice_log'] != "" else "``None``",

            "``On``" if cfg["persist"] is True else "``Off``",

            "``On``" if cfg["dm_on_actions"] is True else "``Off``",
        ),
        inline=True
    )

    f = plugin.emotes.get('WARN')
    punishments = [f"• {x} {'warn' if int(x) == 1 else 'warns'}: ``{y.capitalize() if len(y.split(' ')) == 1 else y.split(' ')[0].capitalize() + ' ' + y.split(' ')[-2] + y.split(' ')[-1]}``" for x, y in cfg["punishments"].items()]
    punishments = sorted(punishments, key=lambda i: i.split(" ")[0])
    e.add_field(
        name="❯ Punishments",
        value="{}".format("\n".join(punishments) if len(punishments) > 0 else "• None"),
        inline=True
    )

    filters = plugin.db.configs.get(ctx.guild.id, "filters")
    e.add_field(
        name=f"❯ Filters",
        value="\n".join([f"• {x}: ``{filters[x]['warns']} {'warn' if int(filters[x]['warns']) == 1 else 'warns'}``" for x in filters]) if len(filters) > 0 else "• None",
        inline=True
    )
    
    am = cfg['automod']
    e.add_field(
        name="❯ Max Mentions", 
        value=f"• Threshold: ``{am['mention']['threshold']}``" if "mention" in am else "• Disabled", 
        inline=True
    )
    e.add_field(
        name="❯ Anti Caps", 
        value=f"• {'Warns: ``' + str(am['caps']['warns']) + '``' if 'caps' in am else 'Disabled'}", 
        inline=True
    )
    e.add_field(
        name="❯ Anti @ever1", 
        value=f"• {'Warns: ``' + str(am['everyone']['warns']) + '``' if 'everyone' in am else 'Disabled'}", 
        inline=True
    )
    e.add_field(
        name="❯ Anti Caps", 
        value=f"• Warns: ``{am['invites']['warns']}``" if "invites" in am else "• Disabled", 
        inline=True
    )
    e.add_field(
        name="❯ Anti Spam", 
        value=f"• Warns: ``{am['spam']['warns']}``" if "spam" in am else "• Disabled", 
        inline=True
    )
    e.add_field(
        name="❯ Anti Raid", 
        value=f"• Threshold: ``{am['raid']['threshold'].split('/')[0]}``/``{am['raid']['threshold'].split('/')[1]}``" if "raid" in am and am['raid']['status'] is True else "• Disabled", 
        inline=True
    )
    
    await ctx.send(embed=e)