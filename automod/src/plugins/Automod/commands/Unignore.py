import discord
import traceback



async def run(plugin, ctx, channel_role):
    cu = channel_role
    roles = plugin.db.configs.get(ctx.guild.id, "ignored_roles")
    channels = plugin.db.configs.get(ctx.guild.id, "ignored_channels")
    
    if isinstance(cu, discord.Role):
        if cu.id not in roles:
            return await ctx.send(plugin.i18next.t(ctx.guild, "role_not_ignored", _emote="NO"))
        roles.remove(cu.id)
        plugin.db.configs.update(ctx.guild.id, "ignored_roles", roles)
        return await ctx.send(plugin.i18next.t(ctx.guild, "role_unignored", _emote="YES", role=cu.name))
    elif isinstance(cu, discord.TextChannel):
        if cu.id not in channels:
            return await ctx.send(plugin.i18next.t(ctx.guild, "channel_not_ignored", _emote="NO"))
        channels.remove(cu.id)
        plugin.db.configs.update(ctx.guild.id, "ignored_channels", channels)
        return await ctx.send(plugin.i18next.t(ctx.guild, "channel_unignored", _emote="YES", channel=cu.name))