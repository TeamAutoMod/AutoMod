import discord
from discord.ext import commands

from typing import Optional
import datetime

from .PluginBlueprint import PluginBlueprint
from .Types import Reason as _Reason
from .Types import DiscordUser, Embed
from utils.Views import MultiPageView, ConfirmView



async def getLogForCase(plugin, ctx, case):
    if not "log_id" in case:
        return
    
    log_id = case["log_id"]
    if log_id == "":
        return None

    if "jump_url" in case:
        instant = case["jump_url"]
        if instant != "":
            return instant
        
    log_channel_id = plugin.db.configs.get(ctx.guild.id, "mod_log")
    if log_channel_id == "":
        return None

    return f"https://discord.com/channels/{ctx.guild.id}/{log_channel_id}/{log_id}"


async def deleteLogMessage(plugin, ctx, log_id):
    if log_id is None:
        return
    log_channel_id = plugin.db.configs.get(ctx.guild.id, "mod_log")
    if log_channel_id == "":
        return

    log_channel = await plugin.bot.utils.getChannel(ctx.guild, log_channel_id)
    if log_channel is None:
        return

    msg = await log_channel.fetch_message(int(log_id))
    if msg is None:
        return
    
    try:
        await msg.delete()
    except Exception:
        pass


async def updateLogMessage(plugin, ctx, log_id, case, reason):
    if log_id is None:
        return
    log_channel_id = plugin.db.configs.get(ctx.guild.id, "mod_log")
    if log_channel_id == "":
        return await ctx.send(plugin.i18next.t(ctx.guild, "no_mod_log_set", _emote="NO"))

    log_channel = await plugin.bot.utils.getChannel(ctx.guild, log_channel_id)
    if log_channel is None:
        return await ctx.send(plugin.i18next.t(ctx.guild, "no_mod_log_set", _emote="NO"))

    try:
        msg = await log_channel.fetch_message(int(log_id))
    except Exception:
        return await ctx.send(plugin.i18next.t(ctx.guild, "log_not_found", _emote="NO"))
    if msg is None:
        return await ctx.send(plugin.i18next.t(ctx.guild, "log_not_found", _emote="NO"))
    
    try:
        current = plugin.db.inf.get(f"{ctx.guild.id}-{case}", "reason")
        e = msg.embeds[0]
        e.description = e.description.replace(f"**Reason:** {current}", f"**Reason:** {reason}")
        await msg.edit(embed=e)
    except Exception as ex:
        await ctx.send(plugin.i18next.t(ctx.guild, "log_edit_failed", _emote="NO", exc=ex))
    else:
        plugin.db.inf.update(f"{ctx.guild.id}-{case}", "reason", reason)
        await ctx.send(plugin.i18next.t(ctx.guild, "log_edited", _emote="YES", case=case))


def create_embed(option, user):
    main_embed = Embed(
        title="Recent cases"
    )
    if option == "guild":
        if user.icon != None:
            main_embed.set_thumbnail(
                url=user.icon.url
            )
    else:
        main_embed.set_thumbnail(
            url=user.display_avatar
        )
    main_embed.add_field(
        name="❯ History",
        value=""
    )
    return main_embed


def update_embed(main_embed, inp):
    main_embed._fields[0]["value"] = main_embed._fields[0]["value"] + f"\n{inp}"
    return None


options = {
    "guild": "guild",
    "user": "user",
    "mod": "mod"
}


