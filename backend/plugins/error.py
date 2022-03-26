import discord
from discord.ext import commands

import logging; log = logging.getLogger()
import traceback

from . import AutoModPlugin



class PostParseError(commands.BadArgument):
    def __init__(self, type, error):
        super().__init__(None)
        self.type = type
        self.error = error


class ErrorPlugin(AutoModPlugin):
    """Plugin to handle command/event errors"""
    def __init__(self, bot):
        super().__init__(bot)


    @AutoModPlugin.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            return
        
        if isinstance(error, commands.NotOwner):
            await ctx.send(f"{self.bot.emotes.get('NO')} You can't use this command")
        elif isinstance(error, commands.MissingPermissions):
            perms = " | ".join([f"``{x}``" for x in error.missing_permissions])
            await ctx.send(self.locale.t(ctx.guild, "missing_user_perms", _emote="LOCK", perms=perms))
        
        elif isinstance(error, commands.BotMissingPermissions):
            perms = " | ".join([f"``{x}``" for x in error.missing_permissions])
            await ctx.send(self.locale.t(ctx.guild, "missing_bot_perms", _emote="LOCK", perms=perms))
        
        elif isinstance(error, commands.CheckFailure):
            if len(ctx.command.checks) < 1:
                await ctx.send(self.locale.t(ctx.guild, "check_fail", _emote="LOCK"))
            else:
                await ctx.command.checks[0](ctx) # this raises a 'commands.MissingPermissions'
        
        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.send(self.locale.t(ctx.guild, "on_cooldown", _emote="NO", retry_after=round(error.retry_after)))
        
        elif isinstance(error.__cause__, discord.Forbidden):
            await ctx.send(self.locale.t(ctx.guild, "forbidden", _emote="NO", exc=error))

        elif isinstance(error, commands.MissingRequiredArgument):
            param = list(ctx.command.params.values())[len(ctx.args) + len(ctx.kwargs) - len(ctx.command.params)]
            usage = f"{self.get_prefix(ctx.guild)}{ctx.command.qualified_name} {ctx.command.signature}"
            info = f"{self.get_prefix(ctx.guild)}help {ctx.command.qualified_name}"
            await ctx.send(self.locale.t(ctx.guild, "missing_arg", _emote="NO", param=param._name, usage=usage, info=info))
        
        elif isinstance(error, PostParseError):
            usage = f"{self.get_prefix(ctx.guild)}{ctx.command.qualified_name} {ctx.command.signature}"
            info = f"{self.get_prefix(ctx.guild)}help {ctx.command.qualified_name}"
            await ctx.send(self.locale.t(ctx.guild, "bad_arg", _emote="NO", param=error.type, error=error.error, usage=usage, info=info))

        elif isinstance(error, commands.BadArgument) or isinstance(error, commands.BadUnionArgument):
            usage = f"{self.get_prefix(ctx.guild)}{ctx.command.qualified_name} {ctx.command.signature}"
            info = f"{self.get_prefix(ctx.guild)}help {ctx.command.qualified_name}"
            try:
                param = list(ctx.command.params.values())[min(len(ctx.args) + len(ctx.kwargs), len(ctx.command.params))]
            except IndexError:
                await ctx.send(self.locale.t(ctx.guild, "bad_arg_no_param", _emote="NO", error=error, usage=usage, info=info))
            else:
                await ctx.send(self.locale.t(ctx.guild, "bad_arg", _emote="NO", param=param._name, error=error, usage=usage, info=info))

        else:
            log.error(f"Error in command {ctx.command} - {''.join(traceback.format_exception(etype=type(error), value=error, tb=error.__traceback__))}")


async def setup(bot): await bot.register_plugin(ErrorPlugin(bot))
