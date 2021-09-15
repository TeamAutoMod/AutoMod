import discord
from discord.ext import commands

from ..PluginBlueprint import PluginBlueprint
from ..Types import Embed
from .sub.Utils import get_stars_for_message, delete_or_edit, build_embed, edit_or_send
from ...utils.Views import ConfirmView


class StarboardPlugin(PluginBlueprint):
    def __init__(self, bot):
        super().__init__(bot)


    @commands.Cog.listener()
    async def on_raw_reaction_add(
        self,
        payload: discord.RawReactionActionEvent
    ):
        if str(payload.emoji) != "⭐":
            return

        if payload.guild_id == None:
            return
        guild = self.bot.get_guild(payload.guild_id)
        if guild is None:
            return

        if str(payload.user_id) == str(self.bot.user.id):
            return

        config = self.db.configs.get(f"{payload.guild_id}", "starboard")
        if config["enabled"] == False or config["channel"] == "":
            return

        if payload.channel_id in config["ignored_channels"]:
            return

        starboard_channel = await self.bot.utils.getChannel(guild, int(config["channel"]))
        if starboard_channel == None:
            return

        current_channel = await self.bot.utils.getChannel(guild, payload.channel_id)
        if current_channel == None:
            return

        if str(starboard_channel.id) == str(current_channel.id):
            return

        message = await current_channel.fetch_message(payload.message_id)
        if message == None or str(message.author.id) == str(payload.user_id) or message.author.bot == True:
            return

        stars, new = get_stars_for_message(self, message)
        embed, content = build_embed(message, stars)

        await edit_or_send(self, new, message, starboard_channel, content, embed)


    @commands.Cog.listener()
    async def on_raw_reaction_remove(
        self,
        payload: discord.RawReactionActionEvent
    ):
        if str(payload.emoji) != "⭐":
            return

        if payload.guild_id == None:
            return
        guild = self.bot.get_guild(payload.guild_id)
        if guild is None:
            return

        if str(payload.user_id) == str(self.bot.user.id):
            return

        config = self.db.configs.get(f"{payload.guild_id}", "starboard")
        if config["enabled"] == False or config["channel"] == "":
            return

        if payload.channel_id in config["ignored_channels"]:
            return

        starboard_channel = await self.bot.utils.getChannel(guild, int(config["channel"]))
        if starboard_channel == None:
            return

        current_channel = await self.bot.utils.getChannel(guild, payload.channel_id)
        if current_channel == None:
            return

        if str(starboard_channel.id) == str(current_channel.id):
            return

        message = await current_channel.fetch_message(payload.message_id)
        if message == None or str(message.author.id) == str(payload.user_id) or message.author.bot == True:
            return

        if not self.db.stars.exists(f"{message.id}"):
            return

        await delete_or_edit(self, message, starboard_channel)


    @commands.group(aliases=["sb"])
    @commands.has_permissions(ban_members=True)
    async def starboard(
        self,
        ctx
    ):
        """starboard_help"""
        if ctx.invoked_subcommand is None:
            message = None
            async def confirm(interaction):
                config = self.db.configs.get(f"{ctx.guild.id}", "starboard")
                config["enabled"] = not config["enabled"]
                self.db.configs.update(f"{ctx.guild.id}", "starboard", config)
                if config["enabled"] == False:
                    key = "disabled_starboard"
                else:
                    key = "enabled_starboard"
                await interaction.response.edit_message(content=self.i18next.t(ctx.guild, key, _emote="YES"), embed=None, view=None)
                


            async def cancel(interaction):
                e = Embed(
                    description=self.i18next.t(ctx.guild, "aborting")
                )
                await interaction.response.edit_message(embed=e, view=None)

            async def timeout():
                if message is not None:
                    e = Embed(
                        description=self.i18next.t(ctx.guild, "aborting")
                    )
                    await message.edit(embed=e, view=None)

            def check(interaction):
                return interaction.user.id == ctx.author.id and interaction.message.id == message.id

            config = self.db.configs.get(f"{ctx.guild.id}", "starboard")
            if config["enabled"] == False:
                key = "starboard_disabled"
            else:
                key = "starboard_enabled"
            e = Embed(
                description=self.i18next.t(ctx.guild, key)
            )
            message = await ctx.send(
                embed=e,
                view=ConfirmView(
                    ctx.guild.id, 
                    on_confirm=confirm, 
                    on_cancel=cancel, 
                    on_timeout=timeout,
                    check=check
                )
            )



    @starboard.command()
    @commands.has_permissions(ban_members=True)
    async def channel(
        self,
        ctx,
        channel: discord.TextChannel
    ):
        """starboard_channel_help"""
        config = self.db.configs.get(f"{ctx.guild.id}", "starboard")
        if config["enabled"] == False:
            return await ctx.send(self.i18next.t(ctx.guild, "starboard_is_disabled", _emote="NO", prefix=self.bot.get_guild_prefix(ctx.guild)))
        
        config["channel"] = f"{channel.id}"
        self.db.configs.update(f"{ctx.guild.id}", "starboard", config)
        await ctx.send(self.i18next.t(ctx.guild, "set_starboard_channel", _emote="YES", channel=channel.mention))



def setup(bot):
    pass