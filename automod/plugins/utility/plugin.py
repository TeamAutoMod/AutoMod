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
from ...__obj__ import TypeHintedToolboxObject as Object
from typing import Union, Literal, Tuple, Optional, List, Dict, Any

from .. import AutoModPluginBlueprint, ShardedBotInstance
from ...types import Embed, Duration, E
from ...views import AboutView, HelpView, SetupView, HighlightDMView
from ...schemas import Slowmode, Highlights
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
}

EMOJI_RE = re.compile(r"<:(.+):([0-9]+)>")
CDN = "https://twemoji.maxcdn.com/2/72x72/{}.png"

MAX_NATIVE_SLOWMODE = 21600 # 6 hours
MAX_BOT_SLOWMODE = 1209600 # 14 days


def get_help_embed(plugin: AutoModPluginBlueprint, ctx: discord.Interaction, cmd: Union[discord.app_commands.AppCommand,discord.app_commands.Group]) -> Embed:
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
        name="❯ __Description__", 
        value=f"{help_message}"
    )
    
    if not isinstance(cmd, discord.app_commands.Group):
        examples = cmd._callback.__doc__.replace("        ", "").split("\nexamples:")[1].split("\n-")[1:]
        if len(examples) > 0:
            prefix = "/"
            e.add_field(
                name="❯ __Examples__",
                value="\n".join(
                    [
                        f"{prefix}{exmp}" for exmp in examples
                    ]
                )
            )
    else:
        e.add_field(
            name="❯ __Subcommands__", 
            value="{}".format("\n".join([f"**•** </{x.qualified_name}:{plugin.bot.internal_cmd_store.get(cmd.name)}>" for x in cmd.commands]))
        )

    e.set_footer(text="<required> [optional]")
    return e


def get_command_help(plugin: AutoModPluginBlueprint, ctx: discord.Interaction, query: str) -> Optional[Embed]:
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


def to_string(char: str) -> str:
    dig = f"{ord(char):x}"
    name = unicodedata.name(char, "Name not found")
    return f"\\U{dig:>08} | {name} | {char}"