class CasesPlugin(PluginBlueprint):
    def __init__(self, bot):
        super().__init__(bot)


    @commands.command()
    @commands.has_guild_permissions(kick_members=True)
    async def cases(
        self,
        ctx,
        user: DiscordUser = None
    ):
        """cases_help"""
        # If nothing is passed, we check for all the guilds cases
        if user is None:
            user = ctx.guild
        
        message = await ctx.send(embed=Embed(description=self.i18next.t(ctx.guild, "searching", _emote="SEARCH")))
        # Check what we should search by
        option = None
        if isinstance(user, discord.Guild):
            option = options["guild"]
        if isinstance(user, discord.user.User) or isinstance(user, discord.User) or isinstance(user, discord.user.ClientUser):
            member = ctx.guild.get_member(user.id)
            if member is None:
                option = options["user"]
            elif member.guild_permissions.kick_members:
                option = options["mod"]
            else:
                option = options["user"]
        else:
            option = options["guild"]

        raw = [
            self.db.inf.get_doc(f"{ctx.guild.id}-{k}") for k, v in self.db.configs.get(ctx.guild.id, "case_ids").items() if v[option] == f"{user.id}"
        ]
        results = sorted(
            raw, 
            key=lambda e: int(e['id'].split("-")[-1]), 
            reverse=True
        )
        if len(results) < 1:
            return await message.edit(embed=Embed(description=self.i18next.t(ctx.guild, "no_cases_found", _emote="NO")))

        out = list()
        counts = {
            "warn": 0,
            "mute": 0,
            "kick": 0,
            "ban": 0
        }
        for e in results:
            if e["type"].lower() in counts:
                counts.update({
                    e["type"].lower(): (counts[e["type"].lower()] + 1)
                })

            case = e['id'].split("-")[-1]

            reason = e["reason"]
            reason = reason if len(reason) < 40 else f"{reason[:40]}..."

            case_type = e["type"]
            if "restriction" in case_type.lower():
                case_type = "restriction"

            timestamp = e["timestamp"]
            if isinstance(timestamp, str):
                if not timestamp.startswith("<t"):
                    dt = datetime.datetime.strptime(timestamp, "%d/%m/%Y %H:%M")
                    timestamp = f"<t:{round(dt.timestamp())}>"
                # else:
                    # timestamp = timestamp.replace(">", ":d>")
            else:
                timestamp = f"<t:{round(timestamp.timestamp())}>"


            log_url = await getLogForCase(self, ctx, e)

            out.append(
                "• {} ``{}`` {} {}"\
                .format(
                    timestamp,
                    case_type.upper(),
                    f"[#{case}]({log_url})" if log_url is not None else f"#{case}",
                    reason
                )
            )

        main_embed = create_embed(option, user)

        pages = []
        lines = 0
        max_lines = 5 if len(out) >= 5 else len(out)
        max_lines -= 1
        for i, inp in enumerate(out):
            if lines >= max_lines:
                update_embed(main_embed, inp)
                pages.append(main_embed)
                main_embed = create_embed(option, user)
                lines = 0
            else:
                lines += 1
                if len(out) <= i+1:
                    update_embed(main_embed, inp)
                    pages.append(main_embed)
                else:
                    update_embed(main_embed, inp)
        
        text = []
        for k, v in counts.items():
            text.append(f"{v} {k if v == 1 else f'{k}s'}")
        text = ", ".join(text[:3]) + f" & {text[-1]}"

        for em in pages:
            em.set_footer(text=text)

        if len(pages) > 1:
            data = {
                "pages": pages,
                "page_number": 0
            }
            self.bot.case_cache.update({
                message.id: data
            })
            view = MultiPageView(0, len(pages))
            await message.edit(content=None, embed=pages[0], view=view)
        else:
            await message.edit(content=None, embed=pages[0])


    @commands.group()
    @commands.has_guild_permissions(kick_members=True)
    async def case(
        self,
        ctx
    ):
        """case_help"""
        if ctx.subcommand_passed is None:
            _help = self.bot.get_command("help")
            await _help.__call__(ctx, query="case")


    @case.command()
    @commands.has_guild_permissions(kick_members=True)
    async def info(
        self,
        ctx,
        case
    ):
        """case_info_help"""
        # In case a user adds the # in front of the case
        case = case.split("#")[1] if len(case.split("#")) == 2 else case

        case_id = f"{ctx.guild.id}-{case}"
        if not self.db.inf.exists(case_id):
            return await ctx.send(self.i18next.t(ctx.guild, "case_not_found", _emote="NO"))
        
        _case = [x for x in self.db.inf.find({"id": case_id})][0]

        target = await self.bot.utils.getUser(_case["target_id"])
        target = target if target is not None else "Unknown#0000"

        mod = await self.bot.utils.getUser(_case["moderator_id"])
        mod = mod if mod is not None else "Unknown#0000"

        reason = _case["reason"]
        reason = reason if len(reason) < 50 else f"{reason[:50]}..."

        timestamp = _case["timestamp"]
        case_type = _case["type"]

        e = Embed()
        e.set_thumbnail(
            url=_case["target_av"]
        )
        e.add_field(
            name="❯ Case",
            value=f"``#{case}``"
        )
        e.add_field(
            name="❯ Type",
            value=f"``{case_type}``"
        )
        e.add_field(
            name="❯ Target",
            value=f"``{target}`` ({_case['target_id']})",
        )
        e.add_field(
            name="❯ Moderator",
            value=f"``{mod}`` ({_case['moderator_id']})",
        )
        e.add_field(
            name="❯ Reason",
            value=f"``{reason}``"
        )
        if not timestamp.startswith("<t"):
            dt = datetime.datetime.strptime(timestamp, "%d/%m/%Y %H:%M")
            timestamp = f"<t:{round(dt.timestamp())}>"
        e.add_field(
            name="❯ Timestamp",
            value=f"{timestamp}"
        )

        await ctx.send(embed=e)


    @case.command()
    @commands.has_guild_permissions(kick_members=True)
    async def claim(
        self,
        ctx,
        case
    ):
        """case_claim_help"""
        # In case a user adds the # in front of the case
        case = case.split("#")[1] if len(case.split("#")) == 2 else case

        case_id = f"{ctx.guild.id}-{case}"
        if not self.db.inf.exists(case_id):
            return await ctx.send(self.i18next.t(ctx.guild, "case_not_found", _emote="NO"))

        _case = [x for x in self.db.inf.find({"id": case_id})][0]
        if _case["moderator_id"] == str(ctx.author.id):
            return await ctx.send(self.i18next.t(ctx.guild, "case_already_owned", _emote="WARN"))

        if _case["target_id"] == str(ctx.author.id):
            return await ctx.send(self.i18next.t(ctx.guild, "case_target", _emote="NO"))

        self.db.inf.update(case_id, "moderator_id", f"{ctx.author.id}")
        self.db.inf.update(case_id, "moderator_av", f"{ctx.author.display_avatar}")

        case_ids = self.db.configs.get(f"{ctx.guild.id}", "case_ids")
        case_ids[case_id.split("-")[1]]["mod"] = f"{ctx.author.id}"
        self.db.configs.update(f"{ctx.guild.id}", "case_ids", case_ids)

        await ctx.send(self.i18next.t(ctx.guild, "case_claimed", _emote="YES", case=case))


    @case.command()
    @commands.has_guild_permissions(administrator=True)
    async def delete(
        self,
        ctx,
        case
    ):
        """case_delete_help"""
        # In case a user adds the # in front of the case
        case = case.split("#")[1] if len(case.split("#")) == 2 else case

        case_id = f"{ctx.guild.id}-{case}"
        if not self.db.inf.exists(case_id):
            return await ctx.send(self.i18next.t(ctx.guild, "case_not_found", _emote="NO"))

        message = None
        
        async def confirm(interaction):
            log_id = self.db.inf.get(case_id, "log_id")
            self.db.inf.delete(case_id)

            case_ids = self.db.configs.get(f"{ctx.guild.id}", "case_ids")
            del case_ids[case_id.split("-")[1]]
            self.db.configs.update(f"{ctx.guild.id}", "case_ids", case_ids)

            await deleteLogMessage(self, ctx, log_id)
            await interaction.response.edit_message(
                content=self.i18next.t(ctx.guild, "case_deleted", _emote="YES", case=case), 
                embed=None, 
                view=None
            )

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

        
        e = Embed(
            description=self.i18next.t(ctx.guild, "case_delete_description", case=case)
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
    @commands.has_guild_permissions(kick_members=True)
    async def reason(
        self,
        ctx,
        case: Optional[int],
        *,
        reason: _Reason
    ):
        """reason_help"""
        if case is None:
            recent = sorted([x for x in self.db.inf.find({"guild": f"{ctx.guild.id}"}) if x["reason"] == self.i18next.t(ctx.guild, "no_reason") or x["reason"] == "No reason provided"], key=lambda k: int(k['id'].split('-')[1]))
            if len(recent) < 1:
                return await ctx.send(self.i18next.t(ctx.guild, "no_recent_case", _emote="NO"))
            else:
                return await updateLogMessage(self, ctx, recent[-1]["log_id"], recent[-1]["id"].split("-")[1], reason)
        else:
            case = str(case)
            case = case.split("#")[1] if len(case.split("#")) == 2 else case
            if not self.db.inf.exists(f"{ctx.guild.id}-{case}"):
                return await ctx.send(self.i18next.t(ctx.guild, "case_not_found", _emote="NO"))

            log_id = self.db.inf.get(f"{ctx.guild.id}-{case}", "log_id")
            await updateLogMessage(self, ctx, log_id, case, reason)



def setup(bot):
    bot.add_cog(CasesPlugin(bot))