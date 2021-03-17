import asyncio
import datetime
import traceback

import discord
from discord.ext import commands

from i18n import Translator
from Utils import Logging, Pages, Utils
from Utils.Converters import RangedInt

from Database import Connector, DBUtils
from Database.Schemas import level_schema
from Cogs.Base import BaseCog


db = Connector.Database()


class Leveling(BaseCog):
    def __init__(self, bot):
        super().__init__(bot)
        self.running = True
        self.rank_cache = dict()
        self.cached_guilds = set()
        self.cooldown_cache = []
        self.bot.loop.create_task(self._fill_rank_cache())


    def cog_unload(self):
        self.running = False


    @staticmethod
    async def _update_data(guild_id, lvl_id, user_id):
        if not DBUtils.get(db.levels, "levelId", lvl_id, "xp"):
            DBUtils.insert(db.levels, level_schema(guild_id, user_id))


    @staticmethod
    async def _add_xp(lvl_id, xp):
        cur = DBUtils.get(db.levels, "levelId", lvl_id, "xp")
        new_xp = int(cur) + xp
        DBUtils.update(db.levels, "levelId", lvl_id, "xp", new_xp)

    
    @staticmethod
    async def _level_up(message, lvl_id, user):
        xp = DBUtils.get(db.levels, "levelId", lvl_id, "xp")
        lvl = DBUtils.get(db.levels, "levelId", lvl_id, "lvl")

        # calculations
        #TODO: It's way to easy to level up, migth have to change that
        starting_xp = 10
        counter = 0
        while counter < lvl:
            counter += 1
            if counter > 1:
                starting_xp += 40
            if counter >= lvl:
                break
        if lvl > 1:
            starting_xp += 40

        if starting_xp < xp:
            after = lvl + 1
            DBUtils.update(db.levels, "levelId", lvl_id, "lvl", after)
            try:
                await message.channel.send(Translator.translate(ctx.guild, "lvl_up", user=user, lvl=after))
            except Exception:
                pass

            lvl_roles = DBUtils.get(db.configs, "guildId", f"{message.guild.id}", "level_roles")
            if len(lvl_roles) < 1:
                return
            for l in lvl_roles:
                if str(l.split("-")[0]) == str(after):
                    try:
                        role = discord.utils.get(message.guild.roles, id=int(l.split("-")[1]))
                        await user.add_roles(role)
                        try:
                            await user.send(Translator.translate(ctx.guild, "role_added", user=user.name, role=role.name, guild=message.guild.name, lvl=after))
                        except Exception:
                            pass
                    except Exception:
                        pass

    
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.guild is None:
            return

        if DBUtils.get(db.configs, "guildId", f"{message.guild.id}", "lvlsystem") is False:
            return
        
        user = message.author
        if user.id in self.cooldown_cache:
            return
        
        prefix = DBUtils.get(db.configs, "guildId", f"{message.guild.id}", "prefix")
        if user.bot is True or f"{prefix}rank" in message.content or f"{prefix}lb" in message.content or f"{prefix}leaderboard" in message.content:
            return
        
        self.cooldown_cache.append(user.id)

        lvl_id = f"{message.guild.id}-{user.id}"
        await self._update_data(message.guild.id, lvl_id, user.id)
        await self._add_xp(lvl_id, 2)
        await self._level_up(message, lvl_id, user)

        await asyncio.sleep(5) # 5 seconds cache lifetime

        self.cooldown_cache.remove(user.id)

            

    @commands.guild_only()
    @commands.command()
    async def rank(self, ctx, user: discord.Member = None):
        """rank_help"""
        if user is None:
            user = ctx.author

        if DBUtils.get(db.configs, "guildId", f"{ctx.guild.id}", "lvlsystem") is False:
            return await ctx.send(Translator.translate(ctx.guild, "lvlsystem_disabled"))
        
        try:
            level_id = f"{ctx.guild.id}-{user.id}"

            xp = DBUtils.get(db.ranks, "levelId", level_id, "xp")
            lvl = DBUtils.get(db.ranks, "levelId", level_id, "lvl")
            needed = 10

            if lvl <= 1:
                needed_xp = needed + 1
                return await ctx.send(embed=await self._rank(ctx, user, xp, lvl, needed_xp))
            
            counter = 0
            while counter < lvl:
                counter += 1
                needed += 40
                if counter >= lvl:
                    break
            needed_xp = needed + 2
            return await ctx.send(embed=await self._rank(ctx, user, xp, lvl, needed_xp))
        except Exception:
            await ctx.send(Translator.translate(ctx.guild, "not_ranked", user=user))



    @commands.guild_only()
    @commands.command(aliases=["lb"])
    async def leaderboard(self, ctx):
        """leaderboard_help"""
        try:
            if DBUtils.get(db.configs, "guildId", f"{ctx.guild.id}", "lvlsystem") is False:
                return await ctx.send(Translator.translate(ctx.guild, "lvlsystem_disabled"))
            pages = []
            out = []
            lvl_strings = await self._position_or_lb(ctx, user=None, position=False) # we don't want to get a users position, we want the entire thing
            if len(lvl_strings) < 2:
                return await ctx.send(Translator.translate(ctx.guild, "not_enough_for_lb"))
            basic_table = "Rank | Level | Experience | User \n======================================================="
            
            msg = await ctx.send(Translator.translate(ctx.guild, "fetching_lb"))

            rank = 0
            for s in lvl_strings:
                rank += 1
                lvl = s.split("-")[0]
                xp = s.split("-")[1]
                uid = s.split("-")[2] # fun note: I'm stupid and actually put 3 here, right after I wanted to add a note that python lists are 0 index
                if uid in self.rank_cache:
                    user = self.rank_cache[uid]
                else:
                    user = ctx.guild.get_member(int(uid))
                    self.rank_cache[uid] = f"{user.name}#{user.discriminator}"
                output = f"{rank}.{' '*abs(len(str(rank)) - 4)}| {lvl}{' '*abs(len(str(lvl)) - 6)}| {xp}{' '*abs(len(str(xp)) - 11)}| {user}"
                out.append("{}".format(output))


            for page in Pages.paginate("\n".join(out), prefix="```md\n{}\n".format(basic_table), suffix="\n```"):
                pages.append(page)

            page_count = len(pages)
            cur_page = 1
            await msg.edit(content=f"**🏆 {Translator.translate(ctx.guild, 'lb')} {ctx.guild.name} ({cur_page}/{page_count}) 🏆**\n{pages[cur_page-1]}")
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
                        await msg.edit(content=f"**🏆  {Translator.translate(ctx.guild, 'lb')} {ctx.guild.name} ({cur_page}/{page_count}) 🏆**\n{pages[cur_page-1]}")
                        await msg.remove_reaction(reaction, u)

                    elif str(reaction.emoji) == "◀️" and cur_page > 1:
                        cur_page -= 1
                        await msg.edit(content=f"**🏆  {Translator.translate(ctx.guild, 'lb')} {ctx.guild.name} ({cur_page}/{page_count}) 🏆**\n{pages[cur_page-1]}")
                        await msg.remove_reaction(reaction, u)

                    else:
                        await msg.remove_reaction(reaction, u)
                except asyncio.TimeoutError:
                    await msg.clear_reactions()
                    break
        except Exception:
            pass



    @commands.guild_only()
    @commands.group()
    async def lvlrole(self, ctx):
        """lvlrole_help"""
        if ctx.invoked_subcommand is None:
            await ctx.invoke(self.bot.get_command("help"), query="lvlrole")


    @commands.guild_only()
    @lvlrole.command()
    @commands.has_permissions(ban_members=True)
    async def add(self, ctx, lvl: RangedInt(2, 200), role: discord.Role):
        "add_help"
        if DBUtils.get(db.configs, "guildId", f"{ctx.guild.id}", "lvlsystem") is False:
            return await ctx.send(Translator.translate(ctx.guild, "lvlsystem_disabled"))
        
        automod = await Utils.get_member(self.bot, ctx.guild, self.bot.user.id)
        if role.position >= automod.top_role.position:
            return await ctx.send(Translator.translate(ctx.guild, "role_too_high"))
        
        level_roles = DBUtils.get(db.configs, "guildId", f"{ctx.guild.id}", "level_roles")
        roles = [x.split("-")[1] for x in level_roles]
        levels = [x.split("-")[0] for x in level_roles]

        if str(lvl) in levels:
            return await ctx.send(Translator.translate(ctx.guild, "already_role_for_lvl", lvl=lvl))
        
        if str(role.id) is roles:
            return await ctx.send(Translator.translate(ctx.guild, "already_lvl_role", role=role))

        if len(level_roles) > 10:
            return await ctx.send(Translator.translate(ctx.guild, "max_lvl_roles"))

        level_roles.append(f"{lvl}-{role.id}")
        DBUtils.update(db.configs, "guildId", f"{ctx.guild.id}", "level_roles", level_roles)
        await ctx.send(Translator.translate(ctx.guild, "added_lvl_role", role=role, lvl=lvl))


    @commands.guild_only()
    @lvlrole.command()
    @commands.has_permissions(ban_members=True)
    async def remove(self, ctx, role: discord.Role):
        "remove_help"
        if DBUtils.get(db.configs, "guildId", f"{ctx.guild.id}", "lvlsystem") is False:
            return await ctx.send(Translator.translate(ctx.guild, "lvlsystem_disabled"))

        level_roles = DBUtils.get(db.configs, "guildId", f"{ctx.guild.id}", "level_roles")
        roles = [x.split("-")[1] for x in level_roles]
        levels = [x.split("-")[0] for x in level_roles]

        if len(level_roles) < 1:
            return await ctx.send(Translator.translate(ctx.guild, "no_lvl_roles"))

        if not str(role.id) in roles:
            return await ctx.send(Translator.translate(ctx.guild, "invalid_lvl_role", role=role))

        lvl = levels[roles.index(str(role.id))]
        level_roles.remove(f"{lvl}-{role.id}")

        DBUtils.update(db.configs, "guildId", f"{ctx.guild.id}", "level_roles", level_roles)
        await ctx.send(Translator.translate(ctx.guild, "removed_lvl_role", role=role))


    @commands.guild_only()
    @commands.command()
    async def ranks(self, ctx):
        """ranks_help"""
        if DBUtils.get(db.configs, "guildId", f"{ctx.guild.id}", "lvlsystem") is False:
            return await ctx.send(Translator.translate(ctx.guild, "lvlsystem_disabled"))
        
        level_roles = DBUtils.get(db.configs, "guildId", f"{ctx.guild.id}", "level_roles")
        if len(level_roles) < 1:
            return await ctx.send(Translator.translate(ctx.guild, "no_lvl_roles"))

        embed = discord.Embed(
            color=discord.Color.blurple(),
            title="{} {}".format(ctx.guild.name, Translator.translate(ctx.guild, "lvl_roles")),
        )
        embed.set_thumbnail(
            url=ctx.guild.icon_url
        )
        for r in level_roles:
            lvl = r.split("-")[0]
            _id = r.split("-")[1]
            if not str(_id) in [str(x.id) for x in ctx.guild.roles]:
                role = Translator.translate(ctx.guild, "deleted_role")
            else:
                role = "<@&{}>".format(_id)
            
            embed.add_field(
                name="**Level {}**".format(lvl),
                value="{}".format(role),
                inline=False
            )

        await ctx.send(embed=embed)


    

    async def _rank(self, ctx, user, xp, lvl, needed_xp):
        embed = discord.Embed(
            color=discord.Color.blurple(),
            title="{}".format(user)
        )
        embed.set_thumbnail(
            url=user.avatar_url_as()
        )
        embed.add_field(
            name="**Rank**",
            value="#{}".format(await self._position_or_lb(ctx, user, position=True)),
            inline=False
        )
        embed.add_field(
            name="**Level**",
            value="{}".format(lvl),
            inline=False
        )
        embed.add_field(
            name="**Experience**",
            value="{}/{} XP ({}%)".format(xp, needed_xp, round(((42 - (needed_xp - xp - 2)) / 42) * 100, 1)),
            inline=False
        )
        return embed


    async def _position_or_lb(self, ctx, user=None, position=False):
        unsorted = self.form_rank_str(["{}-{}-{}".format(x["lvl"], x["xp"], x["levelId"].split("-")[1]) for x in db.levels.find() if x["levelId"].split("-")[0] == str(ctx.guild.id) and ctx.guild.get_member(int(x["levelId"].split("-")[-1])) is not None]).split()
        _sorted = sorted(unsorted, key=lambda x: tuple(map(int, x[0:].split("-"))), reverse=True)
        if position:
            only_ids = [str(x.split("-")[-1]) for x in _sorted]
            return (only_ids.index(str(user.id)) + 1) # add 1, either it would return rank 0 for the rank one person
        else:
            return _sorted


    def form_rank_str(self, l): # only used for generating a leaderboard
        str1 = ""
        counter = 0
        for item in l:
            if counter == 0:
                str1 += item
                counter += 1
            else:
                str1 += " " + item
                counter += 1
        return str1


    # internal cache fill task
    async def _fill_rank_cache(self):
            await asyncio.sleep(1) # wait a bit, we got time
            valid_guilds = [x for x in self.bot.guilds if DBUtils.get(db.configs, "guildId", f"{x.id}", "lvlsystem") is True]
            while len(self.cached_guilds) < len(valid_guilds):
                for g in valid_guilds:
                    if g.id in self.cached_guilds:
                        pass
                    else:
                        for m in g.members:
                            self.rank_cache[m.id] = f"{m.name}#{m.discriminator}"
                        self.cached_guilds.add(g.id)


def setup(bot):
    bot.add_cog(Leveling(bot))