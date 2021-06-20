import discord

from ...Types import Embed



async def run(plugin, ctx, channel_role):
    roles = plugin.db.configs.get(ctx.guild.id, "ignored_roles")
    channels = plugin.db.configs.get(ctx.guild.id, "ignored_channels")
    if channel_role is None:
        e = Embed()
        e.add_field(
            name="❯ Roles",
            value="\n".join(set([*[f"<@&{x.id}>" for x in sorted(ctx.guild.roles, key=lambda l: l.position) if x.position >= ctx.guild.me.top_role.position or x.permissions.ban_members]]))
        )
        
        channels = [f"<#{x}>" for x in sorted(channels)]
        if len(channels) > 0:
            e.add_field(
                name="❯ Channels", 
                value="\n".join(channels)
            )
        
        return await ctx.send(embed=e)

    cu = channel_role
    if cu.id in roles:
        return await ctx.send(plugin.db.configs.get(ctx.guild.id, "role_already_ignored", _emote="WARN"))

    if cu.id in channels:
        return await ctx.send(plugin.db.configs.get(ctx.guild.id, "channel_already_ignored", _emote="WARN"))
    
    if isinstance(cu, discord.Role):
        roles.append(cu.id)
        plugin.db.configs.update(ctx.guild.id, "ignored_roles", roles)
        return await ctx.send(plugin.t(ctx.guild, "role_ignored", _emote="YES", role=cu.name))
    elif isinstance(cu, discord.TextChannel):
        channels.append(cu.id)
        plugin.db.configs.update(ctx.guild.id, "ignored_channels", channels)
        return await ctx.send(plugin.t(ctx.guild, "channel_ignored", _emote="YES", channel=cu.name))