


async def overwrite(plugin, ctx, msg, roles):
    for k, v in roles.items():
        role = v["role"]
        try:
            for c in ctx.guild.categories:
                ov = c.overwrites
                ov.update({
                    role: v["perms"]
                })
                await c.edit(overwrites=ov)
        except Exception as ex:
            return await msg.edit(content=plugin.i18next.t(ctx.guild, "category_fail", _emote="NO", category=c.name, exc=ex))
        else:
            plugin.db.configs.update(ctx.guild.id, k, f"{role.id}")
    await msg.edit(content=f"{msg.content} \n{plugin.emotes.get('YES')} Category overwrites complete!")

    for k, v in roles.items():
        role = v["role"]
        try:
            for c in ctx.guild.text_channels:
                ov = c.overwrites
                ov.update({
                    role: v["perms"]
                })
                await c.edit(overwrites=ov)
        except Exception as ex:
            return await msg.edit(content=plugin.i18next.t(ctx.guild, "text_fail", _emote="NO", channel=c.name, exc=ex))
        else:
            plugin.db.configs.update(ctx.guild.id, k, f"{role.id}")
    await msg.edit(content=f"{msg.content} \n{plugin.emotes.get('YES')} Text channel overwrites complete!")

    await msg.edit(content=plugin.i18next.t(ctx.guild, "restrict_done", _emote="YES"))