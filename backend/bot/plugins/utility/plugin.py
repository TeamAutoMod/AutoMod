# type: ignore

import unicodedata
import discord
from discord.ext import commands

import time
import re
import requests
import subprocess
import datetime
from PIL import Image
from io import BytesIO
from toolbox import S as Object
from typing import Union, List, Literal

from .. import AutoModPluginBlueprint, ShardedBotInstance
from ...types import Embed, Duration, E, Emote
from ...views import AboutView, HelpView
from ...schemas import Slowmode
from ...modals import EmbedBuilderModal



ACTUAL_PLUGIN_NAMES = {
    "ConfigPlugin": "Configuration",
    "AutomodPlugin": "Automoderator",
    "ModerationPlugin": "Moderation",
    "FilterPlugin": "Filters & Regexes",
    "UtilityPlugin": "Utility",
    "LevelPlugin": "Level System",
    "TagsPlugin": "Custom Commands & Responders",
    "CasesPlugin": "Case System",
    "ReactionRolesPlugin": "Reaction Roles"
    #"AlertsPlugin": "👾 Twitch Alerts"
}

EMOJI_RE = re.compile(r"<:(.+):([0-9]+)>")
CDN = "https://twemoji.maxcdn.com/2/72x72/{}.png"

MAX_NATIVE_SLOWMODE = 21600 # 6 hours
MAX_BOT_SLOWMODE = 1209600 # 14 days


def get_help_embed(
    plugin: AutoModPluginBlueprint, 
    ctx: discord.Interaction, 
    cmd: Union[
        discord.app_commands.AppCommand,
        discord.app_commands.Group
    ]
) -> Embed:
    if isinstance(cmd, discord.app_commands.Group): 
        help_message = cmd.description if cmd.description[1] != " " else cmd.description[2:]
        usage = f"/{cmd.name}"
    else:
        usage = f"""{
            "/"
        }{
            cmd.qualified_name
        } {
            " ".join(
                [
                    *[f"<{x}>" for x, y in cmd._params.items() if y.required],
                    *[f"[{x}]" for x, y in cmd._params.items() if not y.required]
                ]
            )
        }"""

        help_message = cmd.description if cmd.description[1] != " " else cmd.description[2:]
        if usage[-1] == " ": usage = usage[:-1]

    e = Embed(
        ctx,
        title=f"``{usage}``"
    )
    e.add_field(
        name="**__Description__**", 
        value=f"{help_message}"
    )
    
    if not isinstance(cmd, discord.app_commands.Group):
        examples = cmd._callback.__doc__.replace("        ", "").split("\nexamples:")[1].split("\n-")[1:]
        if len(examples) > 0:
            prefix = "/"
            e.add_field(
                name="**__Examples__**",
                value="\n".join(
                    [
                        f"{prefix}{exmp}" for exmp in examples
                    ]
                )
            )
    else:
        e.add_field(
            name="**__Subcommands__**", 
            value="{}".format("\n".join([f"> </{x.qualified_name}:{plugin.bot.internal_cmd_store.get(cmd.name)}>" for x in cmd.commands]))
        )

    e.set_footer(text="<required> [optional]")
    return e


def get_command_help(
    plugin: AutoModPluginBlueprint, 
    ctx: discord.Interaction, 
    query: str
) -> Union[
    Embed, 
    None
]:
    for p in [plugin.bot.get_plugin(x) for x in ACTUAL_PLUGIN_NAMES.keys()]:
        if p != None:
            cmds = {x.name.lower(): x for x in p.__cog_app_commands__ if x.name not in plugin.bot.config.disabled_commands}
            root = "".join(query.lower().split(" ")[0])
            if root in cmds:
                cmd = cmds.get(root)
                if len(query.split(" ")) < 2:
                    return get_help_embed(plugin, ctx, cmd)
                else:
                    sub = " ".join(query.lower().split(" ")[1:])
                    if hasattr(cmd, "commands"):
                        for final in cmd.commands:
                            if final.name == sub:
                                return get_help_embed(plugin, ctx, final)
                    else:
                        if cmd.name == sub:
                            return get_help_embed(plugin, ctx, final)
                    return None
    return None


def get_version() -> str:
    try:
        _V = subprocess.check_output(["git", "rev-parse", "HEAD"]).strip()
    except Exception:
        VERSION = "1.0.0"
    else:
        VERSION = str(_V).replace("b'", "")[:7]
    finally:
        return VERSION


def to_string(
    char: str
) -> str:
    dig = f"{ord(char):x}"
    name = unicodedata.name(char, "Name not found")
    return f"\\U{dig:>08} | {name} | {char}"


