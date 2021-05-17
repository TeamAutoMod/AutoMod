


async def addSelfroles(plugin, ctx, roles, role):
    # Split it, so we can add all roles, if the user wants multiple ones
    role = list(set(role.split(" ")))
    out = []
    can_be_added = []
    for r in role:
        try:
            role_id = roles[r]
        except KeyError:
            pass
        else:
            to_add = await plugin.bot.utils.getRole(ctx.guild, role_id)
            if to_add is None:
                del roles[r]
            elif to_add in ctx.author.roles:
                pass
            elif to_add.position >= ctx.guild.me.top_role.position:
                pass
            else:
                can_be_added.append(to_add)
                out.append(f"**{r}**")
        
    if len(out) == 0:
        return await ctx.send(plugin.t(ctx.guild, "no_valid_selfroles", _emote="WARN"))
    
    await ctx.author.add_roles(*can_be_added, reason="Selfroles")
    await ctx.send(plugin.t(ctx.guild, "granted_selfroles", _emote="YES", roles=", ".join(out), user=ctx.author.mention, plural="roles" if len(out) > 1 else "role"))