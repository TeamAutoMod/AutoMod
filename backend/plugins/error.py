import discord
from discord.ext import commands

import logging; log = logging.getLogger()
import traceback
from typing import TypeVar

from . import AutoModPlugin, ShardedBotInstance
from ..types import Embed



T = TypeVar("T")


class PostParseError(commands.BadArgument):
    def __init__(self, type: T, error: Exception) -> None:
        super().__init__(None)
        self.type = type
        self.error = error


class ErrorPlugin(AutoModPlugin):
    """Plugin to handle command/event errors"""
    def __init__(self, bot: ShardedBotInstance) -> None:
        super().__init__(bot)


    @AutoModPlugin.listener()
    async def on_command_error(self, ctx: commands.Context, error: Exception) -> None:
        if isinstance(error, commands.CommandNotFound):
            return
        
        if isinstance(error, commands.NotOwner):
            await ctx.send(f"{self.bot.emotes.get('NO')} You can't use this command")
        elif isinstance(error, commands.MissingPermissions):
            perms = ", ".join([f"``{x}``" for x in error.missing_permissions])
            rid = self.bot.db.configs.get(ctx.guild.id, "mod_role")
            if rid != "":
                role = ctx.guild.get_role(int(rid))
                if role != None:
                    perms += f" or the ``{role.name}`` role"
            
            e = Embed(
                description=self.locale.t(ctx.guild, "missing_user_perms", _emote="LOCK", perms=perms)
            )
            await ctx.send(embed=e)
        
        elif isinstance(error, commands.BotMissingPermissions):
            perms = ", ".join([f"``{x}``" for x in error.missing_permissions])
            e = Embed(
                description=self.locale.t(ctx.guild, "missing_bot_perms", _emote="LOCK", perms=perms)
            )
            await ctx.send(embed=e)
        
        elif isinstance(error, commands.CheckFailure):
            if len(ctx.command.checks) < 1:
                e = Embed(
                    description=self.locale.t(ctx.guild, "check_fail", _emote="LOCK")
                )
                await ctx.send(embed=e)
            else:
                await ctx.command.checks[0](ctx) # this raises a 'commands.MissingPermissions'
        
        elif isinstance(error, commands.CommandOnCooldown):
            e = Embed(
                description=self.locale.t(ctx.guild, "on_cooldown", _emote="NO", retry_after=round(error.retry_after))
            )
            await ctx.send(embed=e)
        
        elif isinstance(error.__cause__, discord.Forbidden):
            e = Embed(
                description=self.locale.t(ctx.guild, "forbidden", _emote="NO", exc=error)
            )
            await ctx.send(embed=e)

        elif isinstance(error, commands.MissingRequiredArgument):
            param = list(ctx.command.params.values())[min(len(ctx.args) + len(ctx.kwargs) - 1, len(ctx.command.params)) - 1]
            usage = f"{self.get_prefix(ctx.guild)}{ctx.command.qualified_name} {ctx.command.signature.replace('...', '')}"
            info = f"{self.get_prefix(ctx.guild)}help {ctx.command.qualified_name}"

            e = Embed(
                description=self.locale.t(ctx.guild, "missing_arg", _emote="NO", param=param._name)
            )
            e.add_fields([
                {
                    "name": "❯ Usage",
                    "value": f"``{usage}``"
                },
                {
                    "name": "❯ Info",
                    "value": f"``{info}``"
                }
            ])
            await ctx.send(embed=e)
        
        elif isinstance(error, PostParseError):
            usage = f"{self.get_prefix(ctx.guild)}{ctx.command.qualified_name} {ctx.command.signature.replace('...', '')}"
            info = f"{self.get_prefix(ctx.guild)}help {ctx.command.qualified_name}"

            e = Embed(
                description=self.locale.t(ctx.guild, "bad_arg", _emote="NO", param=error.type, error=error.error)
            )
            e.add_fields([
                {
                    "name": "❯ Usage",
                    "value": f"``{usage}``"
                },
                {
                    "name": "❯ Info",
                    "value": f"``{info}``"
                }
            ])
            await ctx.send(embed=e)

        elif isinstance(error, commands.BadArgument) or isinstance(error, commands.BadUnionArgument):
            usage = f"{self.get_prefix(ctx.guild)}{ctx.command.qualified_name} {ctx.command.signature.replace('...', '')}"
            info = f"{self.get_prefix(ctx.guild)}help {ctx.command.qualified_name}"

            e = Embed()
            e.add_fields([
                {
                    "name": "❯ Usage",
                    "value": f"``{usage}``"
                },
                {
                    "name": "❯ Info",
                    "value": f"``{info}``"
                }
            ])
            try:
                param = list(ctx.command.params.values())[min(len(ctx.args) + len(ctx.kwargs), len(ctx.command.params))]
            except IndexError:
                e.description = self.locale.t(ctx.guild, "bad_arg_no_param", _emote="NO", error=error)
            else:
                e.description = self.locale.t(ctx.guild, "bad_arg", _emote="NO", param=param._name, error=error)
            finally:
                await ctx.send(embed=e)

        else:
            log.error(f"❌ Error in command {ctx.command} - {''.join(traceback.format_exception(etype=type(error), value=error, tb=error.__traceback__))}")

            e = Embed(
                color=0xff5c5c,
                title="Uncaught error",
                description="```py\n{}\n```".format(("".join(traceback.format_exception(etype=type(error), value=error, tb=error.__traceback__)))[:4000])
            )
            e.add_fields([
                {
                    "name": "❯ Command",
                    "value": f"{ctx.command.qualified_name}" if ctx.command != None else "Unknown",
                    "inline": True
                },
                {
                    "name": "❯ Location",
                    "value": f"{ctx.guild.name} ({ctx.guild.id})" if ctx.guild != None else "Unknown",
                    "inline": True
                }
            ])

            if self.bot.error_log == None:
                try:
                    cid = int(self.bot.config.error_channel)
                except (AttributeError, ValueError):
                    return
                else:
                    clog = await self.bot.fetch_channel(cid)
                    if clog != None:
                        try:
                            await clog.send(embed=e)
                        except Exception:
                            return
                        else:
                            self.bot.error_log = clog
            else:
                try:
                    await self.bot.error_log.send(embed=e)
                except Exception:
                    self.bot.error_log = None


async def setup(bot) -> None: await bot.register_plugin(ErrorPlugin(bot))