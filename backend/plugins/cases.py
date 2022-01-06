from itertools import count
import discord
from discord.ext import commands

import datetime
import logging; log = logging.getLogger()

from . import AutoModPlugin
from ..types import DiscordUser, Embed
from ..views import MultiPageView



class CasesPlugin(AutoModPlugin):
    """Plugin for internal/log events"""
    def __init__(self, bot):
        super().__init__(bot)


    def case_embed(self, opt, user):
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
        return e


    def update_case_embed(self, embed: Embed, inp):
        embed.description = f"{embed.description}\n{inp}"


    def get_log_for_case(self, ctx, case):
        if not "log_id" in case: return None
        if case["log_id"] == None: return

        if "jump_url" in case:
            instant = case["jump_url"]
            if instant != "": instant
        
        log_channel_id = self.db.configs.get(ctx.guild.id, "mod_log")
        if log_channel_id == "": return None

        return "https://discord.com/channels/{ctx.guild.id}/{log_channel_id}/{log_id}"


    @commands.command(aliases=["history"])
    @commands.has_guild_permissions(kick_members=True)
    async def cases(self, ctx, user: DiscordUser = None):
        """cases_help"""
        if user == None: user = ctx.guild

        msg = await ctx.send(embed=Embed(
            description=self.locale.t(ctx.guild, "searching", _emote="SEARCH")
        ))

        # what do search by (guild, mod, user)?
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
        if len(found) < 1: return await msg.edit(embed=Embed(
            description=self.locale.t(ctx.guild, "no_cases", _emote="NO")
        ))

        out = []
        counts = {
            "warn": 0,
            "mute": 0,
            "kick": 0,
            "ban": 0
        }

        for case in found:
            if case["type"] in counts:
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
                    timestamp = f"<t:{round(dt.timestamp())}>"
            else:
                timestamp = f"<t:{round(timestamp.timestamp())}>"

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

        embed = self.case_embed(opt, user)

        pages = []
        lines = 0
        max_lines = 5 if len(out) >= 5 else len(out)
        max_lines -= 1

        for i, inp in enumerate(out):
            if lines >= max_lines:
                self.update_case_embed(embed, inp); pages.append(embed)
                embed = self.case_embed(opt, user); lines = 0
            else:
                lines += 1
                if len(out) <= (i+1):
                    self.update_case_embed(embed, inp); pages.append(embed)
                else:
                    self.update_case_embed(embed, inp)
        
        text = []
        for k, v in counts.items():
            text.append(f"{v} {k if v == 1 else f'{k}s'}")
        text = ", ".join(text[:3]) + f" & {text[-1]}"

        for em in pages: em.set_footer(text=text)

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


def setup(bot): bot.register_plugin(CasesPlugin(bot))