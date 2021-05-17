import discord

from ....utils import Permissions



async def masskickUsers(plugin, ctx, targets, reason):
    targets = list(set(targets))
    failing = 0
    to_kick = list()
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
                to_kick.append(t)
        else:
            failing += 1
            
    if failing >= len(targets):
        return await ctx.send(plugin.translator.translate(ctx.guild, "cant_kick_anyone", _emote="WARN"))
    
    confirm = await ctx.prompt(f'This action will kick {len(to_kick)} member{"" if len(to_kick) == 1 else "s"}. Are you sure?', timeout=15)
    if not confirm:
        return await ctx.send(plugin.translator.translate(ctx.guild, "aborting"))

    kicked = 0
    for t in to_kick:
        try:
            await ctx.guild.kick(user=t, reason=reason)
            plugin.bot.ignore_for_event.add("bans_kicks", t.id)

            _ = plugin.bot.utils.newCase(ctx.guild, "Ban", t, ctx.author, f"[Massban] {reason}")
        except discord.HTTPException:
            pass
        else:
            kicked += 1
        
    await ctx.send(plugin.translator.translate(ctx.guild, "mkick_success", _emote="YES", users=kicked, total=len(to_kick)))
    await plugin.action_logger.log(
            ctx.guild, 
            "mass_kick", 
            moderator=ctx.message.author, 
            moderator_id=ctx.message.author.id,
            users=kicked,
            reason=reason
        )