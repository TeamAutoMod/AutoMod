import discord
from discord.ext import commands
from discord import PermissionOverwrite

from typing import Union

from ..PluginBlueprint import PluginBlueprint
from ..Types import Embed
from ...utils.Views import ConfirmView



async def overwrite(plugin, ctx, msg, roles):
    for k, v in roles.items():
        role = v["role"]
        try:
            for c in ctx.guild.categories:
                ov = c.overwrites
                ov.update({
                    role: v["perms"]
                })
                await c.edit(overwrites=ov)
        except Exception as ex:
            return await msg.edit(content=plugin.i18next.t(ctx.guild, "category_fail", _emote="NO", category=c.name, exc=ex))
        else:
            plugin.db.configs.update(ctx.guild.id, k, f"{role.id}")
    await msg.edit(content=f"{msg.content} \n{plugin.emotes.get('YES')} Category overwrites complete!")

    for k, v in roles.items():
        role = v["role"]
        try:
            for c in ctx.guild.text_channels:
                ov = c.overwrites
                ov.update({
                    role: v["perms"]
                })
                await c.edit(overwrites=ov)
        except Exception as ex:
            return await msg.edit(content=plugin.i18next.t(ctx.guild, "text_fail", _emote="NO", channel=c.name, exc=ex))
        else:
            plugin.db.configs.update(ctx.guild.id, k, f"{role.id}")
    await msg.edit(content=f"{msg.content} \n{plugin.emotes.get('YES')} Text channel overwrites complete!")

    await msg.edit(content=plugin.i18next.t(ctx.guild, "restrict_done", _emote="YES"))


