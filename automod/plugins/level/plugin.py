# type: ignore

import discord
from discord.ext import commands

from ...__obj__ import TypeHintedToolboxObject as Object
from random import randint
from typing import OrderedDict, List, Union, Literal

from .. import AutoModPluginBlueprint, ShardedBotInstance
from ...schemas import UserLevel
from ...types import Embed, E



MAX_BONUS_XP = 500000


class LevelPlugin(AutoModPluginBlueprint):
    """Plugin for all level system commands"""
    def __init__(self, bot: ShardedBotInstance) -> None:
        super().__init__(bot, requires_premium=False) # set this to true for now (testing etc)
        self._processing = []
        self._cooldowns = []


    def exists(self, config: Object, guild: discord.Guild, user: Union[discord.Member, discord.User], insert: bool = True) -> bool:
        if not str(user.id) in config.users:
            if insert == True:
                config.users.append(str(user.id))
                self.db.configs.update(
                    guild.id, 
                    "lvl_sys", 
                    {
                        "enabled": config.enabled,
                        "notif_mode": config.notif_mode,
                        "users": config.users,
                        "rewards": config.rewards,
                        "reward_mode": config.reward_mode
                    }
                )
                self.db.level.insert(UserLevel(guild, user))
            return False
        else:
            return True


    def get_user_data(self, guild: discord.Guild, user: Union[discord.Member, discord.User]) -> Object:
        return Object(self.db.level.get_doc(f"{guild.id}-{user.id}"))


    def update_user_data(self, guild: discord.Guild, user: Union[discord.Member,discord.User], xp: int, lvl: int) -> None:
        self.db.level.multi_update(f"{guild.id}-{user.id}", {
            "xp": xp,
            "lvl": lvl
        })


    def delete_entry(self, entry: Object) -> None:
        self.db.level.delete(entry.id)
        cfg = self.db.configs.get(entry.id.split("-")[0], "lvl_sys")
        if cfg != None:
            cfg["users"] = [x for x in cfg["users"] if str(x) != str(entry.id.split("-")[1])]
            self.db.configs.update(entry.id.split("-")[0], "lvl_sys", cfg)


    def construct_leaderboard_data(self, ctx: discord.Interaction, init_data: List[Object]) -> List[Object]:
        final = []
        for entry in init_data[:10]:
            user = ctx.guild.get_member(int(entry.id.split("-")[-1]))
            if user == None: 
                self.delete_entry(entry)
            else: 
                final.append(entry)
        return final
    

    def user_set(self, inp: List[Object]) -> List[Object]:
        final = []
        for entry in inp:
            if hasattr(entry, "id"):
                if not entry.id in [_.id for _ in final if hasattr(_, "id")]:
                    final.append(entry)
        return final


    def lb_pos(self, i: int,user: Union[str,discord.Member]) -> str:
        i = (i+1)
        if i == 1:
            return f"🏆 {user}"
        elif i == 2:
            return f"🥈 {user}"
        elif i == 3:
            return f"🥉 {user}"
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
            return f"__{i}{end}__ {user}"


    def has_premium(self, guild: discord.Guild) -> None:
        return self.db.configs.get(guild.id, "premium")
    

    def add_missing_attrs(self, guild: discord.Guild, doc: dict) -> None:
        if "rewards" not in:
            doc["rewards"] = {}
        else:
            if doc["rewards"] = None:
                doc["rewards"] = {}
        if "reward_mode" not in doc:
            doc["reward_mode"] = "stack"
        self.db.configs.update(guild.id, "lvl_sys", doc)


    def get_xp_for_next_lvl(self, lvl: int) -> int:
        if lvl > 1:
            return int((50 * ((lvl - 1) ** 2)) + (50 * (lvl - 1)))
        else:
            return 50
        

    async def is_eligible_message(self, msg: discord.Message) -> bool:
        ctx = await self.bot.get_context(msg)
        return (
            len(msg.content) > 3 \
            and (not ctx.valid and ctx.command == None) \
            and msg.guild != None \
            and msg.author != None \
            and msg.author.bot == False \
            and not msg.content.startswith(tuple([
                "!", "?","/", "-", "+", ".", ";" # common bot prefixes
            ])) \
            and not any([x.bot for x in msg.mentions if hasattr(x, "bot")])
        )


    async def add_reward(self, guild: discord.Guild, user: discord.Member, level: int, config: Object) -> None:
        if not hasattr(config, "rewards"):
            cur = self.db.configs.get(guild.id, "lvl_sys")
            for k, v in {"rewards": {}, "reward_mode": "stack"}.items():
                cur.update({k: v})
            self.db.configs.update(guild.id, "lvl_sys", cur)
            return
            
        if len(config.rewards) < 1: return

        lvl_keys = list({int(k): v for k, v in config.rewards.items()}.keys())
        mins = [i for i in lvl_keys if level <= i]
        maxs = [i for i in lvl_keys if level >= i]
        new_role = guild.get_role(
            int(config.rewards[str(max([min(mins) if len(mins) > 0 else 0, max(maxs) if len(maxs) > 0 else 0]))])
        )

        if new_role != None and new_role not in user.roles:
            try:
                await user.add_roles(new_role)
            except Exception:
                pass
            else:
                try:
                    await user.send(embed=E(self.locale.t(guild, "new_reward", _emote="PARTY", role=new_role.name, lvl=level, server=guild.name), 3))
                except Exception:
                    pass
            finally:
                if config.reward_mode == "single":
                    to_rm = []
                    for r in [x for x in user.roles if x != guild.default_role]:
                        if r.id != new_role.id:
                            if r.id in [int(_) for _ in list({k: v for k, v in config.rewards.items() if int(k) > int(level)}.values())]:
                                to_rm.append(r)
                    
                    if len(to_rm) > 0:
                        try:
                            await user.remove_roles(*to_rm)
                        except Exception:
                            pass


    @AutoModPluginBlueprint.listener()
    async def on_message(self, msg: discord.Message) -> None:
        # if not self.has_premium(msg.guild): return
        if msg.guild == None: return
        if not msg.guild.chunked:
            await self.bot.chunk_guild(msg.guild)
        
        if not await self.is_eligible_message(msg): return
        if msg.author.bot == True: return # safety
        
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

        if len(msg.content.split(" ")) < 5:
            xp = randint(1, 5)
        else:
            xp = randint(5, 10)

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
                ), 3))
            elif config.notif_mode == "dm":
                try:
                    await msg.author.send(embed=E(self.locale.t(
                        msg.guild, 
                        "lvl_up_dm", 
                        _emote="PARTY", 
                        mention=msg.author.mention,
                        lvl=(data.lvl + 1),
                        server=msg.guild.name
                    ), 3))
                except discord.Forbidden:
                    pass
            else:
                pass # None
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
    async def lvlsys(self, ctx: discord.Interaction, enabled: Literal["True", "False"] = None, notifications: Literal["Channel", "DM", "None"] = None) -> None:
        # if not self.has_premium(ctx.guild): return await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "need_premium", _emote="NO"), 0), ephemeral=True)

        config = self.db.configs.get(ctx.guild.id, "lvl_sys")
        if enabled == None and notifications == None:
            e = Embed(
                ctx,
                title="Level System",
                description="**• Enabled:** {} \n**• Notifications:** {} \n**• Rewards:** {}".format(
                    self.bot.emotes.get("YES") if config["enabled"] == True else self.bot.emotes.get("NO"),
                    config["notif_mode"].title(),
                    config["reward_mode"].title()
                )
            )
            await ctx.response.send_message(embed=e)
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
    @discord.app_commands.describe(
        user="The user you want to reset"
    )
    @discord.app_commands.default_permissions(manage_guild=True)
    async def reset(self, ctx: discord.Interaction, user: discord.Member) -> None:
        """
        reset_help
        examples:
        -reset @paul#0009
        """
        # if not self.has_premium(ctx.guild): return await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "need_premium", _emote="NO"), 0), ephemeral=True)

        config = Object(self.db.configs.get(ctx.guild.id, "lvl_sys"))
        cmd = f"</lvlsys:{self.bot.internal_cmd_store.get('lvlsys')}>"
        if config.enabled == False: return await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "lvl_sys_disabled", _emote="NO", cmd=cmd), 0), ephemeral=True)

        if self.exists(config, ctx.guild, user):
            self.update_user_data(ctx.guild, user, 1, 0)
        await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "reset_user", _emote="YES"), 1))


    @discord.app_commands.command(
        name="rewards",
        description="🌱 Shows the current role rewards"
    )
    async def role_reward_show(self, ctx: discord.Interaction) -> None:
        """
        role_reward_show_help
        examples:
        -rewards
        """
        # if not self.has_premium(ctx.guild): return await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "need_premium", _emote="NO"), 0), ephemeral=True)

        raw = self.db.configs.get(ctx.guild.id, "lvl_sys")
        self.add_missing_attrs(ctx.guild, raw)

        config = Object(raw)
        cmd = f"</lvlsys:{self.bot.internal_cmd_store.get('lvlsys')}>"
        if config.enabled == False: return await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "lvl_sys_disabled", _emote="NO", cmd=cmd), 0), ephemeral=True)

        if len(config.rewards) < 1:
            cmd = f"</reward add:{self.bot.internal_cmd_store.get('reward')}>"
            await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "no_rewards", _emote="WARN", cmd=cmd), 2), ephemeral=True)
        else:
            e = Embed(
                ctx,
                title="Role Rewards",
                description="\n".join([
                    f"**• Level {lvl}:** <@&{role}>" for lvl, role in dict(sorted(config.rewards.items(), key=lambda e: int(e[0]))).items()
                ])
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
    @discord.app_commands.describe(
        level="At what level to assign the role",
        role="The role to assign the user"
    )
    @discord.app_commands.default_permissions(manage_guild=True)
    async def role_reward_add(self, ctx: discord.Interaction, level: discord.app_commands.Range[int, 1, 100], role: discord.Role) -> None:
        """
        rol_reward_add_help
        examples:
        -reward add 5 @Level5
        -reward add 10 @Advanced
        """
        # if not self.has_premium(ctx.guild): return await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "need_premium", _emote="NO"), 0), ephemeral=True)
        config = self.db.configs.get(ctx.guild.id, "lvl_sys")
        self.add_missing_attrs(ctx.guild, config)

        cmd = f"</lvlsys:{self.bot.internal_cmd_store.get('lvlsys')}>"
        if config["enabled"] == False: return await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "lvl_sys_disabled", _emote="NO", cmd=cmd), 0), ephemeral=True)

        if len(config["rewards"]) >= 15: return await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "max_rewards", _emote="NO"), 0), ephemeral=True)

        if str(role.id) in list(config["rewards"].values()):
            await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "alr_reward", _emote="NO"), 0), ephemeral=True)
        else:
            if role.position >= ctx.guild.me.top_role.position: 
                return await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "role_too_high", _emote="NO"), 0))
            elif role.is_default() == True:
                return await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "no_default_role", _emote="NO"), 0))
            elif role.is_assignable() == False:
                return await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "cant_assign_role", _emote="NO"), 0))

            config["rewards"].update({
                str(level): str(role.id)
            })
            self.db.configs.update(ctx.guild.id, "lvl_sys", config)
            await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "added_reward", _emote="YES", role=role.mention, lvl=level), 1))


    @role_reward.command(
        name="remove",
        description="❌ Removes the reward for the specified level"
    )
    @discord.app_commands.describe(
        level="The level for which you want to remove to reward",
    )
    @discord.app_commands.default_permissions(manage_guild=True)
    async def role_reward_remove(self, ctx: discord.Interaction, level: discord.app_commands.Range[int, 1, 100]) -> None:
        """
        role_reward_remove_help
        examples:
        -reward remove 5
        """
        # if not self.has_premium(ctx.guild): return await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "need_premium", _emote="NO"), 0), ephemeral=True)
        config = self.db.configs.get(ctx.guild.id, "lvl_sys")
        self.add_missing_attrs(ctx.guild, config)

        cmd = f"</lvlsys:{self.bot.internal_cmd_store.get('lvlsys')}>"
        if config["enabled"] == False: return await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "lvl_sys_disabled", _emote="NO", cmd=cmd), 0), ephemeral=True)

        if not str(level) in list(config["rewards"].keys()):
            await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "no_reward", _emote="NO"), 0), ephemeral=True)
        else:
            del config["rewards"][str(level)]
            self.db.configs.update(ctx.guild.id, "lvl_sys", config)
            await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "removed_reward", _emote="YES", lvl=level), 1))


    @role_reward.command(
        name="mode",
        description="🎉 Configure whether to stack role rewards, or only always have the highest role reward"
    )
    @discord.app_commands.describe(
        mode="The mode for assigning rewards (stack roles or always only allow the highest one) "
    )
    @discord.app_commands.default_permissions(manage_guild=True)
    async def role_reward_mode(self, ctx: discord.Interaction, mode: Literal["Stack", "Single"]) -> None:
        """
        role_reward_mode_help
        examples:
        -reward mode Stack
        """
        # if not self.has_premium(ctx.guild): return await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "need_premium", _emote="NO"), 0), ephemeral=True)
        config = self.db.configs.get(ctx.guild.id, "lvl_sys")
        self.add_missing_attrs(ctx.guild, config)

        cmd = f"</lvlsys:{self.bot.internal_cmd_store.get('lvlsys')}>"
        if config["enabled"] == False: return await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "lvl_sys_disabled", _emote="NO", cmd=cmd), 0), ephemeral=True)
        
        config["reward_mode"] = mode.lower()
        self.db.configs.update(ctx.guild.id, "lvl_sys", config)
        await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "set_mode", _emote="YES", mode=config["reward_mode"]), 1))


    @discord.app_commands.command(
        name="rank",
        description="⭐ View your server rank"
    )
    async def rank(self, ctx: discord.Interaction, user: discord.Member = None) -> None:
        """
        rank_help
        examples:
        -rank
        -rank paul#0009
        """
        if not ctx.guild.chunked: await ctx.guild.chunk(cache=True)
        if user == None: user = ctx.user

        config = Object(self.db.configs.get(ctx.guild.id, "lvl_sys"))
        cmd = f"</lvlsys:{self.bot.internal_cmd_store.get('lvlsys')}>"
        if config.enabled == False: return await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "lvl_sys_disabled", _emote="NO", cmd=cmd), 0), ephemeral=True)

        if not self.exists(
            config, 
            ctx.guild, 
            user,
            insert=False
        ): return await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "not_ranked", _emote="NO"), 0), ephemeral=True)

        data = self.get_user_data(
            ctx.guild, 
            user
        )

        for_nxt_lvl = self.get_xp_for_next_lvl(data.lvl)
        for_last_lvl = self.get_xp_for_next_lvl(data.lvl - 1) if data.lvl > 2 else 0

        e = Embed(
            ctx,
            title=f"{user.name}#{user.discriminator}",
            description="**• Level:** {} \n**• Progress:** {} / {} \n**• Total XP:** {}"\
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
        
        data = sorted(list(self.db.level.find({"guild": f"{ctx.guild.id}"})), key=lambda e: e["xp"], reverse=True)
        e.set_footer(
            text="Your rank: #{}".format(
                data.index([x for x in data if int(x["id"].split("-")[-1]) == ctx.user.id][0]) + 1
            )
        )
        await ctx.response.send_message(embed=e)


    @discord.app_commands.command(
        name="leaderboard",
        description="📜 View the server's leaderboard"
    )
    async def leaderboard(self, ctx: discord.Interaction) -> None:
        """
        leaderboard_help
        examples:
        -leaderboard
        """
        if not ctx.guild.chunked: await ctx.guild.chunk(cache=True)
        config = Object(self.db.configs.get(ctx.guild.id, "lvl_sys"))

        cmd = f"</lvlsys:{self.bot.internal_cmd_store.get('lvlsys')}>"
        if config.enabled == False: return await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "lvl_sys_disabled", _emote="NO", cmd=cmd), 0), ephemeral=True)
        if len(config.users) < 1: return await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "no_one_ranked", _emote="NO"), 0), ephemeral=True)

        await ctx.response.defer(thinking=True)

        users = self.user_set([Object(x) for x in self.db.level.find({"guild": f"{ctx.guild.id}"})][:25])
        data = sorted(set(users), key=lambda e: e.xp, reverse=True)

        e = Embed(
            ctx,
            title=f"Leaderboard for {ctx.guild.name}"
        )
        e.set_thumbnail(
            url=ctx.guild.icon.url
        )

        final_data = self.construct_leaderboard_data(ctx, data)
        for i, entry in enumerate(final_data):
            user = ctx.guild.get_member(int(entry.id.split("-")[-1]))
            if user == None: 
                self.delete_entry(entry)
            else:
                if (i+1) % 2 == 0: e.add_fields([e.blank_field(True, 10)])
                e.add_field(
                    name=f"{self.lb_pos(i, user)}",
                    value="**• Level:** {} \n**• Total XP:** {} \n⠀"\
                        .format(
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
        await ctx.followup.send(embed=e)


async def setup(bot: ShardedBotInstance) -> None: 
    await bot.register_plugin(LevelPlugin(bot))