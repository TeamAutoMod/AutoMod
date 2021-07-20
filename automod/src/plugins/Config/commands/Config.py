from ...Types import Embed



async def run(plugin, ctx):
    cfg = plugin.db.configs.get_doc(ctx.guild.id)

    e = Embed()
    e.add_field(
        name="❯ Configurations",
        value="• Prefix: ``{}`` \n• Mute Role: {} \n• Mod Log: {} \n• Message Log: {} \n• Server Log: {} \n• Voice Log: {} \n• Persist Mode: {} \n• DM on actions: {} \n• Language: {} \n• Tags: {} \n• Timezone: ``UTC``"\
        .format(
            cfg["prefix"],
            f"<@&{cfg['mute_role']}>" if cfg['mute_role'] != "" else "``None``",

            f"<#{cfg['mod_log']}>" if cfg['mod_log'] != "" else "``None``",

            f"<#{cfg['message_log']}>" if cfg['message_log'] != "" else "``None``",

            f"<#{cfg['server_log']}>" if cfg['server_log'] != "" else "``None``",

            f"<#{cfg['voice_log']}>" if cfg['voice_log'] != "" else "``None``",

            "``On``" if cfg["persist"] is True else "``Off``",

            "``On``" if cfg["dm_on_actions"] is True else "``Off``",

            f"``{cfg['lang']}``",

            f"``{len([_ for _ in plugin.db.tags.find({}) if _['id'].split('-')[0] == str(ctx.guild.id)])}``"
        ),
        inline=True
    )

    f = plugin.emotes.get('WARN')
    punishments = [f"``{x} {f}``: {y.capitalize() if len(y.split(' ')) == 1 else y.split(' ')[0].capitalize() + ' ' + y.split(' ')[-2] + y.split(' ')[-1]}" for x, y in cfg["punishments"].items()]
    punishments = sorted(punishments, key=lambda i: i.split(" ")[0])
    e.add_field(
        name="❯ Punishments",
        value="{}".format("\n".join(punishments) if len(punishments) > 0 else "None"),
        inline=True
    )

    am = cfg['automod']
    e.add_field(
        name=f"❯ Automoderator",
        value="__Max-Mentions__ \n{} \n \n__Messages__ \n{} \n \n__Anti-Invites__ \n{} \n \n__Anti-Spam__ \n{} \n \n__Auto-Raid__ \n{}"\
        .format(
            f"• Threshold: ``{am['mention']['threshold']}``" if "mention" in am else "Disabled",

            f"• Anti-Caps: {'``' + str(am['caps']['warns']) + ' ' + f + '``' if 'caps' in am else 'Disabled'} \n• @every1 Attempt: {'``' + str(am['everyone']['warns']) + ' ' + f + '``' if 'everyone' in am else 'Disabled'}",
            
            f"• Warns: ``{am['invites']['warns']} {f}``" if "invites" in am else "Disabled",
            
            f"• Threshold: ``10`` messages/``10``s \nWarns: ``{am['spam']['warns']} {f}``" if "spam" in am else "Disabled",
            
            f"• Threshold: ``{am['raid']['threshold'].split('/')[0]}`` joins/``{am['raid']['threshold'].split('/')[1]}``s" if "raid" in am and am['raid']['status'] is True else "Disabled"
        ),
        inline=True
    )

    filters = plugin.db.configs.get(ctx.guild.id, "filters")
    if len(filters) > 0:
        e.add_field(
            name=f"❯ Filters",
            value="\n".join([f"• {x} - ``{filters[x]['warns']} {f}``" for x in filters])
        )

    await ctx.send(embed=e)