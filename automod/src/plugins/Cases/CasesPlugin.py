import discord
from discord.ext import commands

from typing import Optional, Union

from ..PluginBlueprint import PluginBlueprint
from ..Types import Reason as _Reason
from ..Types import DiscordUser
from .commands import Cases, CaseInfo, CaseClaim, CaseDelete, Reason



class CasesPlugin(PluginBlueprint):
    def __init__(self, bot):
        super().__init__(bot)


    @commands.command()
    @commands.has_guild_permissions(kick_members=True)
    async def cases(
        self,
        ctx,
        user: DiscordUser = None
    ):
        """cases_help"""
        await Cases.run(self, ctx, user)


    @commands.group()
    @commands.has_guild_permissions(kick_members=True)
    async def case(
        self,
        ctx
    ):
        """case_help"""
        if ctx.subcommand_passed is None:
            _help = self.bot.get_command("help")
            await _help.__call__(ctx, query="case")


    @case.command()
    @commands.has_guild_permissions(kick_members=True)
    async def info(
        self,
        ctx,
        case
    ):
        """case_info_help"""
        await CaseInfo.run(self, ctx, case)


    @case.command()
    @commands.has_guild_permissions(kick_members=True)
    async def claim(
        self,
        ctx,
        case
    ):
        """case_claim_help"""
        await CaseClaim.run(self, ctx, case)


    @case.command()
    @commands.has_guild_permissions(administrator=True)
    async def delete(
        self,
        ctx,
        case
    ):
        """case_delete_help"""
        await CaseDelete.run(self, ctx, case)


    @commands.command()
    @commands.has_guild_permissions(kick_members=True)
    async def reason(
        self,
        ctx,
        case: Optional[int],
        *,
        reason: _Reason
    ):
        """reason_help"""
        await Reason.run(self, ctx, case, reason)



def setup(bot):
    pass