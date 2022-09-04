import discord
from discord.ext import commands

from toolbox import S as Object
from random import randint
from typing import Union, Literal

from .. import AutoModPluginBlueprint, ShardedBotInstance
from ...schemas import UserLevel
from ...types import Embed, E



class LevelPlugin(AutoModPluginBlueprint):
    """Plugin for all level system commands"""
    def __init__(
        self, 
        bot: ShardedBotInstance,
    ) -> None:
        super().__init__(bot, requires_premium=True)


    def exists(
        self, 
        config: Object, 
        guild: discord.Guild, 
        user: Union[
            discord.Member,
            discord.User
        ], 
        insert: bool = True
    ) -> bool:
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


    def get_user_data(
        self, 
        guild: discord.Guild, 
        user: Union[
            discord.Member,
            discord.User
        ], 
    ) -> Object:
        return Object(self.db.level.get_doc(f"{guild.id}-{user.id}"))


    def update_user_data(
        self, 
        guild: discord.Guild, 
        user: Union[
            discord.Member,
            discord.User
        ],
        xp: int, 
        lvl: int
    ) -> None:
        self.db.level.multi_update(f"{guild.id}-{user.id}", {
            "xp": xp,
            "lvl": lvl
        })


    def lb_pos(
        self, 
        i: int
    ) -> str:
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


    def has_premium(
        self,
        guild: discord.Guild
    ) -> None:
        return self.db.configs.get(guild.id, "premium")


    @AutoModPluginBlueprint.listener()
    async def on_message(
        self, 
        msg: discord.Message
    ) -> None:
        if msg.guild == None: return
        if msg.author == None: return
        if msg.author.bot == True: return
        if not self.has_premium(msg.guild): return
        if not msg.guild.chunked:
            await self.bot.chunk_guild(msg.guild)
        
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
                await msg.channel.send(embed=E(self.locale.t(
                    msg.guild, 
                    "lvl_up_channel", 
                    _emote="PARTY", 
                    mention=msg.author.mention,
                    lvl=(data.lvl + 1)
                ), 2))
            elif config.notif_mode == "dm":
                try:
                    await msg.author.send(embed=E(self.locale.t(
                        msg.guild, 
                        "lvl_up_dm", 
                        _emote="PARTY", 
                        mention=msg.author.mention,
                        lvl=(data.lvl + 1),
                        guild=msg.guild.name
                    ), 2))
                except discord.Forbidden:
                    pass
        else:
            self.update_user_data(
                msg.guild,
                msg.author,
                new_xp,
                data.lvl
            )


    @discord.app_commands.command(
        name="lvlsys",
        description="🏆 Configure the level system"
    )
    @discord.app_commands.describe(
        enabled="Whether the level system should be enabled or disabled",
        notifications="Where users should be notified when leveling up"
    )
    @discord.app_commands.default_permissions(manage_guild=True)
    async def lvlsys(
        self,
        ctx: discord.Interaction,
        enabled: Literal[
            "True",
            "False"
        ] = None,
        notifications: Literal[
            "Channel",
            "DM"
        ] = None
    ) -> None:
        if not self.has_premium(ctx.guild): return await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "need_premium", _emote="NO"), 0))

        config = self.db.configs.get(ctx.guild.id, "lvl_sys")
        if enabled == None and notifications == None:
            await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "lvl_sys_status", status="enabled" if config["enabled"] == True else "disabled"), 2))
        else:
            if enabled != None:
                if enabled.lower() == "true":
                    config["enabled"] = True
                else:
                    config["enabled"] = False
            
            if notifications != None:
                config["notif_mode"] = notifications.lower()

            self.db.configs.update(ctx.guild.id, "lvl_sys", config)
            await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "changed_lvl_sys_status", _emote="YES", status="enabled" if config["enabled"] == True else "disabled", notifs=notifications), 1))


    @discord.app_commands.command(
        name="rank",
        description="⭐ View your server rank"
    )
    async def rank(
        self, 
        ctx: discord.Interaction, 
        user: discord.Member = None
    ) -> None:
        """
        rank_help
        examples:
        -rank
        -rank paul#0009
        """
        if not self.has_premium(ctx.guild): return await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "need_premium", _emote="NO"), 0))
        if user == None: user = ctx.user

        config = Object(self.db.configs.get(ctx.guild.id, "lvl_sys"))
        if config.enabled == False: return await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "lvl_sys_disabled", _emote="NO", prefix="/"), 0))

        if not self.exists(
            config, 
            ctx.guild, 
            user,
            insert=False
        ): return await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "not_ranked", _emote="NO"), 0))

        data = self.get_user_data(
            ctx.guild, 
            user
        )

        for_nxt_lvl = 3 * ((data.lvl - 1) ** 2) + 30
        for_last_lvl = 3 * ((data.lvl - 2) ** 2) + 30

        e = Embed(
            ctx,
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
        await ctx.response.send_message(embed=e)


    @discord.app_commands.command(
        name="leaderboard",
        description="📜 View the server's leaderboard"
    )
    async def leaderboard(
        self, 
        ctx: discord.Interaction
    ) -> None:
        """
        leaderboard_help
        examples:
        -leaderboard
        """
        if not self.has_premium(ctx.guild): return await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "need_premium", _emote="NO"), 0))
        config = Object(self.db.configs.get(ctx.guild.id, "lvl_sys"))

        if config.enabled == False: return await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "lvl_sys_disabled", _emote="NO", prefix="/"), 0))
        if len(config.users) < 1: return await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "no_one_ranked", _emote="NO"), 0))

        users = [Object(x) for x in self.db.level.find({"guild": f"{ctx.guild.id}"})]
        data = sorted(users, key=lambda e: e.xp, reverse=True)

        e = Embed(
            ctx,
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
        
        await ctx.response.send_message(embed=e)


async def setup(
    bot: ShardedBotInstance
) -> None: await bot.register_plugin(LevelPlugin(bot))