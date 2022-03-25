import discord
from discord.ext import commands

from toolbox import S as Object
from random import randint

from . import AutoModPlugin
from ..schemas import UserLevel
from ..types import Embed



class LevelPlugin(AutoModPlugin):
    """Plugin for all level system commands"""
    def __init__(self, bot):
        super().__init__(bot)


    def exists(self, config, guild, user, insert=True):
        if not str(user.id) in config.users:
            if insert == True:
                config.users.append(str(user.id))
                self.db.configs.update(
                    guild.id, 
                    "lvl_sys", 
                    {
                        "enabled": config.enabled,
                        "notif_mode": config.notif_mode,
                        "users": config.users
                    }
                )
                self.db.level.insert(UserLevel(guild, user))
            return False
        else:
            return True


    def get_user_data(self, guild, user):
        return Object(self.db.level.get_doc(f"{guild.id}-{user.id}"))


    def update_user_data(self, guild, user, xp, lvl):
        self.db.level.multi_update(f"{guild.id}-{user.id}", {
            "xp": xp,
            "lvl": lvl
        })


    def lb_pos(self, i):
        i = (i+1)
        if i == 1:
            return "🏆"
        elif i == 2:
            return "🥈"
        elif i == 3:
            return "🥉"
        else:
            if len(str(i)) >= 2 and int(str(i)[-2]) == 1:
                end = "th"
            else:
                if int(str(i)[-1]) == 1:
                    end = "st"
                elif int(str(i)[-1]) == 2:
                    end = "nd"
                elif int(str(i)[-1]) == 3:
                    end = "rd"
                else:
                    end = "th"
            return f"{i}{end}"


    @AutoModPlugin.listener()
    async def on_message(self, msg: discord.Message):
        if msg.guild == None: return
        if msg.author == None: return
        if msg.author.bot == True: return
        if not msg.guild.chunked:
            await msg.guild.chunk(cache=True)
        
        ctx = await self.bot.get_context(msg)
        if ctx.valid and ctx.command is not None: return
        
        config = Object(self.db.configs.get(msg.guild.id, "lvl_sys"))
        if config.enabled == False: return
        if not self.exists(
            config, 
            msg.guild, 
            msg.author
        ): return

        data = self.get_user_data(
            msg.guild, 
            msg.author
        )

        if data.lvl < 4:
            xp = randint(1, 4)
        else:
            xp = randint(2, 7)
        for_nxt_lvl = 3 * ((data.lvl - 1) ** 2) + 30
        new_xp = (data.xp + xp)

        if new_xp >= for_nxt_lvl:
            self.update_user_data(
                msg.guild,
                msg.author,
                new_xp,
                (data.lvl + 1)
            )
            if config.notif_mode == "channel":
                await msg.channel.send(self.locale.t(
                    msg.guild, 
                    "lvl_up_channel", 
                    _emote="PARTY", 
                    mention=msg.author.mention,
                    lvl=(data.lvl + 1)
                ))
            elif config.notif_mode == "dm":
                try:
                    await msg.author.send(self.locale.t(
                        msg.guild, 
                        "lvl_up_dm", 
                        _emote="PARTY", 
                        mention=msg.author.mention,
                        lvl=(data.lvl + 1),
                        guild=msg.guild.name
                    ))
                except discord.Forbidden:
                    pass
        else:
            self.update_user_data(
                msg.guild,
                msg.author,
                new_xp,
                data.lvl
            )


    @commands.command(aliases=["level", "lvl"])
    async def rank(self, ctx, user: discord.Member = None):
        """rank_help"""
        if user == None: user = ctx.message.author

        config = Object(self.db.configs.get(ctx.guild.id, "lvl_sys"))
        if config.enabled == False: 
            return await ctx.send(self.locale.t(ctx.guild, "lvl_sys_disabled", _emote="NO", prefix=self.get_prefix(ctx.guild)))

        if not self.exists(
            config, 
            ctx.guild, 
            user,
            insert=False
        ): return await ctx.send(self.locale.t(ctx.guild, "not_ranked", _emote="NO"))

        data = self.get_user_data(
            ctx.guild, 
            user
        )

        for_nxt_lvl = 3 * ((data.lvl - 1) ** 2) + 30
        for_last_lvl = 3 * ((data.lvl - 2) ** 2) + 30

        e = Embed(
            title=f"{user.name}#{user.discriminator}",
            description="**Level:** {} \n**Progress:** {} / {} \n**Total XP:** {}"\
                .format(
                    data.lvl,
                    ((for_nxt_lvl - for_last_lvl) - (for_nxt_lvl - data.xp)) if data.lvl > 1 else data.xp,
                    (for_nxt_lvl - for_last_lvl) if data.lvl > 1 else 30,
                    data.xp
                )
        )
        e.set_thumbnail(
            url=user.display_avatar
        )
        await ctx.send(embed=e)


    @commands.command(aliases=["lb"])
    @commands.cooldown(rate=1, per=30.0, type=commands.BucketType.user)
    async def leaderboard(self, ctx):
        """leaderboard_help"""
        config = Object(self.db.configs.get(ctx.guild.id, "lvl_sys"))
        if config.enabled == False: 
            return await ctx.send(self.locale.t(ctx.guild, "lvl_sys_disabled", _emote="NO", prefix=self.get_prefix(ctx.guild)))
        if len(config.users) < 1: 
            return await ctx.send(self.locale.t(ctx.guild, "no_one_ranked", _emote="NO"))

        users = [Object(x) for x in self.db.level.find({"guild": f"{ctx.guild.id}"})]
        data = sorted(users, key=lambda e: e.xp, reverse=True)

        e = Embed(
            title="Leaderboard"
        )
        e.set_thumbnail(
            url=ctx.guild.icon.url
        )
        for i, entry in enumerate(data):
            user = ctx.guild.get_member(int(entry.id.split("-")[-1]))
            if user == None: 
                user = "Unknown#0000"
            else:
                user = f"{user.name}#{user.discriminator}"

            e.add_field(
                name=f"❯ {self.lb_pos(i)}",
                value="> **• User:** {} \n> **• Level:** {} \n> **• Total XP:** {}"\
                    .format(
                        user,
                        entry.lvl,
                        entry.xp
                    )
            )
        
        await ctx.send(embed=e)


async def setup(bot): await bot.register_plugin(LevelPlugin(bot))