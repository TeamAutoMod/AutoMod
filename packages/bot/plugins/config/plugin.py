import discord
from discord.ext import commands

import logging; log = logging.getLogger()
from toolbox import S as Object
from typing import Union, Tuple, Literal
import asyncio

from .. import AutoModPluginBlueprint, ShardedBotInstance
from ...types import Embed, Duration
from ...views import SetupView



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
        "i18n_type": "join logs"
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


PRETTY_PLUGIN_NAMES = {
    "AutoModPluginBlueprint": "Automoderator",
    "ModerationPlugin": "Moderation",
    "UtilityPlugin": "Utility",
    "CasesPlugin": "Cases",
    "TagsPlugin": "Custom Commands",
    "ReactionRolesPlugin": "Reaction Roles",
    "AutoReplyPlugin": "Auto Reply"
}


class ConfigPlugin(AutoModPluginBlueprint):
    """Plugin for all configuration commands"""
    def __init__(
        self, 
        bot: ShardedBotInstance
    ) -> None:
        super().__init__(bot)
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
                name=ctx.bot.user.name,
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


    @discord.app_commands.command(
        name="config",
        description="Shows the current server config"
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

        mute_perm = "no"
        if (ctx.guild.me.guild_permissions.value & 0x10000000000) != 0x10000000000:
            if ctx.guild.me.guild_permissions.administrator == True: 
                mute_perm = "yes"
        else:
            mute_perm = "yes"

        dash_length = 34
        e = Embed(
            ctx,
            title=f"Server config for {ctx.guild.name}",
        )
        e.add_fields([
            {
                "name": "⚙️ __**General**__",
                "value": "``▶`` **Text Prefix:** {} \n``▶`` **Can mute:** {} \n``▶`` **Filters:** {} \n``▶`` **Regexes:** {} \n``▶`` **Custom Commands:** {} \n``▶`` **Infractions:** {} \n``▶`` **Join Role:** {}"\
                .format(
                    config.prefix,
                    mute_perm,
                    len(config.filters),
                    len(config.regexes),
                    len(tags.get(ctx.guild.id, {})) if ctx.guild.id in tags else 0,
                    len(list(self.db.cases.find({"guild": str(ctx.guild_id)}))),
                    "none" if config.join_role == "" else f"<@&{config.join_role}>"
                ),
                "inline": True
            },
            {
                "name": "📁 __**Logging**__",
                "value": "``▶`` **Mod Log:** {} \n``▶`` **Message Log:** {}\n``▶`` **Server Log:** {}\n``▶`` **Join Log:** {} \n``▶`` **Member Log:** {} \n``▶`` **Voice Log:** {} \n``▶`` **Report Log:** {}"\
                .format(
                    "disabled" if config.mod_log == "" else f"<#{config.mod_log}>",
                    "disabled" if config.message_log == "" else f"<#{config.message_log}>",
                    "disabled" if config.server_log == "" else f"<#{config.server_log}>",
                    "disabled" if config.join_log == "" else f"<#{config.join_log}>",
                    "disabled" if config.member_log == "" else f"<#{config.member_log}>",
                    "disabled" if config.voice_log == "" else f"<#{config.voice_log}>",
                    "disabled" if config.report_log == "" else f"<#{config.report_log}>"
                ),
                "inline": True
            },
            e.dash_field(dash_length),
            {
                "name": "⚔️ __**Automod Rules**__",
                "value": "``▶`` **Max Mentions:** {} \n``▶`` **Max Newlines:** {} \n``▶`` **Max Emotes:** {} \n``▶`` **Max Repetitions:** {} \n``▶`` **Links:** {} \n``▶`` **Invites:** {} \n``▶`` **Bad Files:** {} \n``▶`` **Zalgo:** {}  \n``▶`` **CAPS:** {} \n``▶`` **Spam:** {}"\
                .format(
                    "disabled" if not hasattr(rules, "mentions") else f"{rules.mentions.threshold}",
                    "disabled" if not hasattr(rules, "lines") else f"{rules.lines.threshold}",
                    "disabled" if not hasattr(rules, "emotes") else f"{rules.emotes.threshold}",
                    "disabled" if not hasattr(rules, "repeat") else f"{rules.repeat.threshold}",
                    "disabled" if not hasattr(rules, "links") else f"{rules.links.warns} warn{'' if rules.links.warns == 1 else 's'}" if rules.links.warns > 0 else "delete message",
                    "disabled" if not hasattr(rules, "invites") else f"{rules.invites.warns} warn{'' if rules.invites.warns == 1 else 's'}" if rules.invites.warns > 0 else "delete message",
                    "disabled" if not hasattr(rules, "files") else f"{rules.files.warns} warn{'' if rules.files.warns == 1 else 's'}" if rules.files.warns > 0 else "delete message",
                    "disabled" if not hasattr(rules, "zalgo") else f"{rules.zalgo.warns} warn{'' if rules.zalgo.warns == 1 else 's'}" if rules.zalgo.warns > 0 else "delete message",
                    "disabled" if not hasattr(rules, "caps") else f"{rules.caps.warns} warn{'' if rules.caps.warns == 1 else 's'}" if rules.caps.warns > 0 else "delete message",
                    "disabled" if config.antispam.enabled == False else f"{config.antispam.rate} per {config.antispam.per} ({config.antispam.warns} warn{'' if config.antispam.warns == 1 else 's'})"
                ),
                "inline": True
            },
            {
                "name": "🔨 __**Punishments**__",
                "value": "\n".join([
                    f"``▶`` **{x} Warn{'' if int(x) == 1 else 's'}:** {y.capitalize() if len(y.split(' ')) == 1 else y.split(' ')[0].capitalize() + ' ' + y.split(' ')[-2] + y.split(' ')[-1][0]}" \
                    for x, y in dict(
                        sorted(
                            config.punishments.items(), 
                            key=lambda x: int(x[0])
                        )
                    ).items()
                ]) if len(config.punishments.items()) > 0 else "> None",
                "inline": True
            },
            e.dash_field(dash_length),
            {
                "name": "🔒 __**Ignored Roles (automod)**__",
                "value": "``▶`` None" if len(config.ignored_roles_automod) < 1 else "``▶`` {}".format(", ".join([f"<@&{x}>" for x in config.ignored_roles_automod])),
                "inline": True
            },
            {
                "name": "🔒 __**Ignored Channels (automod)**__",
                "value": "``▶`` None" if len(config.ignored_channels_automod) < 1 else "``▶`` {}".format(", ".join([f"<#{x}>" for x in config.ignored_channels_automod])),
                "inline": True
            },
            e.dash_field(dash_length),
            {
                "name": "🔒 __**Ignored Roles (logging)**__",
                "value": "``▶`` None" if len(config.ignored_roles_log) < 1 else "``▶`` {}".format(", ".join([f"<@&{x}>" for x in config.ignored_roles_log])),
                "inline": True
            },
            {
                "name": "🔒 __**Ignored Channels (logging)**__",
                "value": "``▶`` None" if len(config.ignored_channels_log) < 1 else "``▶`` {}".format(", ".join([f"<#{x}>" for x in config.ignored_channels_log])),
                "inline": True
            },
            e.dash_field(dash_length),
            {
                "name": "🎭 __**Reaction Roles**__",
                "value": "``▶`` None" if len(rrs) < 1 else "\n".join(
                    [
                        f"``▶`` **[Message](https://discord.com/channels/{ctx.guild.id}/{v['channel']}/{k})** {', '.join([f'``[``{self.parse_emote(ctx.guild, data[emote])} <@&{data[role]}>``]``' for data in v['pairs']])}" for k, v in rrs.items()
                    ]
                ),
                "inline": False
            }
        ])
        await ctx.response.send_message(embed=e)


    @discord.app_commands.command(
        name="punishment",
        description="Adds or removes a punishment for a specific amount of warns"
    )
    @discord.app_commands.describe(
        warns="The amount of warns the punishment is being configured for",
        action="The action that should be taken (use 'none' to remove the punishment)",
        time="10m, 2h, 1d (the 'mute' action requires this, while the 'ban' option can have a duration)"
    )
    @discord.app_commands.default_permissions(manage_guild=True)
    async def punishment(
        self, 
        ctx: discord.Interaction, 
        warns: int, 
        action: Literal[
            "kick",
            "ban",
            "mute",
            "none"
        ], 
        time: str = None
    ) -> None:
        """
        punishment_help
        examples:
        -punishment 3 kick
        -punishment 4 ban
        -punishment 2 mute 10m
        -punishment 6 ban 7d
        -punishment 5 none
        """
        action = action.lower()

        if warns < 1: return await ctx.response.send_message(self.locale.t(ctx.guild, "min_warns", _emote="NO"))
        if warns > 100: return await ctx.response.send_message(self.locale.t(ctx.guild, "max_warns", _emote="NO"))

        if time != None:
            try:
                time = await Duration().convert(ctx, time)
            except Exception as ex:
                return self.error(ctx, ex)

        current = self.db.configs.get(ctx.guild.id, "punishments")
        prefix = "/"
        text = ""

        if action == "none":
            current = {k: v for k, v in current.items() if str(k) != str(warns)}
            text = self.locale.t(ctx.guild, "set_none", _emote="YES", warns=warns, prefix=prefix)

        elif action != "mute":
            new = ""
            key = action
            kwargs = {
                "prefix": prefix,
                "warns": warns
            }

            if action == "ban":
                if time != None:
                    sec = time.to_seconds(ctx)
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
            if time == None: return await ctx.response.send_message(self.locale.t(ctx.guild, "time_needed", _emote="NO"))

            sec = time.to_seconds(ctx)
            if sec > 0: 
                length, unit = time.length, time.unit
                current.update({
                    str(warns): f"mute {sec} {length} {unit}"
                })
                text = self.locale.t(ctx.guild, "set_mute", _emote="YES", warns=warns, length=length, unit=unit, prefix=prefix)
        
            else:
                return self.error(ctx, commands.BadArgument("number_too_small"))
        
        self.db.configs.update(ctx.guild.id, "punishments", current)
        await ctx.response.send_message(text)


    @discord.app_commands.command(
        name="log",
        description="Configure logging"
    )
    @discord.app_commands.describe(
        option="The logging option you want to configure",
        channel="Channel where actions from the log option will be sent to",
        disable="Wheter you want to disable the logging option"
    )
    @discord.app_commands.default_permissions(manage_guild=True)
    async def _log(
        self, 
        ctx: discord.Interaction, 
        option: Literal[
            "mod",
            "server",
            "messages",
            "joins",
            "members",
            "voice",
            "reports"
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
        data = Object(LOG_OPTIONS[option])
        if disable == "True":
            self.db.configs.update(ctx.guild.id, data.db_field, "")
            await self.delete_webhook(
                ctx,
                data.db_field
            )

            return await ctx.response.send_message(self.locale.t(ctx.guild, "log_off", _emote="YES", _type=data.i18n_type))
        else:
            if channel == None:
                prefix = "/"
                e = Embed(
                    ctx,
                    description=self.locale.t(ctx.guild, "invalid_log_channel", _emote="NO", prefix=prefix, option=option)
                )
                e.add_fields([
                    {
                        "name": "__**Enable this option**__",
                        "value": f"``{prefix}log {option} #channel``"
                    },
                    {
                        "name": "__**Disable this option**__",
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

                await ctx.response.send_message(self.locale.t(ctx.guild, "log_on", _emote="YES", _type=data.i18n_type, channel=channel.mention))


    @discord.app_commands.command(
        name="prefix",
        description="Sets the prefix for text & custom commands"
    )
    @discord.app_commands.default_permissions(manage_guild=True)
    async def prefix(
        self, 
        ctx: discord.Interaction, 
        prefix: str
    ) -> None:
        """
        prefix_help
        examples:
        -prefix !
        """
        if len(prefix) > 20: 
            return await ctx.response.send_message(self.locale.t(ctx.guild, "prefix_too_long", _emote="NO"))

        self.db.configs.update(ctx.guild.id, "prefix", prefix)
        await ctx.response.send_message(self.locale.t(ctx.guild, "prefix_updated", _emote="YES", prefix=prefix))


    ignore_log = discord.app_commands.Group(
        name="ignore_log",
        description="Manage ignored roles & channels for logging",
        default_permissions=discord.Permissions(manage_guild=True)
    )
    @ignore_log.command(
        name="show",
        description="Shows the current list of ignored roles & channels for logging"
    )
    @discord.app_commands.default_permissions(manage_guild=True)
    async def show(
        self, 
        ctx: discord.Interaction
    ) -> None:
        """
        ignore_log_help
        examples:
        -ignore_log show
        """
        roles, channels = self.get_ignored_roles_channels(ctx.guild)

        if (len(roles) + len(channels)) < 1:
            return await ctx.response.send_message(self.locale.t(ctx.guild, "no_ignored_log", _emote="NO"))
        else:
            e = Embed(
                ctx,
                title="Ignored roles & channels for logging"
            )
            e.add_fields([
                {
                    "name": "🎭 __**Roles**__",
                    "value": "``▶`` {}".format(", ".join([f"<@&{x}>" for x in roles])) if len(roles) > 0 else "``▶`` None"
                },
                {
                    "name": "💬 __**Channels**__",
                    "value": "``▶`` {}".format(", ".join([f"<#{x}>" for x in channels])) if len(channels) > 0 else "``▶`` None"
                }
            ])

            await ctx.response.send_message(embed=e)


    @ignore_log.command(
        name="add",
        description="Adds the given role and/or channel as ignored for logging"
    )
    @discord.app_commands.default_permissions(manage_guild=True)
    async def add(
        self, 
        ctx: discord.Interaction, 
        role: discord.Role = None,
        channel: discord.TextChannel = None
    ) -> None:
        """
        ignore_log_add_help
        examples:
        -ignore_log add @test
        -ignore_log add #test
        """
        if role == None and channel == None: return self.error(ctx, commands.BadArgument("At least one role or channel required"))
        role_or_channel = [role, channel]

        roles, channels = self.get_ignored_roles_channels(ctx.guild)

        added, ignored = [], []
        for e in role_or_channel:
            if isinstance(e, discord.Role):
                if not e.id in roles:
                    roles.append(e.id); added.append(e)
                else:
                    ignored.append(e)
            elif isinstance(e, (discord.TextChannel, discord.VoiceChannel)):
                if not e.id in channels:
                    channels.append(e.id); added.append(e)
                else:
                    ignored.append(e)
        
        self.db.configs.multi_update(ctx.guild.id, {
            "ignored_roles_log": roles,
            "ignored_channels_log": channels
        })

        e = Embed(
            ctx,
            title="Updated the following roles & channels"
        )
        e.add_fields([
            {
                "name": "🎭 __**Added roles**__",
                "value": "``▶`` {}".format(", ".join(
                    [
                        x.mention for x in added if isinstance(x, discord.Role)
                    ]
                )) if len(
                    [
                        _ for _ in added if isinstance(_, discord.Role)
                    ]
                ) > 0 else "``▶`` None"
            },
            {
                "name": "💬 __**Added channels**__",
                "value": "``▶`` {}".format(", ".join(
                    [
                        x.mention for x in added if isinstance(x, (discord.TextChannel, discord.VoiceChannel))
                    ]
                )) if len(
                    [
                        _ for _ in added if isinstance(_, (discord.TextChannel, discord.VoiceChannel))
                    ]
                ) > 0 else "``▶`` None"
            },
            {
                "name": "🔒 __**Ignored**__",
                "value": "``▶`` {}".format(", ".join(
                    [
                        x.mention for x in ignored
                    ]
                )) if len(
                    [
                        _ for _ in ignored
                    ]
                ) > 0 else "``▶`` None"
            },
        ])

        await ctx.response.send_message(embed=e)


    @ignore_log.command(
        name="remove",
        description="Removes the given role and/or channel as ignored for logging"
    )
    @discord.app_commands.default_permissions(manage_guild=True)
    async def remove(
        self, 
        ctx: discord.Interaction, 
        role: discord.Role = None,
        channel: discord.TextChannel = None
    ) -> None:
        """
        ignore_log_remove_help
        examples:
        -ignore_log remove @test 
        -ignore_log remove #test
        """
        if role == None and channel == None: return self.error(ctx, commands.BadArgument("At least one role or channel required"))
        role_or_channel = [role, channel]

        roles, channels = self.get_ignored_roles_channels(ctx.guild)

        removed, ignored = [], []
        for e in role_or_channel:
            if isinstance(e, discord.Role):
                if e.id in roles:
                    roles.remove(e.id); removed.append(e)
                else:
                    ignored.append(e)
            elif isinstance(e, (discord.TextChannel, discord.VoiceChannel)):
                if e.id in channels:
                    channels.remove(e.id); removed.append(e)
                else:
                    ignored.append(e)
            else:
                ignored.append(e)
        
        self.db.configs.multi_update(ctx.guild.id, {
            "ignored_roles_log": roles,
            "ignored_channels_log": channels
        })

        e = Embed(
            ctx,
            title="Updated the following roles & channels"
        )
        e.add_fields([
            {
                "name": "🎭 __**Removed roles**__",
                "value": "``▶`` {}".format(", ".join(
                    [
                        x.mention for x in removed if isinstance(x, discord.Role)
                    ]
                )) if len(
                    [
                        _ for _ in removed if isinstance(_, discord.Role)
                    ]
                ) > 0 else "``▶`` None"
            },
            {
                "name": "💬 __**Removed channels**__",
                "value": "``▶`` {}".format(", ".join(
                    [
                        x.mention for x in removed if isinstance(x, (discord.TextChannel, discord.VoiceChannel))
                    ]
                )) if len(
                    [
                        _ for _ in removed if isinstance(_, (discord.TextChannel, discord.VoiceChannel))
                    ]
                ) > 0 else "``▶`` None"
            },
            {
                "name": "🔒 __**Ignored**__",
                "value": "``▶`` {}".format(", ".join(
                    [
                        x.mention for x in ignored
                    ]
                )) if len(
                    [
                        _ for _ in ignored
                    ]
                ) > 0 else "``▶`` None"
            },
        ])

        await ctx.response.send_message(embed=e)


    @discord.app_commands.command(
        name="join_role",
        description="Configure the join role (role users automatically get when joining the server)"
    )
    @discord.app_commands.default_permissions(manage_roles=True)
    async def join_role(
        self,
        ctx: discord.Interaction,
        role: discord.Role = None,
        disable: Literal[
            "True"
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
            return await ctx.response.send_message(self.locale.t(ctx.guild, "join_role_off", _emote="YES"))
        else:
            if role == None:
                prefix = "/"
                e = Embed(
                    ctx,
                    description=self.locale.t(ctx.guild, "invalid_join_role", _emote="NO")
                )
                e.add_fields([
                    {
                        "name": "__**Set the join role**__",
                        "value": f"``{prefix}join_role @role``"
                    },
                    {
                        "name": "__**Remove the join role**__",
                        "value": f"``{prefix}join_role disable:True``"
                    }
                ])

                return await ctx.response.send_message(embed=e)
            else:
                if role.position >= ctx.guild.me.top_role.position: 
                    return await ctx.response.send_message(self.locale.t(ctx.guild, "role_too_high", _emote="NO"))

                self.db.configs.update(ctx.guild.id, "join_role", f"{role.id}")
                await ctx.response.send_message(self.locale.t(ctx.guild, "join_role_on", _emote="YES", role=role.name))


    @discord.app_commands.command(
        name="setup",
        description="Guide for setting up the bot"
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