class ConfigPlugin(PluginBlueprint):
    def __init__(self, bot):
        super().__init__(bot)


    async def cog_check(self, ctx):
        return ctx.author.guild_permissions.administrator


    @commands.group()
    async def setup(
        self,
        ctx
    ):
        """setup_help"""
        prefix = self.bot.get_guild_prefix(ctx.guild)
        e = Embed(
            title="Setup commands",
            description=self.i18next.t(ctx.guild, "setup_description")
        )
        e.add_field(
            name="❯ Mute role",
            value=f"``{prefix}setup muted``"
        )
        e.add_field(
            name="❯ Automoderator",
            value=f"``{prefix}setup automod``"
        )
        e.add_field(
            name="❯ Restrict roles",
            value=f"``{prefix}setup restrict``"
        )
        await ctx.send(embed=e)
    


    @setup.command()
    async def muted(
        self, 
        ctx
    ):
        """setup_muted_help"""
        role_id = self.db.configs.get(ctx.guild.id, "mute_role")
        if role_id == "":
            text = self.i18next.t(ctx.guild, "setup_muted_description_1")
        else:
            text = self.i18next.t(ctx.guild, "setup_muted_description_2")

        message = None
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

        async def confirm(interaction):
            await interaction.response.edit_message(
                content=self.i18next.t(ctx.guild, "start_mute", _emote="WAIT"), 
                embed=None, 
                view=None
            )
            msg = interaction.message

            global role
            if role_id != "":
                role = await self.bot.utils.getRole(ctx.guild, int(role_id))
            else:
                try:
                    role = await ctx.guild.create_role(name="Muted")
                except Exception as ex:
                    return await msg.edit(content=self.i18next.t(ctx.guild, "role_fail", _emote="NO", exc=ex))

            await msg.edit(content=f"{msg.content} \n{self.emotes.get('YES')} Role initialized!")
            try:
                for c in ctx.guild.categories:
                    ov = c.overwrites
                    ov.update({
                        role: discord.PermissionOverwrite(send_messages=False)
                    })
                    await c.edit(overwrites=ov)
            except Exception as ex:
                return await msg.edit(content=self.i18next.t(ctx.guild, "category_fail", _emote="NO", category=c.name, exc=ex))
            
            await msg.edit(content=f"{msg.content} \n{self.emotes.get('YES')} Category overwrites complete!")
            try:
                for c in ctx.guild.text_channels:
                    ov = c.overwrites
                    ov.update({
                        role: discord.PermissionOverwrite(send_messages=False)
                    })
                    await c.edit(overwrites=ov)
            except Exception as ex:
                return await msg.edit(content=self.i18next.t(ctx.guild, "text_fail", _emote="NO", channel=c.name, exc=ex))

            await msg.edit(content=f"{msg.content} \n{self.emotes.get('YES')} Text channel overwrites complete!")
            try:
                for c in ctx.guild.voice_channels:
                    ov = c.overwrites
                    ov.update({
                        role: discord.PermissionOverwrite(send_messages=False)
                    })
                    await c.edit(overwrites=ov)
            except Exception as ex:
                return await msg.edit(content=self.i18next.t(ctx.guild, "voice_fail", _emote="NO", channel=c.name, exc=ex))

            await msg.edit(content=f"{msg.content} \n{self.emotes.get('YES')} Voice channel overwrites complete!")
            if role_id == "":
                self.db.configs.update(ctx.guild.id, "mute_role", f"{role.id}")
            await msg.edit(content=self.i18next.t(ctx.guild, "mute_done", _emote="YES"))
        
        e = Embed(
            title="Muted role setup",
            description=text
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


    @setup.command()
    async def automod(
        self, 
        ctx
    ):
        """setup_automod_help"""
        message = None
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

        async def confirm(interaction):
            await interaction.response.edit_message(
                content=self.i18next.t(ctx.guild, "start_automod", _emote="WAIT"), 
                embed=None, 
                view=None
            )
            msg = interaction.message

            punishments = self.db.configs.get(ctx.guild.id, "punishments")
            if not "5" in punishments:
                punishments.update({
                    "5": "kick"
                })
            
            automod = {
                "invites": {"warns": 1},
                "everyone": {"warns": 1},

                "mention": {"threshold": 10},
                "lines": {"threshold": 15},

                "raid": {"status": False, "threshold": ""},

                "caps": {"warns": 1},
                "files": {"warns": 1},
                "zalgo": {"warns": 1},
                "censor": {"warns": 1},
                "spam": {"status": True, "warns": 3}
            }

            self.db.configs.update(ctx.guild.id, "punishments", punishments)
            self.db.configs.update(ctx.guild.id, "automod", automod)

            prefix = self.bot.get_guild_prefix(ctx.guild)
            e = Embed()
            e.add_field(
                name="❯ Configured",
                value=self.i18next.t(ctx.guild, "automod_basic")
            )
            e.add_field(
                name="❯ View Config",
                value=f"``{prefix}config``"
            )
            await msg.edit(content=self.i18next.t(ctx.guild, "automod_done", _emote="YES", prefix=prefix), embed=e)

        
        e = Embed(
            title="Automoderator setup",
            description=self.i18next.t(ctx.guild, "setup_automod_description")
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


    @setup.command()
    async def restrict(
        self,
        ctx
    ):
        """setup_restrict_help"""
        message = None
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

        async def confirm(interaction):
            await interaction.response.edit_message(
                content=self.i18next.t(ctx.guild, "start_restrict", _emote="WAIT"), 
                embed=None, 
                view=None
            )
            msg = interaction.message


            global embed_role
            embed_role_id = self.db.configs.get(ctx.guild.id, "embed_role")
            if embed_role_id != "":
                embed_role = await self.bot.utils.getRole(ctx.guild, int(embed_role_id))
            else:
                try:
                    embed_role = await ctx.guild.create_role(name="Embed restricted")
                except Exception as ex:
                    return await msg.edit(content=self.i18next.t(ctx.guild, "role_fail2", _emote="NO", role="Embed restricted", exc=ex))


            global emoji_role
            emoji_role_id = self.db.configs.get(ctx.guild.id, "emoji_role")
            if emoji_role_id != "":
                emoji_role = await self.bot.utils.getRole(ctx.guild, int(emoji_role_id))
            else:
                try:
                    emoji_role = await ctx.guild.create_role(name="Emoji restricted")
                except Exception as ex:
                    return await msg.edit(content=self.i18next.t(ctx.guild, "role_fail2", _emote="NO", role="Emoji restricted", exc=ex))


            global tag_role
            tag_role_id = self.db.configs.get(ctx.guild.id, "tag_role")
            if tag_role_id != "":
                tag_role = await self.bot.utils.getRole(ctx.guild, int(tag_role_id))
            else:
                try:
                    tag_role = await ctx.guild.create_role(name="Tag restricted")
                except Exception as ex:
                    return await msg.edit(content=self.i18next.t(ctx.guild, "role_fail2", _emote="NO", role="Tag restricted", exc=ex))
                else:
                    self.db.configs.update(ctx.guild.id, "tag_role", f"{tag_role.id}")


            await msg.edit(content=f"{msg.content} \n{self.emotes.get('YES')} Roles initialized!")
            await overwrite(
                self, 
                ctx, 
                msg, 
                {
                    "embed_role": {"role": embed_role, "perms": PermissionOverwrite(embed_links=False, attach_files=False)}, 
                    "emoji_role": {"role": emoji_role, "perms": PermissionOverwrite(external_emojis=False)}
                }
            )

        e = Embed(
            title="Restrict roles setup",
            description=self.i18next.t(ctx.guild, "setup_restrict_description")
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

    
    @commands.command()
    async def prefix(
        self,
        ctx,
        prefix: str
    ):
        """prefix_help"""
        current = self.bot.get_guild_prefix(ctx.guild)
        if prefix is None:
            return await ctx.send(self.i18next.t(ctx.guild, "current_prefix", prefix=current))

        if prefix == current:
            return await ctx.send(self.i18next.t(ctx.guild, "already_is_prefix", _emote="WARN"))
        
        if len(prefix) > 10:
            return await ctx.send(self.i18next.t(ctx.guild, "prefix_too_long", _emote="NO"))

        self.db.configs.update(ctx.guild.id, "prefix", prefix)
        await ctx.send(self.i18next.t(ctx.guild, "prefix_updated", _emote="YES", prefix=prefix))


    @commands.command()
    async def config(
        self, 
        ctx
    ):
        """config_help"""
        if ctx.subcommand_passed is None:
            cfg = self.db.configs.get_doc(ctx.guild.id)

        e = Embed(
            title="Server configuration",
            description="This shows all of the current server and automoderator configurations."
        )
        if ctx.guild.icon != None:
            e.set_thumbnail(url=ctx.guild.icon.url)
        e.add_field(
            name="Prefix",
            value=f"``{cfg['prefix']}``",
            inline=True
        )
        e.add_field(
            name="Mute Role",
            value=f"<@&{cfg['mute_role']}>" if cfg['mute_role'] != "" else "``❌``",
            inline=True
        )
        e.add_field(
            name="Mod Log",
            value=f"<#{cfg['mod_log']}>" if cfg['mod_log'] != "" else "``❌``",
            inline=True
        )
        e.add_field(
            name="Message Log",
            value=f"<#{cfg['message_log']}>" if cfg['message_log'] != "" else "``❌``",
            inline=True
        )
        e.add_field(
            name="Server Log",
            value=f"<#{cfg['server_log']}>" if cfg['server_log'] != "" else "``❌``",
            inline=True
        )
        e.add_field(
            name="Voice Log",
            value=f"<#{cfg['voice_log']}>" if cfg['voice_log'] != "" else "``❌``",
            inline=True
        )
        # e.add_field(
        #     name="Persist Mode",
        #     value=f"``✅``" if cfg['persist'] is True else "``❌``",
        #     inline=True
        # )
        e.add_field(
            name="Starboard",
            value=f"``✅``" if cfg['starboard']['enabled'] is True else "``❌``",
            inline=True
        )
        e.add_field(
            name="DM on actions",
            value=f"``✅``" if cfg['dm_on_actions'] is True else "``❌``",
            inline=True
        )
        e.add_field(
            name="Show mod in DM",
            value=f"``✅``" if cfg['show_mod_in_dm'] is True else "``❌``",
            inline=True
        )
        
        am = cfg['automod']
        e.add_field(
            name="Max Mentions", 
            value=f"``{am['mention']['threshold']} mentions``" if "mention" in am else "``❌``", 
            inline=True
        )
        e.add_field(
            name="Anti Caps", 
            value=f"``{am['caps']['warns']} {'warn' if int(am['caps']['warns']) == 1 else 'warns'}``" if 'caps' in am else "``❌``", 
            inline=True
        )
        e.add_field(
            name="Anti @ever1", 
            value=f"``{am['everyone']['warns']} {'warn' if int(am['everyone']['warns']) == 1 else 'warns'}``" if 'everyone' in am else "``❌``", 
            inline=True
        )
        e.add_field(
            name="Anti Invites", 
            value=f"``{am['invites']['warns']} {'warn' if int(am['invites']['warns']) == 1 else 'warns'}``" if "invites" in am else "``❌``", 
            inline=True
        )
        e.add_field(
            name="Anti Spam", 
            value=f"``{am['spam']['warns']} {'warn' if int(am['spam']['warns']) == 1 else 'warns'}``" if "spam" in am else "``❌``", 
            inline=True
        )
        e.add_field(
            name="Anti Raid", 
            value=f"``{am['raid']['threshold'].split('/')[0]}``/``{am['raid']['threshold'].split('/')[1]}``" if "raid" in am and am['raid']['status'] is True else "``❌``", 
            inline=True
        )
        e.add_field(
            name="Bad Files", 
            value=f"``{am['files']['warns']} {'warn' if int(am['files']['warns']) == 1 else 'warns'}``" if "files" in am else "``❌``", 
            inline=True
        )
        e.add_field(
            name="Max Newlines", 
            value=f"``{am['lines']['threshold']} lines``" if "files" in am else "``❌``", 
            inline=True
        )
        e.add_field(
            name="Anti Zalgo", 
            value=f"``{am['zalgo']['warns']} {'warn' if int(am['zalgo']['warns']) == 1 else 'warns'}``" if "files" in am else "``❌``", 
            inline=True
        )

        punishments = [f"``{x} ({y.capitalize() if len(y.split(' ')) == 1 else y.split(' ')[0].capitalize() + ' ' + y.split(' ')[-2] + y.split(' ')[-1]})``" for x, y in cfg["punishments"].items()]
        punishments = sorted(punishments, key=lambda i: int(i.split(" ")[0].replace("``", "")))
        e.add_field(
            name="Punishments",
            value="{}".format(" | ".join(punishments) if len(punishments) > 0 else "``❌``"),
            inline=False
        )

        filters = self.db.configs.get(ctx.guild.id, "filters")
        e.add_field(
            name=f"Filters",
            value=" | ".join([f"``{x}``" for x in filters]) if len(filters) > 0 else "``❌``",
            inline=False
        )
        
        await ctx.send(embed=e)


    @commands.command()
    async def modlog(
        self,
        ctx,
        channel: Union[discord.TextChannel, str]
    ):
        """modlog_help"""
        if isinstance(channel, str):
            if channel.lower() == "off":
                self.db.configs.update(ctx.guild.id, "mod_log", "")
                return await ctx.send(self.i18next.t(ctx.guild, "log_off", _emote="YES", opt="Moderation Logs"))
            else:
                return await ctx.send(self.i18next.t(ctx.guild, "invalid_channel", _emote="NO"))
        
        self.db.configs.update(ctx.guild.id, "mod_log", f"{channel.id}")
        await ctx.send(self.i18next.t(ctx.guild, "log_on", _emote="YES", opt="Moderation Logs", channel=channel.mention))


    @commands.command()
    async def voicelog(
        self,
        ctx,
        channel: Union[discord.TextChannel, str]
    ):
        """voicelog_help"""
        if isinstance(channel, str):
            if channel.lower() == "off":
                self.db.configs.update(ctx.guild.id, "voice_log", "")
                self.db.configs.update(ctx.guild.id, "voice_logging", False)
                return await ctx.send(self.i18next.t(ctx.guild, "log_off", _emote="YES", opt="Voice Logs"))
            else:
                return await ctx.send(self.i18next.t(ctx.guild, "invalid_channel", _emote="NO"))
        
        self.db.configs.update(ctx.guild.id, "voice_log", f"{channel.id}")
        self.db.configs.update(ctx.guild.id, "voice_logging", True)
        await ctx.send(self.i18next.t(ctx.guild, "log_on", _emote="YES", opt="Voice Logs", channel=channel.mention))


    @commands.command()
    async def serverlog(
        self,
        ctx,
        channel: Union[discord.TextChannel, str]
    ):
        """serverlog_help"""
        if isinstance(channel, str):
            if channel.lower() == "off":
                self.db.configs.update(ctx.guild.id, "server_logging", True)
                self.db.configs.update(ctx.guild.id, "server_log", "")
                return await ctx.send(self.i18next.t(ctx.guild, "log_off", _emote="YES", opt="Server Logs"))
            else:
                return await ctx.send(self.i18next.t(ctx.guild, "invalid_channel", _emote="NO"))
        
        self.db.configs.update(ctx.guild.id, "server_logging", True)
        self.db.configs.update(ctx.guild.id, "server_log", f"{channel.id}")
        await ctx.send(self.i18next.t(ctx.guild, "log_on", _emote="YES", opt="Server Logs", channel=channel.mention))

    
    @commands.command()
    async def messagelog(
        self,
        ctx,
        channel: Union[discord.TextChannel, str]
    ):
        """messagelog_help"""
        if isinstance(channel, str):
            if channel.lower() == "off":
                self.db.configs.update(ctx.guild.id, "message_logging", False)
                self.db.configs.update(ctx.guild.id, "message_log", "")
                return await ctx.send(self.i18next.t(ctx.guild, "log_off", _emote="YES", opt="Message Logs"))
            else:
                return await ctx.send(self.i18next.t(ctx.guild, "invalid_channel", _emote="NO"))
        
        self.db.configs.update(ctx.guild.id, "message_logging", True)
        self.db.configs.update(ctx.guild.id, "message_log", f"{channel.id}")
        await ctx.send(self.i18next.t(ctx.guild, "log_on", _emote="YES", opt="Message Logs", channel=channel.mention))


    @commands.command()
    async def dm_on_actions(
        self,
        ctx
    ):
        """dm_on_actions_help"""
        state = self.db.configs.get(ctx.guild.id, "dm_on_actions")
        state = not state
        self.db.configs.update(ctx.guild.id, "dm_on_actions", state)
        if state is False:
            return await ctx.send(self.i18next.t(ctx.guild, "dm_on_actions_false", _emote="YES"))
        else:
            return await ctx.send(self.i18next.t(ctx.guild, "dm_on_actions_true", _emote="YES"))


    @commands.command()
    async def show_mod_in_dm(
        self,
        ctx
    ):
        """show_mod_in_dm_help"""
        state = self.db.configs.get(ctx.guild.id, "show_mod_in_dm")
        state = not state
        self.db.configs.update(ctx.guild.id, "show_mod_in_dm", state)
        if state is False:
            return await ctx.send(self.i18next.t(ctx.guild, "show_mod_in_dm_false", _emote="YES"))
        else:
            return await ctx.send(self.i18next.t(ctx.guild, "show_mod_in_dm_true", _emote="YES"))


    @commands.command()
    async def persist(
        self,
        ctx
    ):
        """persist_help"""
        state = self.db.configs.get(ctx.guild.id, "persist")
        state = not state
        self.db.configs.update(ctx.guild.id, "persist", state)
        if state is False:
            return await ctx.send(self.i18next.t(ctx.guild, "persist_False", _emote="YES"))
        else:
            return await ctx.send(self.i18next.t(ctx.guild, "persist_true", _emote="YES"))



def setup(bot):
    pass