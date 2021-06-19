import discord
from discord.ext import commands



def is_mod(member):
    return member.guild_permissions.ban_members


def is_admin(member):
    return member.guild_permissions.administrator


def is_allowed(ctx, mod, target):
    bot = ctx.guild.me
    mod = ctx.guild.get_member(mod.id)
    if target is None:
        return True
    if target.top_role.position >= mod.top_role.position\
        or target.id == ctx.guild.owner.id \
        or target.top_role.position >= bot.top_role.position \
        or target.id == mod.id \
        or target.id == bot.id:
            return False
    else:
        return True


async def is_banned(ctx, user):
    try:
        await ctx.guild.fetch_ban(user)
    except discord.NotFound:
        return False
    else:
        return True