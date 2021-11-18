import discord
from discord.ext import commands

import logging; log = logging.getLogger(__name__)
import traceback

from .PluginBlueprint import PluginBlueprint
from .Types import Embed



class NotCachedError(commands.CheckFailure):
    pass


class PostParseError(commands.BadArgument):
    def __init__(self, type, error):
        super().__init__(None)
        self.type = type
        self.error = error



class ErrorPlugin(PluginBlueprint):
    def __init__(self, bot):
        super().__init__(bot)


    @commands.Cog.listener()
    async def on_command_error(
        self,
        ctx,
        error
    ):
        # if isinstance(error, NotCachedError):
        #     if self.bot.ready is False:
        #         log.info("Tried to use a command while still chunking guilds - {}".format(ctx.guild.id))

        if isinstance(error, commands.CommandNotFound):
            return
        
        if isinstance(error, commands.MissingPermissions):
            perms = " | ".join([f"``{x}``" for x in error.missing_permissions])
            await ctx.send(self.i18next.t(ctx.guild, "missing_user_perms", _emote="LOCK", perms=perms))
        elif isinstance(error, commands.BotMissingPermissions):
            perms = " | ".join([f"``{x}``" for x in error.missing_permissions])
            await ctx.send(self.i18next.t(ctx.guild, "missing_bot_perms", _emote="LOCK", perms=perms))
        elif isinstance(error, commands.CheckFailure):
            await ctx.send(self.i18next.t(ctx.guild, "check_fail", _emote="LOCK"))
        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.send(self.i18next.t(ctx.guild, "on_cooldown", retry_after=round(error.retry_after)))
        elif isinstance(error.__cause__, discord.Forbidden):
            await ctx.send(self.i18next.t(ctx.guild, "forbidden", _emote="NO", exc=error))

        elif isinstance(error, commands.MissingRequiredArgument):
            param = list(ctx.command.params.values())[min(len(ctx.args) + len(ctx.kwargs), len(ctx.command.params))]
            self.bot.help_command.context = ctx
            usage = self.bot.help_command.get_command_signature(ctx.command)
            
            await ctx.send(self.i18next.t(ctx.guild, "missing_arg", _emote="NO", param=param._name, usage=usage))
        elif isinstance(error, PostParseError):
            self.bot.help_command.context = ctx
            usage = self.bot.help_command.get_command_signature(ctx.command)
            
            await ctx.send(self.i18next.t(ctx.guild, "bad_argument", _emote="NO", param=error.type, error=error.error, usage=usage))
        elif isinstance(error, commands.BadArgument) or isinstance(error, commands.BadUnionArgument):
            self.bot.help_command.context = ctx
            usage = self.bot.help_command.get_command_signature(ctx.command)
            try:
                param = list(ctx.command.params.values())[min(len(ctx.args) + len(ctx.kwargs), len(ctx.command.params))]
            except IndexError:
                await ctx.send(self.i18next.t(ctx.guild, "bad_argument_no_param", _emote="NO", error=error, usage=usage))
            else:
                await ctx.send(self.i18next.t(ctx.guild, "bad_argument", _emote="NO", param=param._name, error=error, usage=usage))
        else:
            e = Embed(
                color=0xff5c5c,
                title="❯ Command Error",
                description="```py\n{}\n```".format("".join(
                    traceback.format_exception(
                        etype=type(error), 
                        value=error, 
                        tb=error.__traceback__
                    )
                ))
            )
            e.add_field(
                name="❯ Location",
                value="• Name: {} \n• ID: {}".format(
                    ctx.guild.name or "None",
                    ctx.guild.id or "None"
                )
            )
            await self.bot.utils.sendErrorLog(e)


def setup(bot):
    bot.add_cog(ErrorPlugin(bot))