def get_user_badges(bot: ShardedBotInstance, flags: discord.PublicUserFlags) -> str:
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
    def __init__(self, bot: ShardedBotInstance) -> None:
        super().__init__(bot)


    def get_log_for_case(self, ctx: discord.Interaction, case: Dict[str, Any]) -> Optional[str]:
        if not "log_id" in case: return None

        log_id = case["log_id"]
        if log_id == None: return

        if "jump_url" in case:
            instant = case["jump_url"]
            if instant != "": instant
        
        log_channel_id = self.db.configs.get(ctx.guild.id, "mod_log")
        if log_channel_id == "": return None

        return f"https://discord.com/channels/{ctx.guild.id}/{log_channel_id}/{log_id}"


    def server_status_for(self, user: discord.Member) -> str:
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


    def can_act(self, guild: discord.Guild, mod: discord.Member, target: Union[discord.Member, discord.User]) -> bool:
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


    def get_features(self, guild: discord.Guild) -> List[Embed]:
        _prefix = "/"
        base = Embed(
            None,
            title=f"Setup Guide",
            description=self.locale.t(guild, "setup_desc", inv=self.bot.config.support_invite)
        )

        log = Embed(
            None,
            title=f"Logging",
            description=self.locale.t(guild, "log_val", prefix=_prefix, cmd=f"</logs enable:{self.bot.internal_cmd_store.get('logs')}>")
        )

        am = Embed(
            None,
            title=f"Automoderator",
            description=self.locale.t(guild, "automod_val", prefix=_prefix, cmd=f"</automod enable:{self.bot.internal_cmd_store.get('automod')}>")
        )

        pun = Embed(
            None,
            title=f"Punishments",
            description=self.locale.t(guild, "pun_val", prefix=_prefix, cmd=f"</punishments add:{self.bot.internal_cmd_store.get('punishments')}>")
        )
        
        embeds = [base, log, am, pun]
        for e in embeds: e.credits()

        return embeds


    def get_color(self,inp: str) -> Optional[int]:
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
            

    def get_viewable_plugins(self, ctx: discord.Interaction) -> List[str]:
        viewable_plugins = []
        for p in [self.bot.get_plugin(x) for x in ACTUAL_PLUGIN_NAMES.keys()]:
            if p != None:
                if p._requires_premium:
                    if self.db.configs.get(ctx.guild.id, "premium") == False:
                        continue

                has_commands = False
                for cmd in (p.__cog_app_commands__ if p.qualified_name != "TagsPlugin" else p.__cog_app_commands__[::-1]): # Rather have commands before autoresponders
                    if cmd.qualified_name not in self.bot.config.disabled_commands:
                        if cmd.default_permissions != None:
                            if ctx.user.guild_permissions >= cmd.default_permissions:
                                if isinstance(cmd, discord.app_commands.Group):
                                    has_commands = True
                                else:
                                    has_commands = True
                        else:
                            if isinstance(cmd, discord.app_commands.Group):
                                has_commands = True
                            else:
                                has_commands = True
                
                if has_commands:
                    viewable_plugins.append(p.qualified_name)
        return viewable_plugins
    

    def get_highlights(self, ctx: discord.Interaction) -> Tuple[List[str], Dict[str, List[str]]]:
        highlights_from_db: Optional[Dict[str, List[Dict[str, str]]]] = self.db.highlights.get(f"{ctx.guild.id}", "highlights")
        if highlights_from_db == None:
            self.db.highlights.insert(Highlights(ctx))
            return [], {f"{ctx.user.id}": []}
        else:
            return highlights_from_db.get(f"{ctx.user.id}", []), highlights_from_db
        

    def get_highlights_from_msg(self, msg: discord.Message) -> Dict[str, List[str]]:
        highlights_from_db: Optional[Dict[str, List[Dict[str, str]]]]  = self.db.highlights.get(f"{msg.guild.id}", "highlights")
        if highlights_from_db == None:
            self.db.highlights.insert(Highlights(msg))
            return {}
        else:
            return highlights_from_db
        

    def add_highlight(self, ctx: discord.Interaction, all_highlights: List[Dict[str, Any]], new_highlight: str) -> None:
        all_highlights.update({
            f"{ctx.user.id}": [*all_highlights.get(f"{ctx.user.id}", []), *[new_highlight]]
        })
        self.db.highlights.update(f"{ctx.guild.id}", "highlights", all_highlights)


    def delete_highlight(self, guild: discord.Guild, user_id: int, all_highlights: List[Dict[str, Any]], old_highlight: str) -> None:
        all_highlights.update({
            f"{user_id}": [x for x in all_highlights.get(f"{user_id}", []) if x != old_highlight]
        })
        self.db.highlights.update(f"{guild.id}", "highlights", all_highlights)
        

    @AutoModPluginBlueprint.listener()
    async def on_interaction(self, i: discord.Interaction) -> None:
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
                        sig = "{}".format(
                            f"/{cmd.qualified_name} " \
                            f"{' '.join([f'<{x}>' for x, y in cmd._params.items() if y.required]) if hasattr(cmd, '_params') else ''}" \
                            f"{' ' if len([_ for _, v in cmd._params.items() if v.required] if hasattr(cmd, '_params') else []) > 0 else ''}{' '.join([f'[{x}]' for x, y in cmd._params.items() if not y.required]) if hasattr(cmd, '_params') else ''}" \
                            f"{'(*)' if isinstance(cmd, discord.app_commands.Group) else ''}"
                        )
                        e.add_field(
                            name=f"``{sig}``" if sig[-1] != " " else f"``{sig[0:-1]}``",
                            value="> {}".format(
                                cmd.description if cmd.description[1] != " " else cmd.description[2:]
                            ),
                            inline=False
                        )

                    e.set_footer(text="<required> [optional] (* has subcommands)")
                    await i.response.edit_message(
                        embed=e,
                        view=HelpView(self.bot, show_buttons=False, viewable_plugins=self.get_viewable_plugins(i), current_select=p.qualified_name)
                    )

            elif cid == "setup-select":
                embeds = self.get_features(i.guild)

                for e in embeds[1:]:
                    if e.title.lower() == i.data.get("values")[0]:
                        await i.response.edit_message(
                            embed=e, 
                            view=SetupView(self.bot, embeds=embeds, current_select=i.data.get("values")[0])
                        )


    @AutoModPluginBlueprint.listener(name="on_message")
    async def on_slowmode(self, msg: discord.Message) -> None:
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

    
    @AutoModPluginBlueprint.listener(name="on_message")
    async def on_highlight(self, msg: discord.Message) -> None:
        if msg.guild == None: return
        guild_highlights = self.get_highlights_from_msg(msg)

        if len(guild_highlights) < 1: return
        for uid, phrases in guild_highlights.items():
            user: Optional[discord.Member] = msg.guild.get_member(int(uid))
            if (user != None \
                and str(uid) != str(msg.author.id)  \
                and msg.author.bot == False \
                and str(msg.author.id) != str(self.bot.user.id) \
            ):
                for phrase in phrases:
                    if phrase in msg.content.lower():
                        e = Embed(
                            None,
                            title=f"Highlight in {msg.guild.name}",
                            description="**• Phrase:** ``{}`` \n**• Channel:** {} \n**• Content:** \n```\n{}\n```".format(
                                phrase, msg.channel.mention, msg.content
                            )
                        )
                        view = HighlightDMView(
                            self.bot, 
                            int(uid),
                            msg, 
                            self.delete_highlight, 
                            {
                                "guild": msg.guild,
                                "user_id": int(uid),
                                "all_highlights": guild_highlights, 
                                "old_highlight": phrase
                            }
                        )

                        try:
                            await user.send(embed=e, view=view)
                        except Exception:
                            pass


    @discord.app_commands.command(
        name="ping", 
        description="⏳ Shows the bot's latencies"
    )
    async def ping(self, ctx: discord.Interaction) -> None:
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
    async def about(self, ctx: discord.Interaction) -> None:
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
                "name": f"❯ __Status__",
                "value": "**• Up:** {} \n**• Version:** {} \n**• Latency:** {}ms"\
                .format(
                    self.bot.get_uptime(),
                    get_version(),
                    round(self.bot.latency * 1000)
                ),
                "inline": True
            },
            {
                "name": f"❯ __Stats__",
                "value": "**• Guilds:** {0:,} \n**• Users:** {1:,} \n**• Shards:** {2:,}"\
                .format(
                    len(self.bot.guilds),
                    sum([x.member_count for x in self.bot.guilds]),
                    len(self.bot.shards)
                ),
                "inline": True
            },
            {
                "name": f"❯ __Usage__",
                "value": "**• Commands:** {} \n**• Custom:** {}"\
                .format(
                    self.bot.get_command_stats(),
                    self.bot.get_custom_stats()
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
    async def help(self, ctx: discord.Interaction, *, command: str = None) -> None:
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
                title="AutoMod Help",
                description=self.locale.t(ctx.guild, "help_desc", inv=self.bot.config.support_invite)
            )
            e.set_thumbnail(url=self.bot.user.display_avatar)
            e.credits()

            viewable_plugins = self.get_viewable_plugins(ctx)
            await ctx.response.send_message(
                embed=e, 
                view=HelpView(self.bot, show_buttons=False, viewable_plugins=viewable_plugins) if len(viewable_plugins) > 0 else None, 
                ephemeral=True
            )
        else:
            query = "".join(query.splitlines())

            _help = get_command_help(self, ctx, query)
            if _help == None:
                await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "invalid_command", _emote="NO"), 0), ephemeral=True)
            else:
                await ctx.response.send_message(embed=_help, view=HelpView(self.bot, show_buttons=True), ephemeral=True)


    @discord.app_commands.command(
        name="avatar", 
        description="👻 Shows a bigger version of a users avatar"
    )
    @discord.app_commands.describe(
        user="The user whose avatar you want to view",
        avatar_type="Whether to show the server avatar (if set) or the regular avatar"
    )
    async def avatar(self, ctx: discord.Interaction, user: discord.User = None, avatar_type: Literal["Regular", "Server"] = None) -> None:
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
    @discord.app_commands.describe(
        emotes="The emotes you want to show"
    )
    async def jumbo(self, ctx: discord.Interaction, *, emotes: str) -> None:
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
                return await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "http_error", _emote="NO"), 0), ephemeral=True)

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
        description="📌 Shows some information about a user"
    )
    @discord.app_commands.describe(
        user="The user who you want to get more information about"
    )
    @discord.app_commands.default_permissions(manage_messages=True)
    async def whois(self, ctx: discord.Interaction,user: discord.User = None) -> None:
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
            member: Optional[discord.Member] = ctx.guild.get_member(user.id)
        
        await ctx.response.defer(thinking=True, ephemeral=(True if ctx.data.get("type") == 2 else False) if ctx.data != None else False)
        e = Embed(
            ctx,
            color=user.color if user.color != None else None
        )
        e.set_thumbnail(
            url=user.display_avatar
        )
        e.add_field(
            name=f"❯ __User Information__",
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
                name=f"❯ __Server Information__",
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
            name=f"❯ __Infractions__",
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
    async def server(self, ctx: discord.Interaction) -> None:
        """ 
        server_help
        examples:
        -serverinfo
        """
        g: discord.Guild = ctx.guild

        e = Embed(
            ctx,
            title=f"{g.name}"
        )
        if ctx.guild.icon != None:
            e.set_thumbnail(
                url=ctx.guild.icon.url
            )
        
        e.add_fields([
            {
                "name": f"❯ __Information__",
                "value": "**• ID:** {} \n**• Owner:** {} \n**• Created:** <t:{}:d> \n**• Invite Splash:** {} \n**• Banner:** {}"\
                .format(
                    g.id, 
                    g.owner, 
                    round(g.created_at.timestamp()),
                    f"[Here]({g.splash.url})" if g.splash != None else "None",
                    f"[Here]({g.banner.url})" if g.banner != None else "None"
                ),
                "inline": True
            },
            e.blank_field(True, 8),
            {
                "name": f"❯ __Channels__",
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
                "name": f"❯ __Members__",
                "value": "**• Total:** {} \n**• Users:** {} \n**• Bots:** {}"\
                .format(
                    len(g.members), 
                    len([x for x in g.members if not x.bot]), 
                    len([x for x in g.members if x.bot])
                ),
                "inline": True
            },
            e.blank_field(True, 8),
            {
                "name": f"❯ __Other__",
                "value": "**• Roles:** {} \n**• Emojis:** {} \n**• Boosters:** {}"\
                .format(
                    len(g.roles), 
                    len(g.emojis),
                    g.premium_subscription_count
                ),
                "inline": True
            },
            {
                "name": f"❯ __Features__",
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
        duration="5s, 10m, 3h, 1d (0 to disable)",
        channel="Where to set the slowmode (current channel by default)"
    )
    @discord.app_commands.default_permissions(manage_channels=True)
    async def slowmode(self, ctx: discord.Interaction, duration: str = None, channel: discord.TextChannel = None) -> None:
        """
        slowmode_help
        examples:
        -slowmode 20m
        -slowmode 1d #test
        -slowmode 0
        -slowmode
        """
        if channel == None: channel = ctx.channel
        if duration == None:
            slowmodes = [x for x in self.bot.db.slowmodes.find({}) if x["id"].split("-")[0] == f"{ctx.guild.id}"]
            if len(slowmodes) < 1:
                return await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "no_slowmodes", _emote="INFO"), 2), ephemeral=True)
            else:
                e = Embed(
                    ctx,
                    title="Bot-set slowmodes"
                )
                for s in slowmodes:
                    channel = ctx.guild.get_channel(int(s["id"].split("-")[1]))
                    if channel != None:
                        e.add_field(
                            name=f"__#{channel.name}__",
                            value="**• Time:** {} \n**• Mode:** {} \n**• Moderator:** {}"\
                                .format(
                                    s["pretty"],
                                    s["mode"],
                                    f"<@{s['mod']}>"
                                )
                        )
                if len(e._fields) < 1:
                    return await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "no_slowmodes", _emote="NO"), 0), ephemeral=True)
                else:
                    return await ctx.response.send_message(embed=e)
        else:
            try:
                time = await Duration().convert(ctx, duration)
            except Exception as ex:
                return self.error(ctx, ex)
            else:
                if time.unit == None: time.unit = "m"
                _id = f"{ctx.guild.id}-{channel.id}"
                
                try:
                    seconds = time.to_seconds(ctx)
                except Exception as ex:
                    return self.error(ctx, ex)

                if seconds > 0:
                    if seconds <= MAX_NATIVE_SLOWMODE:
                        if self.db.slowmodes.exists(_id):
                            self.db.slowmodes.delete(_id)
                        try:
                            await channel.edit(
                                slowmode_delay=seconds
                            )
                        except Exception as ex:
                            return await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "fail", _emote="NO", exc=ex), 0), ephemeral=True)
                        else:
                            self.db.slowmodes.insert(Slowmode(ctx.guild, channel, ctx.user, seconds, f"{time}", "native"))
                            return await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "set_slowmode", _emote="YES", time=str(time), channel=channel.mention, mode="native slowmode"), 1))
                    else:
                        if seconds <= MAX_BOT_SLOWMODE:
                            try:
                                await channel.edit(
                                    slowmode_delay=MAX_NATIVE_SLOWMODE
                                )
                            except Exception as ex:
                                return await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "fail", _emote="NO", exc=ex), 0), ephemeral=True)
                            else:
                                if self.db.slowmodes.exists(_id):
                                    self.db.slowmodes.multi_update(_id, {
                                        "time": seconds,
                                        "pretty": f"{time}"
                                    })
                                else:
                                    self.db.slowmodes.insert(Slowmode(ctx.guild, channel, ctx.user, seconds, f"{time}", "bot-maintained"))
                                
                                return await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "set_slowmode", _emote="YES", time=str(time), channel=channel.mention, mode="bot-maintained slowmode"), 1))
                        else:
                            return await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "max_slowmode", _emote="YES", mode="bot-maintained slowmode"), 1))
                else:
                    if channel.slowmode_delay > 0:
                        try:
                            await channel.edit(
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
    async def charinfo(self, ctx: discord.Interaction, *, chars: str) -> None:
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
        description="📈 Creates a message the bot will send"
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
        has_embed: Literal["True", "False"] = "False",
        timestamp: Literal["True", "False"] = "False",
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
            return await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "embed_req", _emote="NO"), 0), ephemeral=True)
        
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
                    await i.response.send_message(embed=E(self.locale.t(i.guild, "fail", _emote="NO", exc=ex), 0), ephemeral=True)
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
                await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "fail", _emote="NO", exc=ex), 0), ephemeral=True)
            else:
                await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "send_msg", _emote="YES", channel=channel), 1), ephemeral=True)      


    _highlights = discord.app_commands.Group(
        name="highlights",
        description="✨ Allows you to setup notifcations for specific phrases in a server"
    )
    @_highlights.command(
        name="add", 
        description="✨ Creates a new highlight for the given phrase"
    )
    @discord.app_commands.describe(
        phrase="The phrase you want to be notified about when said in the server"
    )
    async def _add_highlight(self, ctx: discord.Interaction, phrase: str) -> None:
        """
        highlights_add_help
        examples:
        -highlights add paul
        """
        phrase = phrase.lower()
        guild_highlights, all_highlights = self.get_highlights(ctx)

        if phrase in guild_highlights:
            return await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "alr_highlight", _emote="NO"), 0), ephemeral=True)
        if len(phrase) < 3: 
            return await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "highlight_too_short", _emote="NO"), 0), ephemeral=True)
        
        self.add_highlight(ctx, all_highlights, phrase)
        await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "added_highlight", _emote="YES", phrase=phrase), 1), ephemeral=True)


    @_highlights.command(
        name="delete", 
        description="✨ Deletes a setup highlight"
    )
    @discord.app_commands.describe(
        phrase="The phrase you want to delete as a highlight"
    )
    async def _delete_highlight(self, ctx: discord.Interaction, phrase: str) -> None:
        """
        highlights_delete_help
        examples:
        -highlights delete paul
        """
        phrase = phrase.lower()
        guild_highlights, all_highlights = self.get_highlights(ctx)

        if not phrase in guild_highlights:
            return await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "not_highlight", _emote="NO"), 0), ephemeral=True)
        
        self.delete_highlight(ctx.guild, ctx.user.id, all_highlights, phrase)
        await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "deleted_highlight", _emote="YES", phrase=phrase), 1), ephemeral=True)


    @_highlights.command(
        name="list", 
        description="✨ Lists all your current highlights"
    )
    async def _list_highlight(self, ctx: discord.Interaction) -> None:
        """
        highlights_list_help
        examples:
        -highlights list
        """
        guild_highlights, _ = self.get_highlights(ctx)

        if len(guild_highlights) < 1:
            cmd = f"</highlights add:{self.bot.internal_cmd_store.get('highlights')}>"
            return await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "no_highlights", _emote="NO", cmd=cmd), 0), ephemeral=True)
        
        e = Embed(
            ctx, 
            title=f"Highlights in {ctx.guild.name}", 
            description=", ".join([f"``{x}``" for x in guild_highlights])
        )
        await ctx.response.send_message(embed=e, ephemeral=True)
        

async def setup(bot: ShardedBotInstance) -> None: 
    await bot.register_plugin(UtilityPlugin(bot))