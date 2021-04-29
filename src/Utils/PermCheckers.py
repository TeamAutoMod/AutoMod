from discord.ext import commands


def is_owner():
    async def predicate(ctx):
        return ctx.bot.is_owner(ctx.author)
    
    return commands.check(predicate)


def is_mod(member):
    return member.guild_permissions.ban_members


def is_admin(member):
    return (hasattr(member, "roles") and member.guild_permissions.administrator)