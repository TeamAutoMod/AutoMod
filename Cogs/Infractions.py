import asyncio
import datetime
import traceback

import discord
from discord.ext import commands

from i18n import Translator
from Utils import Logging, PermCheckers, Utils, Pages
from Utils.Converters import DiscordUser

from Database import Connector, DBUtils
from Database.Schemas import warn_schema, new_infraction

from Cogs.Base import BaseCog
from Cogs.Moderation import Moderation




db = Connector.Database()



class Infractions(BaseCog):
    def __init__(self, bot):
        super().__init__(bot)
        self.cached_targets = dict()
        self.cached_mods = dict()


    @staticmethod
    async def _warn(ctx, target, reason):
        try:
            warn_id = f"{ctx.guild.id}-{target.id}"

            if not DBUtils.get(db.warns, "warnId", warn_id, "check"):
                DBUtils.insert(db.warns, warn_schema(warn_id, 1))

                case = DBUtils.new_case()
                timestamp = datetime.datetime.utcnow().strftime("%d/%m/%Y %H:%M")
                DBUtils.insert(db.inf, new_infraction(case, ctx.guild.id, target, ctx.author, timestamp, "Ban", reason))
                
                await ctx.send(Translator.translate(ctx.guild, "user_warned", user=target, user_id=target.id, reason=reason, case=case))
                on_time = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
                await Logging.log_to_guild(ctx.guild.id, "memberLogChannel", Translator.translate(ctx.guild, "log_warn", on_time=on_time, user=target, user_id=target.id, moderator=ctx.author, moderator_id=ctx.author.id, reason=reason, case=case))
            
            warns = DBUtils.get(db.warns, "warnId", warn_id, "warns")
            if (int(warns) + 1) >= 4:
                if DBUtils.get(db.warns, "warnId", warn_id, "kicked") is True:
                    await ctx.guild.ban(user=target, reason=reason)

                    DBUtils.update(db.warns, "warnId", warn_id, "warns", 0)
                    DBUtils.update(db.warns, "warnId", warn_id, "kicked", False)

                    case = DBUtils.new_case()
                    timestamp = datetime.datetime.utcnow().strftime("%d/%m/%Y %H:%M")
                    DBUtils.insert(db.inf, new_infraction(case, ctx.guild.id, target, ctx.author, timestamp, "Ban", reason))

                    await ctx.send(Translator.translate(ctx.guild, "user_banned", user=target, user_id=target.id, reason=f"{reason} (seconds 4 warns)", case=case))
                    on_time = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
                    await Logging.log_to_guild(ctx.guild.id, "memberLogChannel", Translator.translate("log_ban", on_time=on_time, user=target, user_id=target.id, moderator=ctx.author, moderator_id=ctx.author.id, reason=f"{reason} (seconds 4 warns)", case=case))
                    return
                else:
                    await ctx.guild.kick(user=target, reason=reason)

                    DBUtils.update(db.warns, "warnId", warn_id, "warns", 0)
                    DBUtils.update(db.warns, "warnId", warn_id, "kicked", True)

                    case = DBUtils.new_case()
                    timestamp = datetime.datetime.utcnow().strftime("%d/%m/%Y %H:%M")
                    DBUtils.insert(db.inf, new_infraction(case, ctx.guild.id, target, ctx.author, timestamp, "Kick", reason))

                    await ctx.send(Translator.translate(ctx.guild, "user_kicked", user=target, user_id=target.id, reason=f"{reason} (first 4 warns)", case=case))
                    on_time = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
                    await Logging.log_to_guild(ctx.guild.id, "memberLogChannel", Translator.translate(ctx.guild, "log_kick", on_time=on_time, user=target, user_id=target.id, moderator=ctx.author, moderator_id=ctx.author.id, reason=f"{reason} (first 4 warns)", case=case))
                    return
            
            DBUtils.update(db.warns, "warnId", warn_id, "warns", (int(warns) + 1))

            case = DBUtils.new_case()
            timestamp = datetime.datetime.utcnow().strftime("%d/%m/%Y %H:%M")
            DBUtils.insert(db.inf, new_infraction(case, ctx.guild.id, target, ctx.author, timestamp, "Warn", reason))

            await ctx.send(Translator.translate(ctx.guild, "user_warned", user=target, user_id=target.id, reason=reason, case=case))
            on_time = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
            await Logging.log_to_guild(ctx.guild.id, "memberLogChannel", Translator.translate(ctx.guild, "log_warn", on_time=on_time, user=target, user_id=target.id, moderator=ctx.author, moderator_id=ctx.author.id, reason=reason, case=case))
            return
        except Exception as error:
            await ctx.send(Translator.translate(ctx.guild, "warn_error", target=target.name, error=error))


    @staticmethod
    async def _clearwarns(ctx, target, reason):
        warn_id = f"{ctx.guild.id}-{target.id}"
        if not DBUtils.get(db.warns, "warnId", warn_id, "check"):
            case = DBUtils.new_case()

            await ctx.send(Translator.translate(ctx.guild, "user_warns_cleared", user=target, user_id=target.id, reason=reason))
            on_time = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
            await Logging.log_to_guild(ctx.guild.id, "memberLogChannel", Translator.translate(ctx.guild, "log_warn_clearing", on_time=on_time, user=target, user_id=target.id, moderator=ctx.author, moderator_id=ctx.author.id, reason=reason))
            return
        else:
            DBUtils.update(db.warns, "warnId", warn_id, "kicked", False)
            DBUtils.update(db.warns, "warnId", warn_id, "warns", 0)

            case = DBUtils.new_case()

            await ctx.send(Translator.translate(ctx.guild, "user_warns_cleared", user=target, user_id=target.id, reason=reason))
            on_time = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
            await Logging.log_to_guild(ctx.guild.id, "memberLogChannel", Translator.translate(ctx.guild, "log_warn_clearing", on_time=on_time, user=target, user_id=target.id, moderator=ctx.author, moderator_id=ctx.author.id, reason=reason))


    @commands.guild_only()
    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def warn(self, ctx, user: DiscordUser, *, reason = None):
        """warn_help"""
        if reason is None:
            reason = "No reason provided"
            
        member = await Utils.get_member(ctx.bot, ctx.guild, user.id)
        if member is not None:
            if await Moderation.can_act(self, ctx, member, ctx.author):
                await self._warn(ctx, member, reason)
            else:
                await ctx.send(Translator.translate(ctx.guild, "warn_not_allowed", user=member.name))
        else:
            await ctx.send(Translator.translate(ctx.guild, "target_not_on_server"))


    @commands.guild_only()
    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def clearwarns(self, ctx, user: DiscordUser, *, reason = None):
        """clearwarns_help"""
        if reason is None:
            reason = "No reason provided"
        
        member = await Utils.get_member(ctx.bot, ctx.guild, user.id)
        if member is not None:
            if await Moderation.can_act(self, ctx, member, ctx.author):
                await self._clearwarns(ctx, member, reason)
            else:
                await ctx.send(Translator.translate(ctx.guild, "warnclearing_not_allowed", user=member.name))
        else:
            await ctx.send(Translator.translate(ctx.guild, "target_not_on_server"))



    @commands.guild_only()
    @commands.group(aliases=["infractions"])
    @commands.has_permissions(kick_members=True)
    async def inf(self, ctx):
        """inf_help"""
        if ctx.invoked_subcommand is None:
            await ctx.invoke(self.bot.get_command("help"), query="inf")

    

    @commands.guild_only()
    @inf.command()
    @commands.has_permissions(ban_members=True)
    async def find(self, ctx, user: discord.Member = None):
        """inf_find_help"""
        try:
            msg = await ctx.send(Translator.translate(ctx.guild, "fetching_inf"))
            search_by = {
                "user": "target_id",
                "guild": "guild",
                "mod": "moderator_id"
            }

            _for = ""

            filter_option = ""
            filter_value = ""
            if user is None:
                filter_option = "guild"
                filter_value = f"{ctx.guild.id}"
                _for = f"{ctx.guild.name}"
            elif PermCheckers.is_mod(user):
                filter_option = "mod"
                filter_value = f"{user.id}"
                _for = f"{user.name}"
            else:
                filter_option = "user"
                filter_value = f"{user.id}"
                _for = f"{user.name}"
            
            dest = search_by[filter_option]

            out = []
            pages = []
            basic_table = f"Case{' '*3}| Target{' '*14}| Moderator{' '*10}| Timestamp{' '*11}| Type{' '*4}| Reason\n{'='*105}"

            counters = {
                "Ban": 0,
                "Kick": 0,
                "Unban": 0,
                "Warn": 0,
                "Force Ban": 0,
                "Soft Ban": 0,
                "Clean Ban": 0,
                "Mute": 0
            }


            for doc in db.inf.find():
                if doc["guild"] == str(ctx.guild.id): # we only want infractions from this guild
                    if doc[dest] == filter_value:
                        case = doc["case"]

                        target = None
                        if doc["target_id"] in self.cached_mods:
                            target = self.cached_targets[doc["target_id"]]
                        else:
                            raw_target = await Utils.get_user(int(doc["target_id"]))
                            if raw_target is None:
                                target = "Unkown User"
                            else:
                                target = f"{raw_target.name}#{raw_target.discriminator}"
                            self.cached_targets[doc["target_id"]] = target
                        
                        mod = None
                        if doc["moderator_id"] in self.cached_mods:
                            mod = self.cached_mods[doc["moderator_id"]]
                        else:
                            raw_mod = await Utils.get_user(int(doc["moderator_id"]))
                            if raw_mod is None:
                                mod = "Unkown Mod"
                            else:
                                mod = f"{raw_mod.name}#{raw_mod.discriminator}"
                            self.cached_mods[doc["moderator_id"]] = mod

                        timestamp = doc["timestamp"]

                        inf_type = doc["type"]
                        counters[inf_type] = int(counters[inf_type]) + 1


                        reason = doc["reason"]

                        output = "{}| {}| {}| {}| {}| {}".format(
                            f"{case}{' '*abs(len(case) - 7)}",
                            f"{target}{' '*abs(len(target) - 20)}",
                            f"{mod}{' '*abs(len(mod) - 19)}",
                            f"{timestamp}{' '*abs(len(timestamp) - 20)}",
                            f"{inf_type}{' '*abs(len(inf_type) - 8)}",
                            f"{reason}"
                        )
                        out.append(output)
                    else:
                        pass
                else:
                    pass
            if len(out) < 1:
                return await msg.edit(content=Translator.translate(ctx.guild, "no_inf"))
            for page in Pages.paginate("\n".join(out), max_chars=1900, prefix="```md\n{}\n".format(basic_table), suffix="\n```"):
                pages.append(page)
            
            count_string = ', '.join('{} {}{}'.format(counters[x], x.lower(), "" if int(counters[x]) == 1 else "s") for x in counters if counters[x] != 0)

            page_count = len(pages)
            cur_page = 1
            await msg.edit(content=f"**🔎 {Translator.translate(ctx.guild, 'inf_for')} {_for}** ({cur_page}/{page_count})\n{count_string}\n{pages[cur_page-1]}")
            if page_count <= 1:
                return
            await msg.add_reaction("◀️") 
            await msg.add_reaction("▶️")

            def check(reaction, u):
                return u == ctx.author and str(reaction.emoji) in ["◀️", "▶️"]

            while True:
                try:
                    reaction, u = await self.bot.wait_for("reaction_add", timeout=60, check=check)

                    if str(reaction.emoji) == "▶️" and cur_page != pages:
                        cur_page += 1
                        await msg.edit(content=f"**🔎 {Translator.translate(ctx.guild, 'inf_for')} {_for}** ({cur_page}/{page_count})\n{count_string}\n{pages[cur_page-1]}")
                        await msg.remove_reaction(reaction, u)

                    elif str(reaction.emoji) == "◀️" and cur_page > 1:
                        cur_page -= 1
                        await msg.edit(content=f"**🔎 {Translator.translate(ctx.guild, 'inf_for')} {_for}** ({cur_page}/{page_count})\n{count_string}\n{pages[cur_page-1]}")
                        await msg.remove_reaction(reaction, u)

                    else:
                        await msg.remove_reaction(reaction, u)
                except asyncio.TimeoutError:
                    await msg.clear_reactions()
                    break
        except Exception:
            pass
        
    
    @commands.guild_only()
    @inf.command()
    @commands.has_permissions(ban_members=True)
    async def info(self, ctx, case):
        """inf_info_help"""
        case = case.split("#")[1] if len(case.split("#")) == 2 else case # in case a user adds the # in front of the the case

        try:
            guild = DBUtils.get(db.inf, "case", f"{case}", "guild")
            if guild != str(ctx.guild.id):
                # the case exists, but is not on this server
                return await ctx.send(Translator.translate(ctx.guild, "case_not_on_this_server", case=case))
            

            target = None
            target_id = DBUtils.get(db.inf, "case", f"{case}", "target_id")
            if target_id in self.cached_mods:
                target = self.cached_targets[target_id]
            else:
                raw_target = await Utils.get_user(int(target_id))
                if raw_target is None:
                    target = "Unkown User"
                else:
                    target = f"{raw_target.name}#{raw_target.discriminator}"
                self.cached_targets[target_id] = target

            mod = None
            mod_id = DBUtils.get(db.inf, "case", f"{case}", "moderator_id")
            if mod_id in self.cached_mods:
                mod = self.cached_mods[mod_id]
            else:
                raw_mod = await Utils.get_user(int(mod_id))
                if raw_mod is None:
                    mod = "Unkown Mod"
                else:
                    mod = f"{raw_mod.name}#{raw_mod.discriminator}"
                self.cached_mods[mod_id] = mod

            timestamp = DBUtils.get(db.inf, "case", f"{case}", "timestamp")

            inf_type = DBUtils.get(db.inf, "case", f"{case}", "type")

            reason = DBUtils.get(db.inf, "case", f"{case}", "reason")

            target_av = DBUtils.get(db.inf, "case", f"{case}", "target_av")


            embed = discord.Embed(
                color=discord.Color.blurple()
            )
            embed.set_thumbnail(
                url=f"{target_av}"
            )
            embed.add_field(
                name="**Type**",
                value=inf_type,
                inline=False
            )
            embed.add_field(
                name="**Reason**",
                value=reason,
                inline=True
            )
            embed.add_field(
                name="**Moderator**",
                value=mod,
                inline=True
            )
            embed.add_field(
                name="**Target**",
                value=target,
                inline=True
            )
            embed.add_field(
                name="**Moderator ID**",
                value=mod_id,
                inline=True
            )
            embed.add_field(
                name="**Target ID**",
                value=target_id,
                inline=True
            )
            embed.add_field(
                name="**Timestamp**",
                value=timestamp,
                inline=True
            )
            await ctx.send(embed=embed)
        except Exception:
            await ctx.send(Translator.translate(ctx.guild, "case_not_on_this_server", case=case))



    @commands.guild_only()
    @inf.command()
    @commands.has_permissions(ban_members=True)
    async def claim(self, ctx, case, *, reason = None):
        """inf_claim_help"""
        if reason is None:
            reason = "No reason provided"
        
        case = case.split("#")[1] if len(case.split("#")) <= 2 else case

        try:
            guild = DBUtils.get(db.inf, "case", f"{case}", "guild")
            if guild != str(ctx.guild.id):
                # the case exists, but is not on this server
                return await ctx.send(Translator.translate(ctx.guild, "case_not_on_this_server", case=case))
            
            if DBUtils.get(db.inf, "case", f"{case}", "moderator_id") == str(ctx.author.id):
                # user is already the responsible mod for this infraction
                return await ctx.send(Translator.translate(ctx.guild, "case_already_owned"))
            
            DBUtils.update(db.inf, "case", f"{case}", "moderator_id", f"{ctx.author.id}")
            DBUtils.update(db.inf, "case", f"{case}", "moderator", f"{ctx.author.name}#{ctx.author.discriminator}")
            DBUtils.update(db.inf, "case", f"{case}", "moderator_av", f"{ctx.author.avatar_url_as()}")

            await ctx.send(Translator.translate(ctx, "inf_claimed", case=case, reason=reason))
            on_time = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
            await Logging.log_to_guild(ctx.guild.id, "memberLogChannel", Translator.translate(ctx.guild, "log_inf_claim", on_time=on_time, moderator=ctx.author, moderator_id=ctx.author.id, case=case, reason=reason))
        except Exception:
            return await ctx.send(Translator.translate(ctx.guild, "case_not_on_this_server", case=case))


            


def setup(bot):
    bot.add_cog(Infractions(bot))