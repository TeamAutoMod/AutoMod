


async def run(plugin, member, before, after):
    if member.guild is None:
        return
    alerts = [x for x in plugin.db.follows.find({}) if x["id"].split("-")[0] == str(member.guild.id)]

    should_be_notified = [x["id"].split("-")[1] for x in alerts if member.id in x["users"]]

    if len(should_be_notified) < 1:
        return

    if before.channel is None and after.channel is not None:
        for r in should_be_notified:
            requestor = await plugin.bot.utils.getMember(member.guild, int(r))
            if requestor is None:
                pass
            else:
                try:
                    await requestor.send("An alert requested by you has triggered!\n``{}`` has joined voice channel ``{}`` in server ``{}``".format(member, after.channel, member.guild))
                except Exception:
                    pass