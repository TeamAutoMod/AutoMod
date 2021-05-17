import discord
from discord.ext import commands

from ..PluginBlueprint import PluginBlueprint
from .commands import Help, Add, Remove, SetupAdd, SetupRemove



class SelfrolesPlugin(PluginBlueprint):
    def __init__(self, bot):
        super().__init__(bot)

    
    @commands.group()
    async def role(
        self, 
        ctx,
    ):
        """role_help"""
        if ctx.subcommand_passed is None:
            return


    @role.command()
    async def add(
        self, 
        ctx,
        role: str
    ):
        """role_add_help"""
        await Add.run(self, ctx, role)


    @role.command()
    async def remove(
        self, 
        ctx,
        role: str
    ):
        """role_remove_help"""
        await Remove.run(self, ctx, role)
    

    @role.command()
    async def help(
        self, 
        ctx
    ):
        """role_help_help"""
        await Help.run(self, ctx)


    @role.group()
    @commands.has_permissions(administrator=True)
    async def setup(
        self, 
        ctx
    ):
        """role_setup_help"""
        if ctx.subcommand_passed is None:
            _help = self.bot.get_command("help")
            await _help.__call__(ctx, query="role setup")


    @setup.command(name="add")
    @commands.has_permissions(administrator=True)
    async def _add(
        self, 
        ctx,
        name: str,
        role: discord.Role
    ):
        """role_setup_add_help"""
        await SetupAdd.run(self, ctx, name, role)


    @setup.command(name="remove")
    @commands.has_permissions(administrator=True)
    async def _remove(
        self, 
        ctx,
        name: str
    ):
        """role_setup_remove_help"""
        await SetupRemove.run(self, ctx, name)


    


def setup(bot):
    pass