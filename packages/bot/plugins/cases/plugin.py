# type: ignore

import discord
from discord.ext import commands

import datetime
from typing import Union
from toolbox import S as Object
import logging; log = logging.getLogger()
from typing import Union

from .. import AutoModPluginBlueprint, ShardedBotInstance
from ...types import Embed, E
from ...views import MultiPageView
from .._processor.log import LOG_TYPES



class CasesPlugin(AutoModPluginBlueprint):
    """Plugin for internal/log events"""
    def __init__(
        self, 
        bot: ShardedBotInstance
    ) -> None:
        super().__init__(bot)


    def case_embed(
        self, 
        opt: str, 
        user: Union[
            discord.Member, 
            discord.User
        ], 
        last_24_hours: int, 
        last_7_days: int, 
        total: int
    ) -> Embed:
        e = Embed(
            None,
            description=""
        )

        url = None
        if opt == "guild":
            if user.icon != None:
                url=user.icon.url
        else:
            url=user.display_avatar
        e.set_author(
            name=f"Infractions for {user} {f'[{opt.capitalize()}]' if opt != 'guild' else ''}",
            icon_url=url
        )

        e.add_fields([
            {
                "name": "Last 24 hours",
                "value": f"{last_24_hours} infraction{'' if last_24_hours == 1 else 's'}",
                "inline": True
            },
            {
                "name": "Last 7 days",
                "value": f"{last_7_days} infraction{'' if last_24_hours == 1 else 's'}",
                "inline": True
            },
            {
                "name": "Total",
                "value": f"{total} infraction{'' if total == 1 else 's'}",
                "inline": True
            }
        ])
        return e


    def update_case_embed(
        self, 
        embed: Embed, 
        inp: str
    ) -> None:
        embed.description = f"{embed.description}\n{inp}"


    def get_log_for_case(
        self, 
        ctx: discord.Interaction, 
        case: dict
    ) -> Union[
        None, 
        str
    ]:
        if not "log_id" in case: return None

        log_id = case["log_id"]
        if log_id == None: return None

        if "jump_url" in case:
            instant = case["jump_url"]
            if instant != "": instant
        
        log_channel_id = self.db.configs.get(ctx.guild.id, "mod_log")
        if log_channel_id == "": return None

        return f"https://discord.com/channels/{ctx.guild.id}/{log_channel_id}/{log_id}"

    
    async def ban_data(
        self, 
        ctx: discord.Interaction, 
        user: Union[
            discord.Member, 
            discord.User
        ]
    ) -> Union[
        discord.guild.BanEntry, 
        None
    ]:
        try:
            data = await ctx.guild.fetch_ban(user)
        except discord.NotFound:
            return None
        else:
            return data


    @discord.app_commands.command(
        name="infractions",
        description="🛅 Shows recent server or user infractions"
    )
    @discord.app_commands.default_permissions(manage_messages=True)
    async def infractions(
        self, 
        ctx: discord.Interaction, 
        user: discord.User = None
    ) -> None:
        """
        infractions_help
        examples:
        -infractions
        -infractions 543056846601191508
        """
        if user == None: user = ctx.guild

        await ctx.response.defer(thinking=True, ephemeral=True if ctx.data.get("type") == 2 else False)

        # what to search by (guild, mod, user)?
        opt = None
        if isinstance(user, (
            discord.user.User, 
            discord.User, 
            discord.ClientUser,
            discord.Member
        )):
            m = ctx.guild.get_member(user.id)
            if m == None:
                opt = "user"
            elif m.guild_permissions.kick_members:
                opt = "mod"
            else:
                opt = "user"
        else:
            opt = "guild"

        found = sorted(
            [
                x for x in \
                [
                    self.db.cases.get_doc(f"{ctx.guild.id}-{k}") for k, v in \
                    self.db.configs.get(ctx.guild.id, "case_ids").items() if v[opt] == f"{user.id}"
                ] if x != None
            ],
            key=lambda e: int(e["id"].split("-")[-1]),
            reverse=True
        )
        if len(found) < 1: return await ctx.followup.send(embed=E(self.locale.t(ctx.guild, "no_cases", _emote="NO"), 0), ephemeral=True if ctx.data.get("type") == 2 else False)

        out = []
        for case in found:
            case_nr = case["id"].split("-")[-1]

            reason = case["reason"]; 
            reason = reason if len(reason) < 40 else f"{reason[:40]}..."
            
            timestamp = case["timestamp"]
            if isinstance(timestamp, str):
                if not timestamp.startswith("<t"):
                    dt = datetime.datetime.strptime(timestamp, "%d/%m/%Y %H:%M")
                    case["timestamp"] = dt
                    timestamp = f"<t:{round(dt.timestamp())}:d>"
                else:
                    case["timestamp"] = datetime.datetime.fromtimestamp(
                        int(
                            case["timestamp"].replace(
                                "<t:", ""
                            ).replace(
                                ">", ""
                            )
                        )
                    )
                    timestamp = f"<t:{round(case['timestamp'])}:d>"
            else:
                timestamp = f"<t:{round(timestamp.timestamp())}:d>"

            log_url = self.get_log_for_case(ctx, case)

            out.append(
                ">  {} ``{}`` {} {}"\
                .format(
                    timestamp,
                    case["type"].upper(),
                    f"[``#{case_nr}``]({log_url})" if log_url is not None else f"``#{case_nr}``",
                    reason
                )
            )

        now = datetime.datetime.utcnow()
        last_24_hours = len(
            [
                x for x in found if (
                    (now - datetime.timedelta(hours=24)) <= x["timestamp"] <= (now + datetime.timedelta(hours=24))
                ) == True
            ]
        )
        last_7_days = len(
            [
                x for x in found if (
                    (now - datetime.timedelta(days=7)) <= x["timestamp"] <= (now + datetime.timedelta(days=7))
                ) == True
            ]
        )

        embed = self.case_embed(
            opt, 
            user, 
            last_24_hours, 
            last_7_days, 
            len(found)
        )

        pages = []
        lines = 0
        max_lines = 5 if len(out) >= 5 else len(out)
        max_lines -= 1

        for i, inp in enumerate(out):
            if lines >= max_lines:
                self.update_case_embed(embed, inp); pages.append(embed)
                embed = self.case_embed(
                    opt, 
                    user, 
                    last_24_hours, 
                    last_7_days, 
                    len(found)
                ); lines = 0
            else:
                lines += 1
                if len(out) <= (i+1):
                    self.update_case_embed(embed, inp); pages.append(embed)
                else:
                    self.update_case_embed(embed, inp)

        if len(pages) > 1:
            self.bot.case_cmd_cache.update({
                f"{ctx.guild_id}-{user.id}": {
                    "pages": pages,
                    "page_number": 0
                }
            })
            view = MultiPageView(0, len(pages), user.id)
            await ctx.followup.send(content=None, embed=pages[0], view=view, ephemeral=True if ctx.data.get("type") == 2 else False)
        else:
            await ctx.followup.send(content=None, embed=pages[0], ephemeral=True if ctx.data.get("type") == 2 else False)


    @discord.app_commands.command(
        name="case",
        description="📂 Shows info about a specific case"
    )
    @discord.app_commands.default_permissions(manage_messages=True)
    async def case(
        self, 
        ctx: discord.Interaction, 
        case: str
    ) -> None:
        """
        case_help
        examples:
        -case 1234
        -case #1234
        """
        case = case.replace("#", "")
        
        raw = self.db.cases.get_doc(f"{ctx.guild.id}-{case}")
        if raw == None: return await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "case_not_found", _emote="NO"), 0))

        data = Object(raw)
        log_msg_url = self.get_log_for_case(ctx, raw)

        e = Embed(
            ctx,
            color=LOG_TYPES[data.type.replace(" ", "_").lower()]["color"],
            title=f"{data.type.upper()} | #{case}"
        )
        if log_msg_url != None:
            e.description = f"[View log message]({log_msg_url})"
        e.set_thumbnail(
            url=data.user_av
        )
        e.add_fields([
            {
                "name": "**❯ User**",
                "value": f">  <@{data.user_id}> ({data.user_id})"
            },
            {
                "name": "❯ Moderator**",
                "value": f">  <@{data.mod_id}> ({data.mod_id})"
            },
            {
                "name": "**❯ Timestamp**",
                "value": f">  <t:{round(data.timestamp.timestamp())}>"
            },
            {
                "name": "**❯ Reason**",
                "value": f">  {data.reason}"
            },
        ])

        if hasattr(data, "warns_added"):
            if int(data.warns_added) > 0: 
                e.add_field(
                    name=f"**❯ Warns {'removed' if data.type.lower() == 'unwarn' else 'added'}**",
                    value=f">  {data.warns_added}"
                )
        
        if hasattr(data, "until"):
            if data.until != "": 
                e.add_field(
                    name="**❯ Until**",
                    value=f">  {data.until}"
                )
        await ctx.response.send_message(embed=e)


    @discord.app_commands.command(
        name="check",
        description="🩺 Checks the users moderation status"
    )
    @discord.app_commands.default_permissions(manage_messages=True)
    async def check(
        self, 
        ctx: discord.Interaction, 
        user: discord.User
    ) -> None:
        """
        check_help
        examples:
        -check 543056846601191508
        """
        e = Embed(
            ctx,
            title="Info for {0.name}#{0.discriminator}".format(
                user
            )
        )
        if hasattr(user, "display_avatar"):
            e.set_thumbnail(
                url=user.display_avatar
            )

        mute_data = self.db.mutes.get_doc(f"{ctx.guild.id}-{user.id}")
        ban_data = await self.ban_data(ctx, user)
        warns = self.db.warns.get(f"{ctx.guild.id}-{user.id}", "warns")
        e.add_fields([
            {
                "name": "**❯ Status**",
                "value": ">  **Banned:** {}{} \n>  **Muted:** {} \n>  **Muted until:** {}"\
                .format(
                    "yes" if ban_data != None else "no",
                    f" (``{ban_data.reason}``)" if ban_data != None else "",
                    "yes" if mute_data != None else "no",
                    f"<t:{round(mute_data['until'].timestamp())}>" if mute_data != None else "N/A"
                )
            },
            {
                "name": "**❯ Warnings**",
                "value": ">  **Warns:** {}"\
                .format(
                    0 if warns == None else warns
                )
            }
        ])

        await ctx.response.send_message(embed=e)


async def setup(
    bot: ShardedBotInstance
) -> None: await bot.register_plugin(CasesPlugin(bot))