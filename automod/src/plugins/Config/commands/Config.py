from ...Types import Embed



async def run(plugin, ctx):
    cfg = plugin.db.configs.get_doc(ctx.guild.id)

    e = Embed(
        title="Server configuration",
        description="This shows all of the current server and automoderator configurations."
    )
    if ctx.guild.icon != None:
        e.set_thumbnail(url=ctx.guild.icon.url)
    e.add_field(
        name="Prefix",
        value=f"``{cfg['prefix']}``",
        inline=True
    )
    e.add_field(
        name="Mute Role",
        value=f"<@&{cfg['mute_role']}>" if cfg['mute_role'] != "" else "``❌``",
        inline=True
    )
    e.add_field(
        name="Mod Log",
        value=f"<#{cfg['mod_log']}>" if cfg['mod_log'] != "" else "``❌``",
        inline=True
    )
    e.add_field(
        name="Message Log",
        value=f"<#{cfg['message_log']}>" if cfg['message_log'] != "" else "``❌``",
        inline=True
    )
    e.add_field(
        name="Server Log",
        value=f"<#{cfg['server_log']}>" if cfg['server_log'] != "" else "``❌``",
        inline=True
    )
    e.add_field(
        name="Voice Log",
        value=f"<#{cfg['voice_log']}>" if cfg['voice_log'] != "" else "``❌``",
        inline=True
    )
    e.add_field(
        name="Persist Mode",
        value=f"``✅``" if cfg['persist'] is True else "``❌``",
        inline=True
    )
    e.add_field(
        name="DM on actions",
        value=f"``✅``" if cfg['dm_on_actions'] is True else "``❌``",
        inline=True
    )
    e.add_field(
        name="Timezone",
        value="``UTC``",
        inline=True
    )
    
    am = cfg['automod']
    e.add_field(
        name="Max Mentions", 
        value=f"``{am['mention']['threshold']} mentions``" if "mention" in am else "``❌``", 
        inline=True
    )
    e.add_field(
        name="Anti Caps", 
        value=f"``{am['caps']['warns']} {'warn' if int(am['caps']['warns']) == 1 else 'warns'}``" if 'caps' in am else "``❌``", 
        inline=True
    )
    e.add_field(
        name="Anti @ever1", 
        value=f"``{am['everyone']['warns']} {'warn' if int(am['everyone']['warns']) == 1 else 'warns'}``" if 'everyone' in am else "``❌``", 
        inline=True
    )
    e.add_field(
        name="Anti Invites", 
        value=f"``{am['invites']['warns']} {'warn' if int(am['invites']['warns']) == 1 else 'warns'}``" if "invites" in am else "``❌``", 
        inline=True
    )
    e.add_field(
        name="Anti Spam", 
        value=f"``{am['spam']['warns']} {'warn' if int(am['spam']['warns']) == 1 else 'warns'}``" if "spam" in am else "``❌``", 
        inline=True
    )
    e.add_field(
        name="Anti Raid", 
        value=f"``{am['raid']['threshold'].split('/')[0]}``/``{am['raid']['threshold'].split('/')[1]}``" if "raid" in am and am['raid']['status'] is True else "``❌``", 
        inline=True
    )
    e.add_field(
        name="Bad Files", 
        value=f"``{am['files']['warns']} {'warn' if int(am['files']['warns']) == 1 else 'warns'}``" if "files" in am else "``❌``", 
        inline=True
    )
    e.add_field(
        name="Max Newlines", 
        value=f"``{am['lines']['threshold']} lines``" if "files" in am else "``❌``", 
        inline=True
    )
    e.add_field(
        name="Anti Zalgo", 
        value=f"``{am['zalgo']['warns']} {'warn' if int(am['zalgo']['warns']) == 1 else 'warns'}``" if "files" in am else "``❌``", 
        inline=True
    )

    punishments = [f"``{x} ({y.capitalize() if len(y.split(' ')) == 1 else y.split(' ')[0].capitalize() + ' ' + y.split(' ')[-2] + y.split(' ')[-1]})``" for x, y in cfg["punishments"].items()]
    punishments = sorted(punishments, key=lambda i: int(i.split(" ")[0].replace("``", "")))
    e.add_field(
        name="Punishments",
        value="{}".format(" | ".join(punishments) if len(punishments) > 0 else "``❌``"),
        inline=False
    )

    filters = plugin.db.configs.get(ctx.guild.id, "filters")
    e.add_field(
        name=f"Filters",
        value=" | ".join([f"``{x}``" for x in filters]) if len(filters) > 0 else "``❌``",
        inline=False
    )
    
    await ctx.send(embed=e)