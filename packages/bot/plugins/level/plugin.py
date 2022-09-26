# type: ignore

import discord
from discord.ext import commands

from toolbox import S as Object
from random import randint
from typing import OrderedDict, Union, Literal

from .. import AutoModPluginBlueprint, ShardedBotInstance
from ...schemas import UserLevel
from ...types import Embed, E



MAX_BONUS_XP = 500000


class LevelPlugin(AutoModPluginBlueprint):
    """Plugin for all level system commands"""
    def __init__(
        self, 
        bot: ShardedBotInstance,
    ) -> None:
        super().__init__(bot, requires_premium=False) # set this to true for now (testing etc)
        self._processing = []


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
            return "**❯** 🏆"
        elif i == 2:
            return "**❯** 🥈"
        elif i == 3:
            return "**❯** 🥉"
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
            return f"**❯ __{i}{end}__**"


    def has_premium(
        self,
        guild: discord.Guild
    ) -> None:
        return self.db.configs.get(guild.id, "premium")


    def get_xp_for_next_lvl(
        self,
        lvl: int
    ):
        if lvl > 1:
            return int((50 * ((lvl - 1) ** 2)) + (50 * (lvl - 1)))
        else:
            return 50


    async def add_reward(
        self,
        guild: discord.Guild,
        user: discord.Member,
        level: int,
        config: Object
    ) -> None:
        if len(config.rewards) < 1: return

        rewards = OrderedDict(
            sorted({
                k: v for k, v in config.rewards.items() if int(k) <= int(level)
            }.items())
        )
        if len(rewards) > 0:
            new_role = guild.get_role(int(list(rewards.values())[-1]))
            if new_role != None:
                try:
                    await user.add_roles(role)
                except Exception:
                    pass
                else:
                    try:
                        await user.send(embed=E(self.locale.t(guild, "new_reward", _emote="PARTY", role=role.name, lvl=level, server=guild.name), 2))
                    except Exception:
                        pass
                finally:
                    if config.reward_mode == "single":
                        to_rm = []
                        for r in [x for x in user.roles if x != guild.default_role]:
                            if r.id != new_role.id:
                                if r.id in [int(_) for _ in list(rewards.values())]:
                                    to_rm.append(r)
                        
                        if len(to_rm) > 0:
                            try:
                                await user.remove_roles(*to_rm)
                            except Exception:
                                pass


    @AutoModPluginBlueprint.listener()
    async def on_message(
        self, 
        msg: discord.Message
    ) -> None:
        if msg.guild == None: return
        if msg.author == None: return
        if msg.author.bot == True: return
        # if not self.has_premium(msg.guild): return
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

        pid = f"{msg.guild.id}-{msg.author.id}"
        if pid in self._processing: return
        else: self._processing.append(pid)

        data = self.get_user_data(
            msg.guild, 
            msg.author
        )

        xp = randint(5, 15)
        for_nxt_lvl = self.get_xp_for_next_lvl(data.lvl)
        new_xp = (data.xp + xp)

        if new_xp >= for_nxt_lvl:
            await self.add_reward(
                msg.guild, 
                msg.author, 
                (data.lvl + 1), 
                config
            )
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

        if pid in self._processing:
            self._processing.remove(pid)


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
        # if not self.has_premium(ctx.guild): return await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "need_premium", _emote="NO"), 0))

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
            else:
                notifications = config["notif_mode"].title()

            self.db.configs.update(ctx.guild.id, "lvl_sys", config)
            await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "changed_lvl_sys_status", _emote="YES", status="enabled" if config["enabled"] == True else "disabled", notifs=notifications), 1))


    @discord.app_commands.command(
        name="reset",
        description="🔮 Resets a user back to level one"
    )
    @discord.app_commands.default_permissions(manage_guild=True)
    async def reset(
        self,
        ctx: discord.Interaction,
        user: discord.Member
    ) -> None:
        """
        reset_help
        examples:
        -reset @paul#0009
        """
        # if not self.has_premium(ctx.guild): return await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "need_premium", _emote="NO"), 0))

        config = Object(self.db.configs.get(ctx.guild.id, "lvl_sys"))
        if config.enabled == False: return await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "lvl_sys_disabled", _emote="NO", prefix="/"), 0))

        if self.exists(config, ctx.guild, user):
            self.update_user_data(
                ctx.guild,
                user,
                1,
                1
            )
        await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "reset_user", _emote="YES"), 1))


    @discord.app_commands.command(
        name="rewards",
        description="🌱 Shows the current role rewards"
    )
    async def role_reward_show(
        self,
        ctx: discord.Interaction
    ) -> None:
        """
        role_reward_show_help
        examples:
        -rewards
        """
        # if not self.has_premium(ctx.guild): return await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "need_premium", _emote="NO"), 0))

        config = Object(self.db.configs.get(ctx.guild.id, "lvl_sys"))
        if config.enabled == False: return await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "lvl_sys_disabled", _emote="NO", prefix="/"), 0))

        if len(config.rewards) < 1:
            await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "no_rewards", _emote="NO"), 0))
        else:
            e = Embed(
                ctx,
                title="Role Rewards"
            )
            for lvl, role in dict(sorted(config.rewards.items(), key=lambda e: int(e[0]))).items():
                e.add_field(
                    name=f"__**Level {lvl}**__",
                    value=f"> <@&{role}>"
                )
            await ctx.response.send_message(embed=e)


    role_reward = discord.app_commands.Group(
        name="reward",
        description="🌱 Manage role rewards",
        default_permissions=discord.Permissions(manage_guild=True)
    )
    @role_reward.command(
        name="add",
        description="✅ Adds a new role reward for the specified level"
    )
    @discord.app_commands.default_permissions(manage_guild=True)
    async def role_reward_add(
        self,
        ctx: discord.Interaction,
        level: discord.app_commands.Range[
            int,
            1,
            100
        ],
        role: discord.Role
    ) -> None:
        """
        rol_reward_add_help
        examples:
        -reward add 5 @Level5
        -reward add 10 @Advanced
        """
        # if not self.has_premium(ctx.guild): return await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "need_premium", _emote="NO"), 0))

        config = self.db.configs.get(ctx.guild.id, "lvl_sys")
        if config["enabled"] == False: return await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "lvl_sys_disabled", _emote="NO", prefix="/"), 0))

        if len(config["rewards"]) >= 15: return await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "max_rewards", _emote="NO"), 0))

        if str(role.id) in list(config["rewards"].values()):
            await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "alr_reward", _emote="NO"), 0))
        else:
            config["rewards"].update({
                str(level): str(role.id)
            })
            self.db.configs.update(ctx.guild.id, "lvl_sys", config)
            await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "added_reward", _emote="YES", role=role.mention, lvl=level), 1))


    @role_reward.command(
        name="remove",
        description="❌ Removes the reward for the specified level"
    )
    @discord.app_commands.default_permissions(manage_guild=True)
    async def role_reward_remove(
        self,
        ctx: discord.Interaction,
        level: discord.app_commands.Range[
            int,
            1,
            100
        ]
    ) -> None:
        """
        role_reward_remove_help
        examples:
        -reward remove 5
        """
        # if not self.has_premium(ctx.guild): return await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "need_premium", _emote="NO"), 0))

        config = self.db.configs.get(ctx.guild.id, "lvl_sys")
        if config["enabled"] == False: return await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "lvl_sys_disabled", _emote="NO", prefix="/"), 0))

        if not str(level) in list(config["rewards"].keys()):
            await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "no_reward", _emote="NO"), 0))
        else:
            del config["rewards"][str(level)]
            self.db.configs.update(ctx.guild.id, "lvl_sys", config)
            await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "removed_reward", _emote="YES", lvl=level), 1))


    @role_reward.command(
        name="mode",
        description="🎉 Configure whether to stack role rewards, or only always have the highest role reward"
    )
    @discord.app_commands.default_permissions(manage_guild=True)
    async def role_reward_mode(
        self,
        ctx: discord.Interaction,
        mode: Literal[
            "Stack",
            "Single"
        ] = None
    ) -> None:
        """
        role_reward_mode_help
        examples:
        -reward mode Stack
        """
        # if not self.has_premium(ctx.guild): return await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "need_premium", _emote="NO"), 0))

        config = self.db.configs.get(ctx.guild.id, "lvl_sys")
        if config["enabled"] == False: return await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "lvl_sys_disabled", _emote="NO", prefix="/"), 0))
        
        if mode == None:
            await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "current_mode", mode=config["reward_mode"]), 2))
        else:
            config["reward_mode"] = mode.lower()
            self.db.configs.update(ctx.guild.id, "lvl_sys", config)
            await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "set_mode", _emote="YES", mode=config["reward_mode"]), 1))


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
        # if not self.has_premium(ctx.guild): return await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "need_premium", _emote="NO"), 0))
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

        for_nxt_lvl = self.get_xp_for_next_lvl(data.lvl)
        for_last_lvl = self.get_xp_for_next_lvl(data.lvl - 1) if data.lvl > 2 else 0

        e = Embed(
            ctx,
            title=f"{user.name}#{user.discriminator}",
            description="**Level:** {} \n**Progress:** {} / {} \n**Total XP:** {}"\
                .format(
                    data.lvl,
                    ((for_nxt_lvl - for_last_lvl) - (for_nxt_lvl - data.xp)) if data.lvl > 1 else data.xp,
                    (for_nxt_lvl - for_last_lvl) if data.lvl > 1 else 50,
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
        # if not self.has_premium(ctx.guild): return await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "need_premium", _emote="NO"), 0))
        config = Object(self.db.configs.get(ctx.guild.id, "lvl_sys"))

        if config.enabled == False: return await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "lvl_sys_disabled", _emote="NO", prefix="/"), 0))
        if len(config.users) < 1: return await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "no_one_ranked", _emote="NO"), 0))

        users = [Object(x) for x in self.db.level.find({"guild": f"{ctx.guild.id}"})][:25]
        data = sorted(users, key=lambda e: e.xp, reverse=True)

        e = Embed(
            ctx,
            title=f"Leaderboard for {ctx.guild.name}"
        )
        e.set_thumbnail(
            url=ctx.guild.icon.url
        )
        for i, entry in enumerate(data[:11]):
            user = ctx.guild.get_member(int(entry.id.split("-")[-1]))
            if user == None: 
                user = "Unknown#0000"
            else:
                user = f"{user.name}#{user.discriminator}"

            if (i+1) % 2 == 0: e.add_fields([e.blank_field(True, 5)])
            e.add_field(
                name=f"{self.lb_pos(i)}",
                value="> **User:** {} \n> **Level:** {} \n> **Total XP:** {}"\
                    .format(
                        user,
                        entry.lvl,
                        entry.xp
                    ),
                inline=True
            )
        
        e.set_footer(
            text="Your rank: #{}".format(
                data.index([x for x in data if int(x.id.split("-")[-1]) == ctx.user.id][0]) + 1
            )
        )
        await ctx.response.send_message(embed=e)


    # @discord.app_commands.command(
    #     name="bonus",
    #     description=""
    # )
    # @discord.app_commands.describe(
    #     xp="The amount of XP you want  to grant (use a negative number to subract XP)"
    # )
    # @discord.app_commands.default_permissions(manage_guild=True)
    # async def bonus(
    #     self,
    #     ctx: discord.Interaction,
    #     user: discord.Member,
    #     xp: int
    # ) -> None:
    #     """
    #     bonus_help
    #     examples:
    #     -bonus @paul#0009 1000
    #     -bonus @paul#0009 -500
    #     """
    #     if not self.has_premium(ctx.guild): return await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "need_premium", _emote="NO"), 0))

    #     config = Object(self.db.configs.get(ctx.guild.id, "lvl_sys"))
    #     if config.enabled == False: return await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "lvl_sys_disabled", _emote="NO", prefix="/"), 0))

    #     if xp > MAX_BONUS_XP: return await ctx.response.send_message(embed=E(elf.locale.t(ctx.guild, "max_bonus_xp", _emote="NO", amount=MAX_BONUS_XP), 0))

    #     xp = max(0, xp)



async def setup(
    bot: ShardedBotInstance
) -> None: await bot.register_plugin(LevelPlugin(bot))