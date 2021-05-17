import discord
from discord.ext import commands

from ..PluginBlueprint import PluginBlueprint
from .commands import ActionLog, Prefix, \
EnableAutomod, EnableAntispam, EnablePersist, EnableMessageLogging, EnableWelcomeLogging, EnableVoiceLogging, \
DisableAutomod, DisableAntispam, DisablePersist, DisableMessageLogging, DisableWelcomeLogging, DisableVoiceLogging, \
InviteCensor, WordCensor, FileCensor, ZalgoCensor, CapsCensor, SpamDetection, MentionSpam, MaxWarns, \
DMOnActions, AllowedInvites, AddAllowedInvite, RemoveAllowedInvite, \
BlackList, AddToBlackList, RemoveFromBlackList
from .utils import EnableOptions, DisableOptions,PunishmentOptions



class ConfigPlugin(PluginBlueprint):
    def __init__(self, bot):
        super().__init__(bot)

    
    async def cog_check(self, ctx):
        return ctx.author.guild_permissions.administrator


    @commands.group(aliases=["cfg", "configure"])
    async def config(
        self,
        ctx
    ):
        "config_help"
        if ctx.subcommand_passed is None:
            cmd = self.bot.get_command("help")
            await cmd.__call__(ctx, query="config")


    @config.command()
    async def action_log(
        self,
        ctx,
        channel: discord.TextChannel
    ):
        """config_action_log_help"""
        await ActionLog.run(self, ctx, channel)


    @config.command()
    async def prefix(
        self,
        ctx,
        prefix: str = None
    ):
        """config_prefix_help"""
        await Prefix.run(self, ctx, prefix)


    @config.command()
    async def dm_on_actions(
        self,
        ctx
    ):
        """dm_on_actions_help"""
        await DMOnActions.run(self, ctx)

    

    @config.group(aliases=["whitelisted_invites"])
    async def allowed_invites(
        self,
        ctx
    ):
        """allowed_invites_help"""
        if ctx.subcommand_passed is None:
            await AllowedInvites.run(self, ctx)


    @allowed_invites.command(name="add")
    async def add_invite(
        self,
        ctx,
        server: int
    ):
        """allowed_invites_add_help"""
        await AddAllowedInvite.run(self, ctx, server)


    @allowed_invites.command(name="remove")
    async def remove_invite(
        self,
        ctx,
        server: int
    ):
        """allowed_invites_remove_help"""
        await RemoveAllowedInvite.run(self, ctx, server)



    @config.group(aliases=["censor_list"])
    async def black_list(
        self,
        ctx
    ):
        if ctx.subcommand_passed is None:
            """black_list_help"""
            await BlackList.run(self, ctx)


    @black_list.command(name="add")
    async def add_to_black_list(
        self,
        ctx, 
        *,
        text: str
    ):
        """black_list_add_help"""
        await AddToBlackList.run(self, ctx, text)


    @black_list.command(name="remove")
    async def remove_from_black_list(
        self,
        ctx, 
        *,
        text: str
    ):
        """black_list_add_help"""
        await RemoveFromBlackList.run(self, ctx, text)


    
    @config.group(aliases=["punishments"])
    async def punishment(
        self,
        ctx
    ):
        """black_list_remove_help"""
        if ctx.subcommand_passed is None:
            await PunishmentOptions.run(self, ctx)


    @punishment.command()
    async def invite_censor(
        self,
        ctx
    ):
        """config_punsishment_invite_censor_help"""
        await InviteCensor.run(self, ctx)


    @punishment.command()
    async def word_censor(
        self,
        ctx
    ):
        """config_punsishment_word_censor_help"""
        await WordCensor.run(self, ctx)

    @punishment.command()
    async def file_censor(
        self,
        ctx
    ):
        """config_punsishment_file_censor_help"""
        await FileCensor.run(self, ctx)


    @punishment.command()
    async def zalgo_censor(
        self,
        ctx
    ):
        """config_punsishment_zalgo_censor_help"""
        await ZalgoCensor.run(self, ctx)


    @punishment.command()
    async def caps_censor(
        self,
        ctx
    ):
        """config_punsishment_caps_censor_help"""
        await CapsCensor.run(self, ctx)


    @punishment.command()
    async def spam_detection(
        self,
        ctx
    ):
        """config_punsishment_spam_detection_help"""
        await SpamDetection.run(self, ctx)


    @punishment.command()
    async def mention_spam(
        self,
        ctx
    ):
        """config_punsishment_mention_spam_help"""
        await MentionSpam.run(self, ctx)


    @punishment.command()
    async def max_warns(
        self,
        ctx
    ):
        """config_punsishment_max_warns_help"""
        await MaxWarns.run(self, ctx)



    @config.group()
    async def enable(
        self,
        ctx
    ):
        """enable_help"""
        if ctx.subcommand_passed is None:
            await EnableOptions.run(self, ctx)


    @enable.command()
    async def automod(
        self,
        ctx
    ):
        """automod_help"""
        await EnableAutomod.run(self, ctx)


    @enable.command()
    async def antispam(
        self,
        ctx
    ):
        """antispam_help"""
        await EnableAntispam.run(self, ctx)


    @enable.command()
    async def persist(
        self,
        ctx
    ):
        """persist_help"""
        await EnablePersist.run(self, ctx)


    @enable.command()
    async def message_logging(
        self,
        ctx,
        channel: discord.TextChannel
    ):
        """message_logging_help"""
        await EnableMessageLogging.run(self, ctx, channel)


    @enable.command()
    async def welcome_logging(
        self,
        ctx,
        channel: discord.TextChannel
    ):
        """member_logging_help"""
        await EnableWelcomeLogging.run(self, ctx, channel)


    @enable.command()
    async def voice_logging(
        self,
        ctx,
        channel: discord.TextChannel
    ):
        """voice_logging_help"""
        await EnableVoiceLogging.run(self, ctx, channel)


    
    @config.group()
    async def disable(
        self,
        ctx
    ):
        """disable_help"""
        if ctx.subcommand_passed is None:
            await DisableOptions.run(self, ctx)


    @disable.command(name="automod")
    async def _automod(
        self,
        ctx
    ):
        """automod_help"""
        await DisableAutomod.run(self, ctx)


    @disable.command(name="antispam")
    async def _antispam(
        self,
        ctx
    ):
        """antispam_help"""
        await DisableAntispam.run(self, ctx)

    
    @disable.command(name="persist")
    async def _antispam(
        self,
        ctx
    ):
        """persist_help"""
        await DisablePersist.run(self, ctx)


    @disable.command(name="message_logging")
    async def _message_logging(
        self,
        ctx
    ): 
        """message_logging_help"""
        await DisableMessageLogging.run(self, ctx)


    @disable.command(name="welcome_logging")
    async def _welcome_logging(
        self,
        ctx,
    ):
        """member_logging_help"""
        await DisableWelcomeLogging.run(self, ctx)


    @disable.command(name="voice_logging")
    async def _voice_logging(
        self,
        ctx
    ):
        """voice_logging_help"""
        await DisableVoiceLogging.run(self, ctx)




def setup(bot):
    pass