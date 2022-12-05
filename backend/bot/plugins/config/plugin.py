# type: ignore

import discord
from discord.ext import commands

import logging; log = logging.getLogger()
from toolbox import S as Object
from typing import Tuple, Literal
import asyncio

from .. import AutoModPluginBlueprint, ShardedBotInstance
from ...types import Embed, Duration, E
from ...views import SetupView, RoleChannelSelect, RoleSelect
from ...modals import DefaultReasonModal



LOG_OPTIONS = {
    "mod": {
        "db_field": "mod_log",
        "i18n_type": "moderation logs"
    },
    "server": {
        "db_field": "server_log",
        "i18n_type": "server logs"
    },
    "messages": {
        "db_field": "message_log",
        "i18n_type": "message logs"
    },
    "joins": {
        "db_field": "join_log",
        "i18n_type": "join & leave logs"
    },
    "members": {
        "db_field": "member_log",
        "i18n_type": "member logs"
    },
    "voice": {
        "db_field": "voice_log",
        "i18n_type": "voice logs"
    },
    "reports": {
        "db_field": "report_log",
        "i18n_type": "report logs"
    }
}


class ConfigPlugin(AutoModPluginBlueprint):
    """Plugin for all configuration commands"""
    def __init__(
        self, 
        bot: ShardedBotInstance
    ) -> None:
        super().__init__(bot)
        self._names = {
            "mod": "Moderation Logs",
            "message": "Message Logs",
            "server": "Server Logs",
            "join": "Join Logs",
            "member": "Member Logs",
            "voice": "Voice Logs",
            "report": "Report Logs"
        } 
        self.webhook_queue = []
        self.bot.loop.create_task(self.create_webhooks())


    async def create_webhooks(
        self
    ) -> None:
        while True:
            await asyncio.sleep(1)
            if len(self.webhook_queue) > 0:
                for w in self.webhook_queue:
                    self.webhook_queue.remove(w)
                    await self.create_log_webhook(
                        w["ctx"],
                        w["option"],
                        w["channel"]
                    )


    async def create_log_webhook(
        self, 
        ctx: discord.Interaction, 
        option: str, 
        channel: discord.TextChannel
    ) -> None:
        wid = self.bot.db.configs.get(ctx.guild.id, f"{option}_webhook")
        if wid != "":
            try:
                ow = await self.bot.fetch_webhook(int(wid))
            except Exception:
                pass
            else:
                await ow.delete()
            
        if ctx.guild.id in self.bot.webhook_cache:
            if self.bot.webhook_cache[ctx.guild.id][option] != None:
                try:
                    await (self.bot.webhook_cache[ctx.guild.id][option]).delete()
                except Exception:
                    pass
        
        try:
            w = await channel.create_webhook(
                name=self._names[option.split("_")[0].lower()],
                avatar=self.bot.avatar_as_bytes
            )
        except Exception:
            return
        else:
            self.bot.db.configs.update(ctx.guild.id, f"{option}_webhook", f"{w.id}")
            if not ctx.guild.id in self.bot.webhook_cache:
                self.bot.webhook_cache.update({
                    ctx.guild.id: {
                        **{
                            k: None for k in ["mod_log", "server_log", "message_log", "join_log", "member_log", "voice_log", "report_log"] if k != option
                        }, 
                        **{
                            option: w
                        }
                    }
                })
            else:
                if self.bot.webhook_cache[ctx.guild.id][option] == None:
                    self.bot.webhook_cache[ctx.guild.id][option] = w
                else:
                    if self.bot.webhook_cache[ctx.guild.id][option] != w.id:
                        self.bot.webhook_cache[ctx.guild.id][option] = w


    async def delete_webhook(
        self, 
        ctx: discord.Interaction, 
        option: str
    ) -> None:
        if ctx.guild.id in self.bot.webhook_cache:
            if self.bot.webhook_cache[ctx.guild.id][option] != None:
                try:
                    await (self.bot.webhook_cache[ctx.guild.id][option]).delete()
                except Exception:
                    pass
                else:
                    return
                finally:
                    self.bot.webhook_cache[ctx.guild.id][option] = None

        wid = self.bot.db.configs.get(ctx.guild.id, f"{option}_webhook")
        if wid != "":
            try:
                ow = await self.bot.fetch_webhook(int(wid))
            except Exception:
                pass
            else:
                await ow.delete()


    def get_ignored_roles_channels(
        self, 
        guild: discord.Guild
    ) -> Tuple[
        list, 
        list
    ]:
        roles, channels = self.db.configs.get(guild.id, "ignored_roles_log"), self.db.configs.get(guild.id, "ignored_channels_log")
        return roles, channels

    
    def parse_emote(
        self, 
        guild: discord.Guild, 
        emote: str
    ) -> str:
        if not emote.isnumeric(): 
            return emote
        else:
            emote = discord.utils.find(lambda x: x.id == int(emote), guild.emojis)
            if emote == None:
                return "❓"
            else:
                f"<:{emote.name}:{emote.id}>"


    @AutoModPluginBlueprint.listener()
    async def on_interaction(
        self,
        i: discord.Interaction
    ) -> None:
        cid = i.data.get("custom_id", "").lower()
        parts = cid.split(":")

        if len(parts) != 2: 
            if "".join(parts) == "join_role":
                role = i.guild.get_role(int(i.data.get("values", [1])[0]))
                if role == None:
                    return await i.response.edit_message(embed=E(self.locale.t(i.guild, "role_not_found", _emote="NO"), 0))

                if role.position >= i.guild.me.top_role.position: 
                    return await i.response.edit_message(embed=E(self.locale.t(i.guild, "role_too_high", _emote="NO"), 0))
                elif role.is_default() == True:
                    return await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "no_default_role", _emote="NO"), 0), ephemeral=True)
                elif role.is_assignable() == False:
                    return await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "cant_assign_role", _emote="NO"), 0), ephemeral=True)

                self.db.configs.update(i.guild.id, "join_role", f"{role.id}")
                return await i.response.edit_message(embed=E(self.locale.t(i.guild, "join_role_on", _emote="YES", role=role.name), 1))
        
        if not "log" in parts[0]: return
        
        if parts[1] == "channels":
            func = i.guild.get_channel
        else:
            func = i.guild.get_role

        inp = [func(int(r)) for r in i.data.get("values", [])]
        roles, channels = self.get_ignored_roles_channels(i.guild)
        added, removed, ignored = [], [], []
        
        if parts[0] == "log_add":
            for e in inp:
                if isinstance(e, discord.Role):
                    if not e.id in roles:
                        roles.append(e.id); added.append(e)
                    else:
                        ignored.append(e)
                elif isinstance(e, (discord.TextChannel, discord.VoiceChannel, discord.ForumChannel)):
                    if not e.id in channels:
                        channels.append(e.id); added.append(e)
                    else:
                        ignored.append(e)
        else:
            for e in inp:
                if isinstance(e, discord.Role):
                    if e.id in roles:
                        roles.remove(e.id); removed.append(e)
                    else:
                        ignored.append(e)
                elif isinstance(e, (discord.TextChannel, discord.VoiceChannel, discord.ForumChannel)):
                    if e.id in channels:
                        channels.remove(e.id); removed.append(e)
                    else:
                        ignored.append(e)
                else:
                    ignored.append(e)

        self.db.configs.multi_update(i.guild.id, {
            "ignored_roles_log": roles,
            "ignored_channels_log": channels
        })
        if parts[0] != "log_add": added = removed

        e = Embed(
            i,
            title="Updated the following roles & channels"
        )
        e.add_fields([
            {
                "name": "**__Roles__**",
                "value": "{}".format(", ".join(
                    [
                        x.mention for x in added if isinstance(x, discord.Role)
                    ]
                )) if len(
                    [
                        _ for _ in added if isinstance(_, discord.Role)
                    ]
                ) > 0 else f"{self.bot.emotes.get('NO')}"
            },
            {
                "name": "**__Channels__**",
                "value": "{}".format(", ".join(
                    [
                        x.mention for x in added if isinstance(x, (discord.TextChannel, discord.VoiceChannel, discord.ForumChannel))
                    ]
                )) if len(
                    [
                        _ for _ in added if isinstance(_, (discord.TextChannel, discord.VoiceChannel, discord.ForumChannel))
                    ]
                ) > 0 else f"{self.bot.emotes.get('NO')}"
            },
            {
                "name": "**__Ignored__**",
                "value": "{}".format(", ".join(
                    [
                        x.mention for x in ignored if x != None
                    ]
                )) if len(
                    [
                        _ for _ in ignored if _ != None
                    ]
                ) > 0 else f"{self.bot.emotes.get('NO')}"
            },
        ])

        await i.response.edit_message(embed=e)


    @discord.app_commands.command(
        name="config",
        description="🌐 Shows the current server config"
    )
    @discord.app_commands.default_permissions(manage_guild=True)
    async def config(
        self, 
        ctx: discord.Interaction
    ) -> None:
        """
        config_help
        examples:
        -config
        """
        config = Object(self.db.configs.get_doc(ctx.guild.id))
        rules = config.automod

        rrs = {k: v for k, v in config.reaction_roles.items() if self.bot.get_channel(int(v['channel'])) != None}
        role = "role"
        emote = "emote"
        tags = self.bot.get_plugin("TagsPlugin")._tags
        no, yes = self.bot.emotes.get("NO"), self.bot.emotes.get("YES")
        c = self.bot.internal_cmd_store

        mute_perm = no
        if (ctx.guild.me.guild_permissions.value & 0x10000000000) != 0x10000000000:
            if ctx.guild.me.guild_permissions.administrator == True: 
                mute_perm = yes
        else:
            mute_perm = yes

        dash_length = 34
        e = Embed(
            ctx,
            title=f"Server config for {ctx.guild.name}",
        )
        e.add_fields([
            {
                "name": "**__General__**",
                "value": "**• Prefix:** {} \n**• Premium:** {} \n**• Can mute:** {} \n**• Filters:** {} \n**• Regexes:** {} \n**• Custom Commands:** {} \n**• Join Role:** {}"\
                .format(
                    "/",
                    yes if config.premium == True else no,
                    mute_perm,
                    len(config.filters),
                    len(config.regexes),
                    len(tags.get(ctx.guild.id, {})) if ctx.guild.id in tags else 0,
                    no if config.join_role == "" else f"<@&{config.join_role}>"
                ),
                "inline": True
            },
            {
                "name": "**__Logging__**",
                "value": "**• Mod Log:** {} \n**• Message Log:** {}\n**• Server Log:** {}\n**• Join Log:** {} \n**• Member Log:** {} \n**• Voice Log:** {} \n**• Report Log:** {}"\
                .format(
                    no if config.mod_log == "" else f"<#{config.mod_log}>",
                    no if config.message_log == "" else f"<#{config.message_log}>",
                    no if config.server_log == "" else f"<#{config.server_log}>",
                    no if config.join_log == "" else f"<#{config.join_log}>",
                    no if config.member_log == "" else f"<#{config.member_log}>",
                    no if config.voice_log == "" else f"<#{config.voice_log}>",
                    no if config.report_log == "" else f"<#{config.report_log}>"
                ),
                "inline": True
            },
            e.dash_field(dash_length),
            {
                "name": "**__Automod Rules__**",
                "value": "**• Max Mentions:** {} \n**• Max Newlines:** {} \n**• Max Emotes:** {} \n**• Max Repetitions:** {} \n**• Links:** {} \n**• Invites:** {} \n**• Bad Files:** {} \n**• Zalgo:** {} \n**• CAPS:** {} \n**• Spam:** {}"\
                .format(
                    no if not hasattr(rules, "mentions") else f"{rules.mentions.threshold}",
                    no if not hasattr(rules, "lines") else f"{rules.lines.threshold}",
                    no if not hasattr(rules, "emotes") else f"{rules.emotes.threshold}",
                    no if not hasattr(rules, "repeat") else f"{rules.repeat.threshold}",
                    no if not hasattr(rules, "links") else f"{rules.links.warns} warn{'' if rules.links.warns == 1 else 's'}" if rules.links.warns > 0 else "delete message",
                    no if not hasattr(rules, "invites") else f"{rules.invites.warns} warn{'' if rules.invites.warns == 1 else 's'}" if rules.invites.warns > 0 else "delete message",
                    no if not hasattr(rules, "files") else f"{rules.files.warns} warn{'' if rules.files.warns == 1 else 's'}" if rules.files.warns > 0 else "delete message",
                    no if not hasattr(rules, "zalgo") else f"{rules.zalgo.warns} warn{'' if rules.zalgo.warns == 1 else 's'}" if rules.zalgo.warns > 0 else "delete message",
                    no if not hasattr(rules, "caps") else f"{rules.caps.warns} warn{'' if rules.caps.warns == 1 else 's'}" if rules.caps.warns > 0 else "delete message",
                    no if config.antispam.enabled == False else f"{config.antispam.rate} per {config.antispam.per} ({config.antispam.warns} warn{'' if config.antispam.warns == 1 else 's'})"
                ),
                "inline": True
            },
            {
                "name": "**__Punishments__**",
                "value": "\n".join([
                    f"**• {x} Warn{'' if int(x) == 1 else 's'}:** {y.capitalize() if len(y.split(' ')) == 1 else y.split(' ')[0].capitalize() + ' ' + y.split(' ')[-2] + y.split(' ')[-1][0]}" \
                    for x, y in dict(
                        sorted(
                            config.punishments.items(), 
                            key=lambda x: int(x[0])
                        )
                    ).items()
                ]) if len(config.punishments.items()) > 0 else f"{no}",
                "inline": True
            },
            e.dash_field(dash_length),
            {
                "name": "**__Ignored Roles (automod)__**",
                "value": f"{no}" if len(config.ignored_roles_automod) < 1 else "{}".format(", ".join([f"<@&{x}>" for x in config.ignored_roles_automod])),
                "inline": True
            },
            {
                "name": "**__Ignored Channels (automod)__**",
                "value":  f"{no}" if len(config.ignored_channels_automod) < 1 else "{}".format(", ".join([f"<#{x}>" for x in config.ignored_channels_automod])),
                "inline": True
            },
            e.dash_field(dash_length),
            {
                "name": "**__Ignored Roles (logging)__**",
                "value":  f"{no}" if len(config.ignored_roles_log) < 1 else "{}".format(", ".join([f"<@&{x}>" for x in config.ignored_roles_log])),
                "inline": True
            },
            {
                "name": "**__Ignored Channels (logging)__**",
                "value": f"{no}" if len(config.ignored_channels_log) < 1 else "{}".format(", ".join([f"<#{x}>" for x in config.ignored_channels_log])),
                "inline": True
            },
            e.dash_field(dash_length),
            {
                "name": "**__Help & Support__**",
                "value": f"Use </setup:{c.get('setup')}> or </help:{c.get('help')}> for information about setting up the bot. If you still need help, feel free to join our [support server]({self.bot.config.support_invite})",
                "inline": False
            }
        ])

        await ctx.response.send_message(embed=e)


    auto_punishments = discord.app_commands.Group(
        name="punishments",
        description="💣 Configure automatic punishments (use /setup for more info)",
        default_permissions=discord.Permissions(manage_guild=True)
    )
    @auto_punishments.command(
        name="add",
        description="💣 Creates a new automatic punishment"
    )
    @discord.app_commands.describe(
        warns="The amount of warns the punishment is being configured for",
        action="The action that should be taken",
        time="10m, 2h, 1d (the 'Mute' action requires this, while the 'Ban' option can have a duration)"
    )
    @discord.app_commands.default_permissions(manage_guild=True)
    async def add_punishment(
        self, 
        ctx: discord.Interaction, 
        warns: int, 
        action: Literal[
            "Kick",
            "Ban",
            "Mute"
        ], 
        time: str = None
    ) -> None:
        """
        punishment_add_help
        examples:
        -punishments add 3 kick
        -punishments add 4 ban
        -punishments add 2 mute 10m
        -punishments add 6 ban 7d
        """
        action = action.lower()

        if warns < 1: return await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "min_warns", _emote="NO"), 0))
        if warns > 100: return await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "max_warns", _emote="NO"), 0))

        if time != None:
            try:
                time = await Duration().convert(ctx, time)
            except Exception as ex:
                return self.error(ctx, ex)

        current = self.db.configs.get(ctx.guild.id, "punishments")
        cmd = f"</punishments list:{self.bot.internal_cmd_store.get('punishments')}>"
        text = ""

        if action != "mute":
            new = ""
            key = action
            kwargs = {
                "cmd": cmd,
                "warns": warns
            }

            if action == "ban":
                if time != None:
                    try:
                        sec = time.to_seconds(ctx)
                    except Exception as ex:
                        return self.error(ctx, ex)

                    if sec > 0:
                        new = f"ban {sec} {time.length} {time.unit}"
                        key = "tempban"
                        kwargs.update({
                            "length": time.length,
                            "unit": time.unit
                        })
                    else:
                        new = "ban"
                else:
                    new = "ban"
            else:
                new = action

            current.update({
                str(warns): new
            })
            text = self.locale.t(ctx.guild, f"set_{key}", _emote="YES", **kwargs)

        else:
            if time == None: return await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "time_needed", _emote="NO"), 0))

            try:
                sec = time.to_seconds(ctx)
            except Exception as ex:
                return self.error(ctx, ex)

            if sec > 0: 
                length, unit = time.length, time.unit
                current.update({
                    str(warns): f"mute {sec} {length} {unit}"
                })
                text = self.locale.t(ctx.guild, "set_mute", _emote="YES", warns=warns, length=length, unit=unit, cmd=cmd)
        
            else:
                return self.error(ctx, commands.BadArgument("number_too_small"))
        
        self.db.configs.update(ctx.guild.id, "punishments", current)
        await ctx.response.send_message(embed=E(text, 1))


    @auto_punishments.command(
        name="delete",
        description="💣 Deletes an automatic punishment"
    )
    @discord.app_commands.describe(
        warns="The amount of warns the punishment was set for",
    )
    @discord.app_commands.default_permissions(manage_guild=True)
    async def delete_punishment(
        self, 
        ctx: discord.Interaction, 
        warns: int, 
    ) -> None:
        """
        punishment_delete_help
        examples:
        -punishments delete 3
        """
        current = self.db.configs.get(ctx.guild.id, "punishments")
        cmd = f"</punishments list:{self.bot.internal_cmd_store.get('punishments')}>"
        if not str(warns) in [str(_) for _ in current.keys()]:
            return await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "no_punishment", _emote="NO", cmd=cmd), 0))

        current = {k: v for k, v in current.items() if str(k) != str(warns)}    
        self.db.configs.update(ctx.guild.id, "punishments", current)

        await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "set_none", _emote="YES", warns=warns, cmd=cmd), 1))


    @auto_punishments.command(
        name="list",
        description="💣 Shows all current automatic punishments"
    )
    @discord.app_commands.default_permissions(manage_guild=True)
    async def list_punishment(
        self, 
        ctx: discord.Interaction, 
    ) -> None:
        """
        punishment_list_help
        examples:
        -punishments list
        """
        current = self.db.configs.get(ctx.guild.id, "punishments")
        cmd = f"</punishments list:{self.bot.internal_cmd_store.get('punishments')}>"
        if len(current) < 1:
            return await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "no_punishments", _emote="NO", cmd=cmd), 0))
        
        e = Embed(
            ctx,
            title="Automatic Punishments",
            description="\n".join([
                f"**• {x} Warn{'' if int(x) == 1 else 's'}:** {y.capitalize() if len(y.split(' ')) == 1 else y.split(' ')[0].capitalize() + ' ' + y.split(' ')[-2] + y.split(' ')[-1][0]}" \
                for x, y in dict(
                    sorted(
                        current.items(), 
                        key=lambda x: int(x[0])
                    )
                ).items()
            ]) 
        )
        await ctx.response.send_message(embed=e)


    @discord.app_commands.command(
        name="log",
        description="🚸 Configure logging (use /setup for more info)"
    )
    @discord.app_commands.describe(
        option="Logging option you want to configure (use /setup for more info)",
        channel="Channel where actions from the log option will be sent to",
        disable="Wheter you want to disable the logging option"
    )
    @discord.app_commands.default_permissions(manage_guild=True)
    async def _log(
        self, 
        ctx: discord.Interaction, 
        option: Literal[
            "Mod",
            "Server",
            "Messages",
            "Joins & Leaves",
            "Members",
            "Voice",
            "Reports"
        ], 
        channel: discord.TextChannel = None,
        disable: Literal[
            "True"
        ] = None
    ) -> None:
        """
        log_help
        examples:
        -log mod #mod-log
        -log joins 960832535867306044
        -log server True
        """
        option = option.lower()
        if option == "joins & leaves": option = "joins"
        data = Object(LOG_OPTIONS[option])
        if disable == "True":
            self.db.configs.update(ctx.guild.id, data.db_field, "")
            await self.delete_webhook(
                ctx,
                data.db_field
            )

            return await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "log_off", _emote="YES", _type=data.i18n_type), 1))
        else:
            if channel == None:
                prefix = "/"
                e = Embed(
                    ctx,
                    description=self.locale.t(ctx.guild, "invalid_log_channel", _emote="NO", prefix=prefix, option=option)
                )
                e.add_fields([
                    {
                        "name": "**__Enable this option__**",
                        "value": f"``{prefix}log {option} #channel``"
                    },
                    {
                        "name": "**__Disable this option__**",
                        "value": f"``{prefix}log {option} disable:True``"
                    }
                ])
                return await ctx.response.send_message(embed=e)
            else:
                self.db.configs.update(ctx.guild.id, data.db_field, f"{channel.id}")
                self.webhook_queue.append({
                    "ctx": ctx,
                    "option": data.db_field,
                    "channel": channel
                })

                await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "log_on", _emote="YES", _type=data.i18n_type, channel=channel.mention), 1))


    ignore_log = discord.app_commands.Group(
        name="ignore-log",
        description="🔀 Manage ignored roles & channels for logging",
        default_permissions=discord.Permissions(manage_guild=True)
    )
    @ignore_log.command(
        name="list",
        description="🔒 Shows the current list of ignored roles & channels for logging"
    )
    @discord.app_commands.default_permissions(manage_guild=True)
    async def show(
        self, 
        ctx: discord.Interaction
    ) -> None:
        """
        ignore_log_help
        examples:
        -ignore-log list
        """
        roles, channels = self.get_ignored_roles_channels(ctx.guild)

        if (len(roles) + len(channels)) < 1:
            return await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "no_ignored_log", _emote="NO"), 0))
        else:
            e = Embed(
                ctx,
                title="Ignored roles & channels for logging"
            )
            e.add_fields([
                {
                    "name": "**__Roles__**",
                    "value": "{}".format(", ".join([f"<@&{x}>" for x in roles])) if len(roles) > 0 else "> None"
                },
                {
                    "name": "**__Channels__**",
                    "value": "{}".format(", ".join([f"<#{x}>" for x in channels])) if len(channels) > 0 else "> None"
                }
            ])

            await ctx.response.send_message(embed=e)


    @ignore_log.command(
        name="add",
        description="✅ Adds the given role and/or channel as ignored for logging"
    )
    @discord.app_commands.default_permissions(manage_guild=True)
    async def add(
        self, 
        ctx: discord.Interaction
    ) -> None:
        """
        ignore_log_add_help
        examples:
        -ignore-log add
        """
        view = RoleChannelSelect("log_add")
        await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "bypass_add"), color=2), view=view, ephemeral=True)


    @ignore_log.command(
        name="remove",
        description="❌ Removes the given role and/or channel as ignored for logging"
    )
    @discord.app_commands.default_permissions(manage_guild=True)
    async def remove(
        self, 
        ctx: discord.Interaction
    ) -> None:
        """
        ignore_log_remove_help
        examples:
        -ignore-log remove
        """
        view = RoleChannelSelect("log_remove")
        await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "bypass_remove"), color=2), view=view, ephemeral=True)


    @discord.app_commands.command(
        name="join-role",
        description="🚪 Configure the join role (role users automatically get when joining the server)"
    )
    @discord.app_commands.default_permissions(manage_roles=True)
    async def join_role(
        self,
        ctx: discord.Interaction,
        disable: Literal[
            "True",
            "False"
        ] = None
    ) -> None:
        """
        join_role_help
        examples:
        -join_role Members
        -join_role @Members
        -join_role 793880854367043614
        -join_role disable:True
        """
        if disable == "True":
            self.db.configs.update(ctx.guild.id, "join_role", "")
            await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "join_role_off", _emote="YES"), 1))
        else:
            view = RoleSelect(1, 1, "join_role")
            await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "select_role"), 2), view=view, ephemeral=True)


    @discord.app_commands.command(
        name="default-reason",
        description="📑 Configure a default reason used when none is used in commands"
    )
    @discord.app_commands.default_permissions(manage_guild=True)
    async def default_reason(
        self,
        ctx: discord.Interaction
    ) -> None:
        """
        reason_help
        examples:
        -default_reason
        """
        async def callback(
            i: discord.Interaction
        ) -> None:
            n_reason, = self.bot.extract_args(i, "reason")

            self.db.configs.update(i.guild.id, "default_reason", n_reason)
            await i.response.send_message(embed=E(self.locale.t(i.guild, "set_reason", _emote="YES"), 1))

        c_reason = self.db.configs.get(ctx.guild.id, "default_reason")
        modal = DefaultReasonModal(
            self.bot,
            "Default Reason",
            c_reason,
            callback
        )
        await ctx.response.send_modal(modal)


    @discord.app_commands.command(
        name="setup",
        description="📐 Guide for setting up the bot"
    )
    @discord.app_commands.default_permissions(manage_guild=True)
    async def setup(
        self,
        ctx: discord.Interaction
    ) -> None:
        """
        setup_help
        examples:
        -setup
        """
        embeds = self.bot.get_plugin("UtilityPlugin").get_features(ctx.guild)

        v = SetupView(self.bot, embeds)
        await ctx.response.send_message(embed=embeds[0], view=v)


async def setup(
    bot: ShardedBotInstance
) -> None: await bot.register_plugin(ConfigPlugin(bot))