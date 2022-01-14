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
        
        if isinstance(error, commands.MissingPermissions):
            perms = " | ".join([f"``{x}``" for x in error.missing_permissions])
            await ctx.send(self.locale.t(ctx.guild, "missing_user_perms", _emote="LOCK", perms=perms))
        
        elif isinstance(error, commands.BotMissingPermissions):
            perms = " | ".join([f"``{x}``" for x in error.missing_permissions])
            await ctx.send(self.locale.t(ctx.guild, "missing_bot_perms", _emote="LOCK", perms=perms))
        
        elif isinstance(error, commands.CheckFailure):
            if len(ctx.commands.checks) < 1:
                await ctx.send(self.locale.t(ctx.guild, "check_fail", _emote="LOCK"))
            else:
                ctx.commands.checks[0](ctx) # this raises a 'commands.MissingPermissions'
        
        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.send(self.locale.t(ctx.guild, "on_cooldown", _emote="NO", retry_after=round(error.retry_after)))
        
        elif isinstance(error.__cause__, discord.Forbidden):
            await ctx.send(self.locale.t(ctx.guild, "forbidden", _emote="NO", exc=error))

        elif isinstance(error, commands.MissingRequiredArgument):
            param = list(ctx.command.params.values())[min(len(ctx.args) + len(ctx.kwargs), len(ctx.command.params))]
            self.bot.help_command.context = ctx; usage = self.bot.help_command.get_command_signature(ctx.command)
            info = f"{self.get_prefix(ctx.guild)}help {ctx.command.qualified_name}"
            await ctx.send(self.locale.t(ctx.guild, "missing_arg", _emote="NO", param=param._name, usage=usage, info=info))
        
        elif isinstance(error, PostParseError):
            self.bot.help_command.context = ctx; usage = self.bot.help_command.get_command_signature(ctx.command)
            info = f"{self.get_prefix(ctx.guild)}help {ctx.command.qualified_name}"
            await ctx.send(self.locale.t(ctx.guild, "bad_arg", _emote="NO", param=error.type, error=error.error, usage=usage, info=info))

        elif isinstance(error, commands.BadArgument) or isinstance(error, commands.BadUnionArgument):
            self.bot.help_command.context = ctx
            usage = self.bot.help_command.get_command_signature(ctx.command)
            info = f"{self.get_prefix(ctx.guild)}help {ctx.command.qualified_name}"
            try:
                param = list(ctx.command.params.values())[min(len(ctx.args) + len(ctx.kwargs), len(ctx.command.params))]
            except IndexError:
                await ctx.send(self.locale.t(ctx.guild, "bad_arg_no_param", _emote="NO", error=error, usage=usage, info=info))
            else:
                await ctx.send(self.locale.t(ctx.guild, "bad_arg", _emote="NO", param=param._name, error=error, usage=usage, info=info))

        else:
            log.error(f"Error in command {ctx.command} - {''.join(traceback.format_exception(etype=type(error), value=error, tb=error.__traceback__))}")


def setup(bot): bot.register_plugin(ErrorPlugin(bot))