def get_user_badges(
    bot: ShardedBotInstance, 
    flags: discord.PublicUserFlags
) -> str:
    badges = []
    if flags.staff: badges.append(bot.emotes.get("STAFF"))
    if flags.partner: badges.append(bot.emotes.get("PARTNER"))
    if flags.discord_certified_moderator: badges.append(bot.emotes.get("MOD"))

    if flags.hypesquad: badges.append(bot.emotes.get("HYPESQUAD"))
    if flags.hypesquad_balance: badges.append(bot.emotes.get("BALANCE"))
    if flags.hypesquad_bravery: badges.append(bot.emotes.get("BRAVERY"))
    if flags.hypesquad_brilliance: badges.append(bot.emotes.get("BRILLIANCE"))

    if flags.bug_hunter: badges.append(bot.emotes.get("BUG_HUNTER"))
    if flags.bug_hunter_level_2: badges.append(bot.emotes.get("BUG_HUNTER_GOLD"))

    if flags.early_verified_bot_developer: badges.append(bot.emotes.get("DEV"))
    if flags.early_supporter: badges.append(bot.emotes.get("SUPPORTER"))

    badges = [x for x in badges if x != None]; return " ".join(badges) if len(badges) > 0 else ""


class UtilityPlugin(AutoModPluginBlueprint):
    """Plugin for all utility commands"""
    def __init__(
        self, 
        bot: ShardedBotInstance
    ) -> None:
        super().__init__(bot)


    def get_log_for_case(
        self, 
        ctx: discord.Interaction, 
        case: dict
    ) -> Union[
        str, 
        None
    ]:
        if not "log_id" in case: return None

        log_id = case["log_id"]
        if log_id == None: return

        if "jump_url" in case:
            instant = case["jump_url"]
            if instant != "": instant
        
        log_channel_id = self.db.configs.get(ctx.guild.id, "mod_log")
        if log_channel_id == "": return None

        return f"https://discord.com/channels/{ctx.guild.id}/{log_channel_id}/{log_id}"


    def server_status_for(
        self, 
        user: discord.Member
    ) -> str:
        perms: discord.Permissions = user.guild_permissions
        if (
            perms.administrator == True \
            or perms.manage_guild == True
        ):
            return "Administrator"
        elif (
            perms.manage_channels == True \
            or perms.manage_messages == True \
            or perms.ban_members == True \
            or perms.kick_members == True \
            or perms.moderate_members == True
        ):
            return "Moderator"
        else:
            rid = self.db.configs.get(user.guild.id, "mod_role")
            if rid != "":
                r = user.guild.get_role(int(rid))
                if r != None:
                    if r in user.roles:
                        return "Moderator"
            return "User"


    def can_act(
        self, 
        guild: discord.Guild, 
        mod: discord.Member, 
        target: Union[
            discord.Member, 
            discord.User
        ]
    ) -> bool:
        if mod.id == target.id: return False
        if mod.id == guild.owner_id: return True

        mod = guild.get_member(mod.id)
        target = guild.get_member(target.id)

        if mod != None and target != None:
            rid = self.bot.db.configs.get(guild.id, "mod_role")
            if rid != "":
                if int(rid) in [x.id for x in target.roles]: return False

            return mod.id != target.id \
                and mod.top_role > target.top_role \
                and target.id != guild.owner.id \
                and (
                    target.guild_permissions.ban_members == False 
                    or target.guild_permissions.kick_members == False 
                    or target.guild_permissions.manage_messages == False
                )
        else:
            return True


    def get_features(
        self,
        guild: discord.Guild
    ) -> List[
        Embed
    ]:
        _prefix = "/"
        base = Embed(
            None,
            title="Setup Guide",
            description=self.locale.t(guild, "setup_desc", inv=self.bot.config.support_invite)
        )

        log = Embed(
            None,
            title="📁 Logging",
            description=self.locale.t(guild, "log_val", prefix=_prefix, cmd=f"</log:{self.bot.internal_cmd_store.get('log')}>")
        )

        am = Embed(
            None,
            title="⚔️ Automoderator",
            description=self.locale.t(guild, "automod_val", prefix=_prefix, cmd=f"</automod:{self.bot.internal_cmd_store.get('automod')}>")
        )

        pun = Embed(
            None,
            title="🔨 Punishments",
            description=self.locale.t(guild, "pun_val", prefix=_prefix, cmd=f"</punishments add:{self.bot.internal_cmd_store.get('punishments')}>")
        )
        
        embeds = [base, log, am, pun]
        for e in embeds: e.credits()

        return embeds


    def get_color(
        self,
        inp: str
    ) -> Union[
        int,
        None
    ]:
        base = {
            "red": "FF0000",
            "blue": "0000FF",
            "green": "00FF00",
            "yellow": "FFFF00",
            "orange": "FFA500",
            "purple": "800080",
            "pink": "FF66CC",
            "cyan": "00FFFF",
            "black": "000000",
            "white": "FFFFFF"
        }
        if inp.lower() in base:
            return int(base[inp.lower()], 16)
        else:
            if inp.startswith("#"): inp = inp[1:]
            try:
                out = int(inp, 16)
            except Exception:
                out = None
            finally:
                return out


    @AutoModPluginBlueprint.listener()
    async def on_interaction(
        self,
        i: discord.Interaction
    ) -> None:
        if i.type == discord.InteractionType.component:
            cid = i.data.get("custom_id")
            if cid == "help-select":
                p = self.bot.get_plugin(i.data.get("values")[0])
                if p != None:
                    e = Embed(
                        i,
                        title=ACTUAL_PLUGIN_NAMES.get(i.data.get("values")[0], i.data.get("values")[0])
                    )

                    cmds = []
                    for cmd in p.__cog_app_commands__:
                        if cmd.qualified_name not in self.bot.config.disabled_commands:
                            if cmd.default_permissions != None:
                                if i.user.guild_permissions >= cmd.default_permissions:
                                    cmds.append(cmd)
                            else:
                                cmds.append(cmd)

                    for cmd in cmds:
                        e.add_field(
                            name="**{}**".format(
                                f"/{cmd.qualified_name} " \
                                f"{' '.join([f'<{x}>' for x, y in cmd._params.items() if y.required]) if hasattr(cmd, '_params') else ''}" \
                                f"{' '.join([f'[{x}]' for x, y in cmd._params.items() if not y.required]) if hasattr(cmd, '_params') else ''}" \
                                f"{'(*)' if isinstance(cmd, discord.app_commands.Group) else ''}"
                            ),
                            value="> {}".format(
                                cmd.description
                            ),
                            inline=False
                        )

                    e.set_footer(text="<required> [optional] (* has subcommands)")
                    await i.response.edit_message(embed=e)

            elif cid == "setup-select":
                embeds = self.get_features(i.guild)

                for e in embeds:
                    if e.title[2:].lower() == i.data.get("values")[0]:
                        await i.response.edit_message(embed=e)


    @AutoModPluginBlueprint.listener()
    async def on_message(
        self, 
        msg: discord.Message
    ) -> None:
        if msg.guild == None: return
        if not msg.guild.chunked: await self.bot.chunk_guild(msg.guild)
        if not self.can_act(
            msg.guild, 
            msg.guild.me, 
            msg.author
        ): return
        if not hasattr(msg.channel, "slowmode_delay"): return

        _id = f"{msg.guild.id}-{msg.channel.id}"
        if not self.db.slowmodes.exists(_id): 
            return
        else:
            data = Object(self.db.slowmodes.get_doc(_id))
            needs_update = False
            if f"{msg.author.id}" not in data.users:
                data.users.update({
                    f"{msg.author.id}": {
                        "next_allowed_chat": datetime.datetime.utcnow() + datetime.timedelta(seconds=int(data.time))
                    }
                })
                needs_update = True
            else:
                if data.users[f"{msg.author.id}"]["next_allowed_chat"] > datetime.datetime.utcnow():
                    try:
                        await msg.delete()
                    except Exception:
                        pass
                    else:
                        self.bot.ignore_for_events.append(msg.id)
                    finally:
                        data.users.update({
                            f"{msg.author.id}": {
                                "next_allowed_chat": datetime.datetime.utcnow() + datetime.timedelta(seconds=int(data.time))
                            }
                        })
                        needs_update = True

            if needs_update == True:
                self.db.slowmodes.update(_id, "users", data.users)


    @discord.app_commands.command(
        name="ping", 
        description="⏳ Shows the bot's latencies"
    )
    async def ping(
        self, 
        ctx: discord.Interaction
    ) -> None:
        """
        ping_help
        examples:
        -ping
        """
        # REST API
        msg_t1 = time.perf_counter()
        await ctx.response.defer(thinking=True)
        msg_t2 = time.perf_counter()

        # Database
        db_t1 = time.perf_counter()
        self.db.command("ping")
        db_t2 = time.perf_counter()

        # Shard
        shard = self.bot.get_shard(ctx.guild.shard_id)
        
        await ctx.followup.send(embed=E("**• Rest:** {}ms \n**• Client:** {}ms \n**• Shard:** {}ms \n**• Database:** {}ms".format(
            round((msg_t2 - msg_t1) * 1000),
            round(self.bot.latency * 1000),
            round(shard.latency * 1000),
            round((db_t2 - db_t1) * 1000)
        ), 2))


    @discord.app_commands.command(
        name="about", 
        description="📈 Shows some information about the bot"
    )
    async def about(
        self, 
        ctx: discord.Interaction
    ) -> None:
        """
        about_help
        examples:
        -about
        """
        e = Embed(
            ctx,
            title="AutoMod",
            description=self.locale.t(ctx.guild, "about_description")
        )
        e.set_thumbnail(url=ctx.guild.me.display_avatar)
        e.add_fields([
            {
                "name": "**__Status__**",
                "value": "**• Up:** {} \n**• Version:** {} \n**• Latency:** {}ms"\
                .format(
                    self.bot.get_uptime(),
                    get_version(),
                    round(self.bot.latency * 1000)
                ),
                "inline": True
            },
            {
                "name": "**__Stats__**",
                "value": "**• Guilds:** {0:,} \n**• Users:** {1:,} \n**• Shards:** {2:,}"\
                .format(
                    len(self.bot.guilds),
                    sum([x.member_count for x in self.bot.guilds]),
                    len(self.bot.shards)
                ),
                "inline": True
            },
            {
                "name": "**__Usage__**",
                "value": "**• Commands:** {} \n**• Custom:** {}"\
                .format(
                    self.bot.used_commands,
                    self.bot.used_tags
                ),
                "inline": True
            }
        ])
        e.credits()
        await ctx.response.send_message(embed=e, view=AboutView(self.bot))


    @discord.app_commands.command(
        name="help", 
        description="🔎 Shows help for a specific command or a full list of commands when used without any arguments"
    )
    @discord.app_commands.describe(
        command="The (sub-)command you want to get help about (e.g. ban OR commands add)"
    )
    async def help(
        self, 
        ctx: discord.Interaction, 
        *, 
        command: str = None
    ) -> None:
        """
        help_help
        examples:
        -help
        -help ban
        -help commands add
        """
        query = command
        if query == None:
            e = Embed(
                ctx,
                title="Command List",
                description=self.locale.t(ctx.guild, "help_desc", prefix="/", cmd=f"</setup:{self.bot.internal_cmd_store.get('setup')}>")
            )
            viewable_plugins = []
            for p in [self.bot.get_plugin(x) for x in ACTUAL_PLUGIN_NAMES.keys()]:
                if p != None:
                    if p._requires_premium:
                        if self.db.configs.get(ctx.guild.id, "premium") == False:
                            continue
                    cmds = []
                    for cmd in (p.__cog_app_commands__ if p.qualified_name != "TagsPlugin" else p.__cog_app_commands__[::-1]): # Rather have commands before autoresponders
                        if cmd.qualified_name not in self.bot.config.disabled_commands:
                            if cmd.default_permissions != None:
                                if ctx.user.guild_permissions >= cmd.default_permissions:
                                    if isinstance(cmd, discord.app_commands.Group):
                                        cmds.append(f"``/{cmd.qualified_name}*``")
                                    else:
                                        cmds.append(f"``/{cmd.qualified_name}``")
                            else:
                                if isinstance(cmd, discord.app_commands.Group):
                                    cmds.append(f"``/{cmd.qualified_name}*``")
                                else:
                                    cmds.append(f"``/{cmd.qualified_name}``")
                    
                    if len(cmds) > 0:
                        viewable_plugins.append(p.qualified_name)
                        e.add_field(
                            name=f"**__{ACTUAL_PLUGIN_NAMES[p.qualified_name]}__**",
                            value="> {}".format(
                                ", ".join(cmds)
                            ),
                            inline=False
                        )
            
            if len(viewable_plugins) > 0 and len(viewable_plugins) % 3 != 0:
                e.add_fields([e.blank_field(inline=True) for _ in range((len(viewable_plugins) % 3) - 1)])

            e.credits()

            await ctx.response.send_message(
                embed=e, 
                view=HelpView(self.bot, show_buttons=False, viewable_plugins=viewable_plugins) if len(viewable_plugins) > 0 else None
            )
        else:
            query = "".join(query.splitlines())

            _help = get_command_help(self, ctx, query)
            if _help == None:
                await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "invalid_command", _emote="NO"), 0))
            else:
                await ctx.response.send_message(embed=_help, view=HelpView(self.bot, show_buttons=True))


    @discord.app_commands.command(
        name="avatar", 
        description="👻 Shows a bigger version of a users avatar"
    )
    @discord.app_commands.describe(
        user="The user whose avatar you want to view",
        avatar_type="Whether to show the server avatar (if set) or the regular avatar"
    )
    async def avatar(
        self, 
        ctx: discord.Interaction, 
        user: discord.User = None,
        avatar_type: Literal[
            "Regular",
            "Server"
        ] = None
    ) -> None:
        """
        avatar_help
        examples:
        -avatar
        -avatar @paul#0009
        -avatar 543056846601191508
        """
        if user == None: user = ctx.user

        e = Embed(
            ctx,
            color=user.color if user.color != None else None,
            title="{0.name}#{0.discriminator}'s Avatar".format(user)
        )

        url = None
        if avatar_type == None:
            url = user.display_avatar
        else:
            if avatar_type == "Server":
                url = user.display_avatar
            else:
                url = user.avatar.url if user.avatar != None else user.display_avatar

        e.set_image(
            url=url
        )

        await ctx.response.send_message(embed=e)


    @discord.app_commands.command(
        name="jumbo", 
        description="😀 Shows a bigger version of the provided emotes"
    )
    async def jumbo(
        self, 
        ctx: discord.Interaction, 
        *, 
        emotes: str
    ) -> None:
        """
        jumbo_help
        examples:
        -jumbo :LULW:
        -jumbo :LULW: 🔥
        """
        urls = []
        for e in emotes.split(" ")[:5]:
            if EMOJI_RE.match(e):
                _, eid = EMOJI_RE.findall(e)[0]
                urls.append("https://cdn.discordapp.com/emojis/{}.png".format(eid))
            else:
                url = CDN.format("-".join(
                    c.encode("unicode_escape").decode("utf-8")[2:].lstrip("0")
                    for c in e
                ))
                urls.append(url)

        width, height, images = 0, 0, []
        for url in urls:
            r = requests.get(url)
            try:
                r.raise_for_status()
            except requests.HTTPError:
                return await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "http_error", _emote="NO"), 0))

            img = Image.open(BytesIO(r.content))
            height = img.height if img.height > height else height
            width += img.width + 10
            images.append(img)
        
        image = Image.new("RGBA", (width, height))
        width_offset = 0
        for img in images:
            image.paste(img, (width_offset, 0))
            width_offset += img.width + 10

        combined = BytesIO()
        image.save(combined, "png", quality=55)
        combined.seek(0)
        await ctx.response.send_message(file=discord.File(combined, filename="emoji.png"))

    
    @discord.app_commands.command(
        name="whois", 
        description="📌 Shows some information about the user"
    )
    @discord.app_commands.describe(
        user="The user who you want to get more information about"
    )
    @discord.app_commands.default_permissions(manage_messages=True)
    async def whois(
        self, 
        ctx: discord.Interaction,
        user: discord.User = None
    ) -> None:
        """
        whois_help
        examples:
        -whois
        -whois @paul#0009
        -whois 543056846601191508
        """
        if ctx.guild.chunked == False: await self.bot.chunk_guild(ctx.guild)
        if user == None:
            user = member = ctx.user
        else:
            member: Union[discord.Member, None] = ctx.guild.get_member(user.id)
        
        await ctx.response.defer(thinking=True, ephemeral=(True if ctx.data.get("type") == 2 else False) if ctx.data != None else False)
        e = Embed(
            ctx,
            color=user.color if user.color != None else None
        )
        e.set_thumbnail(
            url=user.display_avatar
        )
        e.add_field(
            name="**__User Information__**",
            value="**• ID:** {} \n**• Profile:** {} \n**• Badges:** {} \n**• Created at:** <t:{}>"\
            .format(
                user.id,
                user.mention,
                get_user_badges(self.bot, user.public_flags),
                round(user.created_at.timestamp())
            )
        )
        if member is not None:
            roles = [r.mention for r in reversed(member.roles) if r != ctx.guild.default_role]

            e.add_field(
                name="**__Server Information__**",
                value="**• Nickname:** {} \n**• Joined at:** <t:{}> \n**• Join position:** {} \n**• Status:** {} \n**• Roles:** {}"\
                .format(
                    member.nick,
                    round(member.joined_at.timestamp()),
                    sorted(ctx.guild.members, key=lambda x: x.joined_at, reverse=False).index(member) + 1,
                    self.server_status_for(member),
                    len(roles) if len(roles) < 1 or len(roles) > 20 else ", ".join(roles)
                )
            )

        cases = list(
            reversed(
                list(
                    filter(
                        lambda x: x["guild"] == str(ctx.guild.id) and x["user_id"] == str(user.id), self.db.cases.find()
                    )
                )
            )
        )
        last_3 = []
        
        if len(cases) < 1:
            last_3.append("None")
        else:
            for c in cases[:max(min(3, len(cases)), 0)]:
                log_url = self.get_log_for_case(ctx, c)
                if log_url == None:
                    last_3.append(f"{c['type'].capitalize()} (#{c['case']})")
                else:
                    last_3.append(f"[{c['type'].capitalize()} (#{c['case']})]({log_url})")    

        e.add_field(
            name="**__Infractions__**",
            value="**• Total Cases:** {} \n**• Last 3 Cases:** {}"\
            .format(
                len(cases),
                ", ".join(last_3)
            )
        )

        await ctx.followup.send(embed=e, ephemeral=(True if ctx.data.get("type") == 2 else False) if ctx.data != None else False)


    @discord.app_commands.command(
        name="serverinfo", 
        description="📚 Shows some information about the server"
    )
    @discord.app_commands.default_permissions(manage_messages=True)
    async def server(
        self, 
        ctx: discord.Interaction
    ) -> None:
        """ 
        server_help
        examples:
        -serverinfo
        """
        g: discord.Guild = ctx.guild

        e = Embed(ctx)
        if ctx.guild.icon != None:
            e.set_thumbnail(
                url=ctx.guild.icon.url
            )
        
        e.add_fields([
            {
                "name": "**__Information__**",
                "value": "**• ID:** {} \n**• Owner:** {} \n**• Created:** <t:{}> \n**• Invite Splash:** {} \n**• Banner:** {}"\
                .format(
                    g.id, 
                    g.owner, 
                    round(g.created_at.timestamp()),
                    f"[Here]({g.splash.url})" if g.splash != None else "None",
                    f"[Here]({g.banner.url})" if g.banner != None else "None"
                ),
                "inline": True
            },
            e.blank_field(True),
            {
                "name": "**__Channels__**",
                "value": "**• Categories:** {} \n**• Text:** {} \n**• Voice:** {} \n**• Threads:** {}"\
                .format(
                    len([x for x in g.channels if isinstance(x, discord.CategoryChannel)]),
                    len(g.text_channels), 
                    len(g.voice_channels),
                    len(g.threads)
                ),
                "inline": True
            },
            {
                "name": "**__Members__**",
                "value": "**• Total:** {} \n**• Users:** {} \n**• Bots:** {}"\
                .format(
                    len(g.members), 
                    len([x for x in g.members if not x.bot]), 
                    len([x for x in g.members if x.bot])
                ),
                "inline": True
            },
            e.blank_field(True),
            {
                "name": "**__Other__**",
                "value": "**• Roles:** {} \n**• Emojis:** {} \n**• Boosters:** {}"\
                .format(
                    len(g.roles), 
                    len(g.emojis),
                    g.premium_subscription_count
                ),
                "inline": True
            },
            {
                "name": "**__Features__**",
                "value": "{}"\
                .format(
                    ", ".join([f"{x.replace('_', ' ').title()}" for x in g.features]) if len(g.features) > 0 else "None"
                ),
                "inline": False
            },
        ])
        await ctx.response.send_message(embed=e)


    @discord.app_commands.command(
        name="slowmode", 
        description="🕒 Edits the channel's slowmode or shows all active bot-set slowmodes"
    )
    @discord.app_commands.describe(
        time="5s, 10m, 3h, 1d (0 to disable)"
    )
    @discord.app_commands.default_permissions(manage_channels=True)
    async def slowmode(
        self, 
        ctx: discord.Interaction, 
        time: str = None
    ) -> None:
        """
        slowmode_help
        examples:
        -slowmode 20m
        -slowmode 1d
        -slowmode 0
        -slowmode
        """
        if time == None:
            slowmodes = [x for x in self.bot.db.slowmodes.find({}) if x["id"].split("-")[0] == f"{ctx.guild.id}"]
            if len(slowmodes) < 1:
                return await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "no_slowmodes", _emote="NO"), 0))
            else:
                e = Embed(
                    ctx,
                    title="Bot-set slowmodes"
                )
                for s in slowmodes:
                    channel = ctx.guild.get_channel(int(s["id"].split("-")[1]))
                    if channel != None:
                        e.add_field(
                            name=f"**__#{channel.name}__**",
                            value="**• Time:** {} \n**• Mode:** {} \n**• Moderator:** {}"\
                                .format(
                                    s["pretty"],
                                    s["mode"],
                                    f"<@{s['mod']}>"
                                )
                        )
                if len(e._fields) < 1:
                    return await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "no_slowmodes", _emote="NO"), 0))
                else:
                    return await ctx.response.send_message(embed=e)
        else:
            try:
                time = await Duration().convert(ctx, time)
            except Exception as ex:
                return self.error(ctx, ex)
            else:
                if time.unit == None: time.unit = "m"
                _id = f"{ctx.guild.id}-{ctx.channel.id}"
                
                try:
                    seconds = time.to_seconds(ctx)
                except Exception as ex:
                    return self.error(ctx, ex)

                if seconds > 0:
                    if seconds <= MAX_NATIVE_SLOWMODE:
                        if self.db.slowmodes.exists(_id):
                            self.db.slowmodes.delete(_id)
                        try:
                            await ctx.channel.edit(
                                slowmode_delay=seconds
                            )
                        except Exception as ex:
                            return await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "fail", _emote="NO", exc=ex), 0))
                        else:
                            self.db.slowmodes.insert(Slowmode(ctx.guild, ctx.channel, ctx.user, seconds, f"{time}", "native"))
                            return await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "set_slowmode", _emote="YES", time=str(time), mode="native slowmode"), 1))
                    else:
                        if seconds <= MAX_BOT_SLOWMODE:
                            try:
                                await ctx.channel.edit(
                                    slowmode_delay=MAX_NATIVE_SLOWMODE
                                )
                            except Exception as ex:
                                return await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "fail", _emote="NO", exc=ex), 0))
                            else:
                                if self.db.slowmodes.exists(_id):
                                    self.db.slowmodes.multi_update(_id, {
                                        "time": seconds,
                                        "pretty": f"{time}"
                                    })
                                else:
                                    self.db.slowmodes.insert(Slowmode(ctx.guild, ctx.channel, ctx.user, seconds, f"{time}", "bot-maintained"))
                                
                                return await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "set_slowmode", _emote="YES", time=str(time),mode="bot-maintained slowmode"), 1))
                        else:
                            return await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "max_slowmode", _emote="YES", mode="bot-maintained slowmode"), 1))
                else:
                    if ctx.channel.slowmode_delay > 0:
                        try:
                            await ctx.channel.edit(
                                slowmode_delay=0
                            )
                        except Exception as ex:
                            return self.error(ctx, ex)

                    if self.db.slowmodes.exists(_id):
                        self.db.slowmodes.delete(_id)
                    
                    return await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "removed_slowmode", _emote="YES"), 1))


    @discord.app_commands.command(
        name="charinfo", 
        description="💱 Shows some information about the characters in the given string"
    )
    async def charinfo(
        self, 
        ctx: discord.Interaction, 
        *, 
        chars: str
    ) -> None:
        """
        charinfo_help
        examples:
        -charinfo A
        -charinfo Test
        -charinfo <= x
        """
        msg = "```\n{}\n```".format("\n".join(map(to_string, chars)))
        await ctx.response.send_message(msg[:2000])


    @discord.app_commands.command(
        name="create-message",
        description="✍️ Creates a message the bot will send"
    )
    @discord.app_commands.describe(
        channel="What channel to send the message/embed in",
        message="The message sent together with the embed",
        has_embed="Whether this message has an embed in general",
        color="Color for the embed (e.g. 7289da, FF0000 or Blue)",
        timestamp="Whether or not to show the timestamp in the footer",
        image_url="URL to an image shown in the embed",
        thumbnail_url="URL to an image used as the thumbnail in the right corner",
        author_name="Text of the author field",
        author_icon_url="URL to an image used as the small icon next to the author text",
        author_url="Create a hyperlink for the author text",
        footer_text="Text for the embed footer",
        footer_icon_url="URL to an image used as the small icon next to the footer text"
    )
    @discord.app_commands.default_permissions(manage_messages=True)
    async def create_message(
        self,
        ctx: discord.Interaction,
        channel: discord.TextChannel,
        message: str = None,
        color: str = None,
        has_embed: Literal[
            "True",
            "False"
        ] = "False",
        timestamp: Literal[
            "True",
            "False"
        ] = "False",
        image_url: str = None,
        thumbnail_url: str = None,
        author_name: str = None,
        author_icon_url: str = None,
        author_url: str = None,
        footer_text: str = None,
        footer_icon_url: str = None
    ) -> None:
        """
        create_message_help
        examples:
        -create-message #test message:Hey
        -create-message #test has_embed:True
        -create-message #test message:Hey has_embed:True
        """
        if message == None and has_embed.lower() == "false":
            return await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "embed_req", _emote="NO"), 0))
        
        if color != None: color = self.get_color(color)

        if has_embed.lower() == "true":
            async def callback(
                i: discord.Interaction
            ) -> None:
                title, desc, fn1, fv1 = self.bot.extract_args(i, "title", "desc", "fn1", "fv1")
                
                e = Embed(
                    None,
                    title=title if title != "" else "None" if desc == "" else None,
                    description=desc if desc != "" else "None" if title == "" else None,
                    color=color,
                    timestamp=datetime.datetime.now() if timestamp.lower() == "true" else None
                )

                if fn1 != "" or fv1 != "":
                    e.add_field(name=fn1 if fn1 != "" else "None", value=fv1 if fv1 != "" else "None")

                if image_url != None: e.set_image(url=image_url)
                if thumbnail_url != None: e.set_thumbnail(thumbnail_url)
                if author_name != None: e.set_author(name=author_name, url=author_url, icon_url=author_icon_url)
                if footer_text != None: e.set_footer(text=footer_text, icon_url=footer_icon_url)

                try:
                    await channel.send(content=message, embed=e)
                except Exception as ex:
                    await i.response.send_message(embed=E(self.locale.t(i.guild, "fail", _emote="NO", exc=ex), 0))
                else:
                    await i.response.send_message(embed=E(self.locale.t(i.guild, "send_msg", _emote="YES", channel=channel), 1), ephemeral=True) 

            modal = EmbedBuilderModal(
                self.bot,
                "Embed Field Builder",
                callback=callback
            )
            await ctx.response.send_modal(modal)
        else:
            try:
                await channel.send(content=message)
            except Exception as ex:
                await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "fail", _emote="NO", exc=ex), 0))
            else:
                await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "send_msg", _emote="YES", channel=channel), 1), ephemeral=True)    


    # @discord.app_commands.command(
    #     name="edit-message",
    #     description="✍️ Edits a message created by the bot"
    # )
    # @discord.app_commands.describe(
    #     message_id="The ID of the message you want to edit (right click message -> copy ID)",
    #     message="The message sent together with the embed",
    #     has_embed="Whether this message has an embed in general",
    #     color="Color for the embed (e.g. 7289da, FF0000 or Blue)",
    #     timestamp="Whether or not to show the timestamp in the footer",
    #     image_url="URL to an image shown in the embed",
    #     thumbnail_url="URL to an image used as the thumbnail in the right corner",
    #     author_name="Text of the author field",
    #     author_icon_url="URL to an image used as the small icon next to the author text",
    #     author_url="Create a hyperlink for the author text",
    #     footer_text="Text for the embed footer",
    #     footer_icon_url="URL to an image used as the small icon next to the footer text"
    # )
    # @discord.app_commands.default_permissions(manage_messages=True)
    # async def edit_message(
    #     self,
    #     ctx: discord.Interaction,
    #     message_id: str,
    #     message: str = None,
    #     color: str = None,
    #     has_embed: Literal[
    #         "True",
    #         "False"
    #     ] = "False",
    #     timestamp: Literal[
    #         "True",
    #         "False"
    #     ] = "False",
    #     image_url: str = None,
    #     thumbnail_url: str = None,
    #     author_name: str = None,
    #     author_icon_url: str = None,
    #     author_url: str = None,
    #     footer_text: str = None,
    #     footer_icon_url: str = None
    # ) -> None:
    #     """
    #     edit_message_help
    #     examples:
    #     -edit-message 123456789 message:Hey
    #     -edit-message 123456789 has_embed:True
    #     -edit-message 123456789 message:Hey has_embed:True
    #     """
    #     try:
    #         og_msg: discord.Message = await ctx.channel.fetch_message(int(message_id))
    #     except Exception as ex:
    #         await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "fail", _emote="NO", exc=ex), 0))
    #     else:
    #         if og_msg == None: return ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "msg_not_found", _emote="NO"), 0))
    #         if str(og_msg.author.id) != str(self.bot.user.id): return ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "msg_not_own", _emote="NO"), 0))

    #         if message == None and has_embed.lower() == "false":
    #             return await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "embed_req", _emote="NO"), 0))
            
    #         if color != None: color = self.get_color(color)

    #         if has_embed.lower() == "true":
    #             async def callback(
    #                 i: discord.Interaction
    #             ) -> None:
    #                 title, desc, fn1, fv1 = self.bot.extract_args(i, "title", "desc", "fn1", "fv1")
                    
    #                 e = Embed(
    #                     None,
    #                     title=title if title != "" else "None" if desc == "" else None,
    #                     description=desc if desc != "" else "None" if title == "" else None,
    #                     color=color,
    #                     timestamp=datetime.datetime.now() if timestamp.lower() == "true" else None
    #                 )

    #                 if fn1 != "" or fv1 != "":
    #                     e.add_field(name=fn1 if fn1 != "" else "None", value=fv1 if fv1 != "" else "None")

    #                 if image_url != None: e.set_image(url=image_url)
    #                 if thumbnail_url != None: e.set_thumbnail(thumbnail_url)
    #                 if author_name != None: e.set_author(name=author_name, url=author_url, icon_url=author_icon_url)
    #                 if footer_text != None: e.set_footer(text=footer_text, icon_url=footer_icon_url)

    #                 try:
    #                     await og_msg.edit(
    #                         content=message if message != None else og_msg.content, 
    #                         embed=e if has_embed.lower() == "true" else (og_msg.embeds[0] if len(og_msg.embeds) > 0 else None)
    #                     )
    #                 except Exception as ex:
    #                     await i.response.send_message(embed=E(self.locale.t(i.guild, "fail", _emote="NO", exc=ex), 0))
    #                 else:
    #                     await i.response.send_message(embed=E(self.locale.t(i.guild, "edited_msg", _emote="YES"), 1), ephemeral=True) 

    #             modal = EmbedBuilderModal(
    #                 self.bot,
    #                 "Embed Field Builder",
    #                 callback=callback
    #             )
    #             await ctx.response.send_modal(modal)
    #         else:
    #             try:
    #                 await og_msg.edit(
    #                     content=message if message != None else og_msg.content, 
    #                     embed=e if has_embed.lower() == "true" else (og_msg.embeds[0] if len(og_msg.embeds) > 0 else None)
    #                 )
    #             except Exception as ex:
    #                 await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "fail", _emote="NO", exc=ex), 0))
    #             else:
    #                 await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "edited_msg", _emote="YES"), 1), ephemeral=True)         


async def setup(
    bot: ShardedBotInstance
) -> None: await bot.register_plugin(UtilityPlugin(bot))