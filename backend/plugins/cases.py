import discord
from discord.ext import commands

import datetime
from typing import Union
from toolbox import S as Object
import logging; log = logging.getLogger()

from . import AutoModPlugin
from ..types import DiscordUser, Embed
from ..views import MultiPageView



class CasesPlugin(AutoModPlugin):
    """Plugin for internal/log events"""
    def __init__(self, bot):
        super().__init__(bot)


    def case_embed(self, opt, user, last_24_hours, last_7_days, total):
        e = Embed(
            title="Recent Infractions",
            description=""
        )
        if opt == "guild":
            if user.icon != None:
                e.set_thumbnail(
                    url=user.icon.url
                )
        else:
            e.set_thumbnail(
                url=user.display_avatar
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


    def update_case_embed(self, embed: Embed, inp):
        embed.description = f"{embed.description}\n{inp}"


    def get_log_for_case(self, ctx, case):
        if not "log_id" in case: return None

        log_id = case["log_id"]
        if log_id == None: return

        if "jump_url" in case:
            instant = case["jump_url"]
            if instant != "": instant
        
        log_channel_id = self.db.configs.get(ctx.guild.id, "mod_log")
        if log_channel_id == "": return None

        return f"https://discord.com/channels/{ctx.guild.id}/{log_channel_id}/{log_id}"

    
    async def ban_data(self, ctx, user):
        try:
            data = await ctx.guild.fetch_ban(user)
        except discord.NotFound:
            return None
        else:
            return data


    @commands.command(aliases=["history", "cases"])
    @AutoModPlugin.can("manage_messages")
    async def infractions(self, ctx, user: Union[DiscordUser, discord.Member, discord.Guild] = None):
        """
        infractions_help
        examples:
        -infractions
        -infractions @paul#0009
        -infractions 543056846601191508
        """
        if user == None: user = ctx.guild

        msg = await ctx.send(self.locale.t(ctx.guild, "searching", _emote="SEARCH"))

        # what to search by (guild, mod, user)?
        opt = None
        if isinstance(user, discord.Guild):
            opt = "guild"
        if isinstance(user, (
            discord.user.User, 
            discord.User, 
            discord.ClientUser)
        ):
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
        if len(found) < 1: return await msg.edit(self.locale.t(ctx.guild, "no_cases", _emote="NO"))

        out = []
        counts = {
            "warn": 0,
            "mute": 0,
            "kick": 0,
            "ban": 0
        }

        for case in found:
            if case["type"].lower() in counts:
                counts.update({
                    case["type"].lower(): (counts[case["type"].lower()] + 1)
                })
            
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
            else:
                timestamp = f"<t:{round(timestamp.timestamp())}:d>"

            log_url = self.get_log_for_case(ctx, case)

            out.append(
                 "• {} ``{}`` {} {}"\
                .format(
                    timestamp,
                    case["type"].upper(),
                    f"[#{case_nr}]({log_url})" if log_url is not None else f"#{case_nr}",
                    reason
                )
            )

        now = datetime.datetime.utcnow()
        last_24_hours = len(
            [
                x for x in found if ((now - datetime.timedelta(hours=24)) <= x["timestamp"] <= (now + datetime.timedelta(hours=24))) == True
            ]
        )
        last_7_days = len(
            [
                x for x in found if ((now - datetime.timedelta(days=7)) <= x["timestamp"] <= (now + datetime.timedelta(days=7))) == True
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
                msg.id: {
                    "pages": pages,
                    "page_number": 0
                }
            })
            view = MultiPageView(0, len(pages))
            await msg.edit(content=None, embed=pages[0], view=view)
        else:
            await msg.edit(content=None, embed=pages[0])


    @commands.command()
    @AutoModPlugin.can("manage_messages")
    async def case(self, ctx, case: str):
        """
        case_help
        examples:
        -case 1234
        -case #1234
        """
        case = case.replace("#", "")
        
        raw = self.db.cases.get_doc(f"{ctx.guild.id}-{case}")
        if raw == None: return await ctx.send(self.locale.t(ctx.guild, "case_not_found", _emote="NO"))

        data = Object(raw)
        log_msg_url = self.get_log_for_case(ctx, raw)

        e = Embed(
            title=f"{data.type.upper()} #{case}"
        )
        if log_msg_url != None:
            e.description = f"[View log message]({log_msg_url})"
        e.set_thumbnail(
            url=data.user_av
        )
        e.add_fields([
            {
                "name": "❯ User",
                "value": f"<@{data.user_id}> ({data.user_id})"
            },
            {
                "name": "❯ Moderator",
                "value": f"<@{data.mod_id}> ({data.mod_id})"
            },
            {
                "name": "❯ Timestamp",
                "value": f"<t:{round(data.timestamp.timestamp())}>"
            },
            {
                "name": "❯ Reason",
                "value": f"{data.reason}"
            },
        ])
        await ctx.send(embed=e)


    @commands.command(aliases=["fetch"])
    @AutoModPlugin.can("manage_messages")
    async def check(self, ctx, user: DiscordUser):
        """
        check_help
        examples:
        -check @paul#0009
        -check 543056846601191508
        """
        e = Embed(
            title="Info for {0.name}#{0.discriminator}".format(
                user
            )
        )
        if hasattr(user, "display_avatar"):
            e.set_thumbnail(
                url=user.display_avatar
            )

        Y = self.bot.emotes.get("YES")
        N = self.bot.emotes.get("NO")
        mute_data = self.db.mutes.get_doc(f"{ctx.guild.id}-{user.id}")
        ban_data = await self.ban_data(ctx, user)
        warns = self.db.warns.get(f"{ctx.guild.id}-{user.id}", "warns")
        e.add_fields([
            {
                "name": "❯ Status",
                "value": "> **• Banned:** {} \n> **• Reason:** {} \n> **• Muted:** {} \n> **• Muted until:** {}"\
                .format(
                    Y if ban_data != None else N,
                    ban_data.reason if ban_data != None else "N/A",
                    Y if mute_data != None else N,
                    f"<t:{round(mute_data['until'].timestamp())}>" if mute_data != None else "N/A"
                )
            },
            {
                "name": "❯ Stats",
                "value": "> **• Warns:** {}"\
                .format(
                    0 if warns == None else warns
                )
            }
        ])

        await ctx.send(embed=e)


async def setup(bot): await bot.register_plugin(CasesPlugin(bot))
