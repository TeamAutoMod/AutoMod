import discord

from ....utils import Permissions



async def massbanUsers(plugin, ctx, targets, reason):
    targets = list(set(targets))
    failing = 0
    to_ban = list()
    for t in targets:
        member = ctx.guild.get_member(t.id)
        bot = ctx.guild.me
        if member is not None:
            if member.top_role.position >= bot.top_role.position \
                or member.top_role.position >= ctx.author.top_role.position \
                or member.id == ctx.author.id \
                or member.id == ctx.guild.owner.id:
                    failing += 1
            else:
                to_ban.append(t)
        else:
            if await Permissions.is_banned(ctx, t):
                failing += 1
            else:
                to_ban.append(t)
            
    if failing >= len(targets):
        return await ctx.send(plugin.translator.translate(ctx.guild, "cant_ban_anyone", _emote="WARN"))
    
    confirm = await ctx.prompt(f'This action will ban {len(to_ban)} member{"" if len(to_ban) == 1 else "s"}. Are you sure?', timeout=15)
    if not confirm:
        return await ctx.send(plugin.translator.translate(ctx.guild, "aborting"))

    banned = 0
    for t in to_ban:
        try:
            await ctx.guild.ban(user=t, reason=reason)
            plugin.bot.ignore_for_event.add("bans_kicks", t.id)

            _ = plugin.bot.utils.newCase(ctx.guild, "Ban", t, ctx.author, f"[Massban] {reason}")
        except discord.HTTPException:
            pass
        else:
            banned += 1
        
    await ctx.send(plugin.translator.translate(ctx.guild, "mban_success", _emote="YES", users=banned, total=len(to_ban)))
    await plugin.action_logger.log(
            ctx.guild, 
            "mass_ban", 
            moderator=ctx.message.author, 
            moderator_id=ctx.message.author.id,
            users=banned,
            reason=reason
        )
