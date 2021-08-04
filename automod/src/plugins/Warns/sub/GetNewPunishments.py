


async def getNewPunishments(plugin, ctx):
    cfg = plugin.db.configs.get(ctx.guild.id, "punishments")
    f = plugin.emotes.get('WARN')
    punishments = [f"``{x} {f}``: {y.capitalize() if len(y.split(' ')) == 1 else y.split(' ')[0].capitalize() + ' ' + y.split(' ')[-2] + y.split(' ')[-1]}" for x, y in cfg.items()]
    punishments = sorted(punishments, key=lambda i: i.split(" ")[0])
    return punishments