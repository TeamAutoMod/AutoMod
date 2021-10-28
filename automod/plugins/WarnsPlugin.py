import discord
from discord.ext import commands

from .PluginBlueprint import PluginBlueprint
from .Types import Duration, Reason, DiscordUser, Embed
from utils import Permissions



valid_actions = [
    "ban",
    "kick",
    "mute",
    "none"
]


async def getNewPunishments(plugin, ctx):
    cfg = plugin.db.configs.get(ctx.guild.id, "punishments")
    f = plugin.emotes.get('WARN')
    punishments = [f"``{x} {f}``: {y.capitalize() if len(y.split(' ')) == 1 else y.split(' ')[0].capitalize() + ' ' + y.split(' ')[-2] + y.split(' ')[-1]}" for x, y in cfg.items()]
    punishments = sorted(punishments, key=lambda i: i.split(" ")[0])
    return punishments


class WarnsPlugin(PluginBlueprint):
    def __init__(self, bot):
        super().__init__(bot)


    @commands.command()
    @commands.has_guild_permissions(administrator=True)
    async def punishment(
        self, 
        ctx,
        warn: int,
        action: str,
        time: Duration = None
    ):
        """punishment_help"""
        warns = warn
        action = action.lower()
        prefix = self.bot.get_guild_prefix(ctx.guild)
        e = Embed()
        if not action in valid_actions:
            return await ctx.send(self.i18next.t(ctx.guild, "invalid_action", _emote="WARN", prefix=prefix))

        if warns < 1:
            return await ctx.send(self.i18next.t(ctx.guild, "min_warns", _emote="NO"))

        if warns > 100:
            return await ctx.send(self.i18next.t(ctx.guild, "max_warns", _emote="NO"))

        current = self.db.configs.get(ctx.guild.id, "punishments")
        if action == "none":
            new = {x: y for x, y in current.items() if str(x) != str(warns)}
            self.db.configs.update(ctx.guild.id, "punishments", new)

            desc = await getNewPunishments(self, ctx)
            e.add_field(
                name="❯ Punishments",
                value="{}".format("\n".join(desc) if len(desc) > 0 else "None")
            )

            return await ctx.send(content=self.i18next.t(ctx.guild, "set_none", _emote="YES", warns=warns), embed=e)
        
        elif action != "mute":
            current.update({
                str(warns): action
            })
            self.db.configs.update(ctx.guild.id, "punishments", current)

            desc = await getNewPunishments(self, ctx)
            e.add_field(
                name="❯ Punishments",
                value="{}".format("\n".join(desc) if len(desc) > 0 else "None")
            )

            return await ctx.send(content=self.i18next.t(ctx.guild, f"set_{action}", _emote="YES", warns=warns), embed=e)

        else:
            if time is None:
                return await ctx.send(self.i18next.t(ctx.guild, "time_needed", _emote="NO", prefix=prefix))
            
            as_seconds = time.to_seconds(ctx)
            if as_seconds > 0:
                length = time.length
                unit = time.unit
                
                current.update({
                    str(warns): f"{action} {as_seconds} {length} {unit}"
                })
                self.db.configs.update(ctx.guild.id, "punishments", current)

                desc = await getNewPunishments(self, ctx)
                e.add_field(
                    name="❯ Punishments",
                    value="{}".format("\n".join(desc) if len(desc) > 0 else "None")
                )

                return await ctx.send(content=self.i18next.t(ctx.guild, f"set_{action}", _emote="YES", warns=warns, length=length, unit=unit), embed=e)
            
            else:
                raise commands.BadArgument("number_too_small")


    @commands.command()
    @commands.has_guild_permissions(kick_members=True)
    async def warn(
        self,
        ctx,
        users: commands.Greedy[discord.Member],
        warns = None,
        *,
        reason: Reason = None
    ):
        """warn_help"""
        if reason is None:
            reason = self.i18next.t(ctx.guild, "no_reason")

        if warns is None:
            warns = 1
        else:
            try:
                warns = int(warns)
            except ValueError:
                reason = " ".join(ctx.message.content.split(" ")[(len(list(set(users))) + 1):])
                warns = 1

        if warns < 1:
            return await ctx.send(self.i18next.t(ctx.guild, "min_warns", _emote="NO"))

        if warns > 100:
            return await ctx.send(self.i18next.t(ctx.guild, "max_warns", _emote="NO"))
        
        users = list(set(users))
        if ctx.message.reference != None: 
            users.append(ctx.message.reference.resolved.author)
        if len(users) < 1:
            return await ctx.send(self.i18next.t(ctx.guild, "no_member", _emote="NO"))

        msgs = []
        for user in users:
            if not Permissions.is_allowed(ctx, ctx.author, user):
                msgs.append(self.i18next.t(ctx.guild, "warn_not_allowed", _emote="NO", user=user.name))

            else:
                _, case = await self.action_validator.add_warns(
                    ctx.message, 
                    user, 
                    warns, 
                    moderator=ctx.author, 
                    moderator_id=ctx.author.id,
                    user=user, 
                    user_id=user.id,
                    reason=reason
                )

                if case == 0:
                    msgs.append(self.i18next.t(ctx.guild, "warn_not_allowed", _emote="NO", user=user.name))
                else:
                    msgs.append(self.i18next.t(ctx.guild, "user_warned", _emote="YES", user=user, reason=reason, case=case, warns=warns))
        
        await ctx.send("\n".join(msgs))


    @commands.command()
    @commands.has_guild_permissions(kick_members=True)
    async def unwarn(
        self,
        ctx,
        users: commands.Greedy[discord.Member],
        warns = None,
        *,
        reason: Reason = None
    ):
        """unwarn_help"""
        if reason is None:
            reason = self.i18next.t(ctx.guild, "no_reason")

        if warns is None:
            warns = 1
        else:
            try:
                warns = int(warns)
            except ValueError:
                reason = " ".join(ctx.message.content.split(" ")[(len(list(set(users))) + 1):])
                warns = 1

        if warns < 1:
            return await ctx.send(self.i18next.t(ctx.guild, "min_warns", _emote="NO"))

        if warns > 100:
            return await ctx.send(self.i18next.t(ctx.guild, "max_warns", _emote="NO"))
        
        users = list(set(users))
        if ctx.message.reference != None: 
            users.append(ctx.message.reference.resolved.author)
        if len(users) < 1:
            return await ctx.send(self.i18next.t(ctx.guild, "no_member", _emote="NO"))

        msgs = []
        for user in users:
            if not Permissions.is_allowed(ctx, ctx.author, user):
                msgs.append(self.i18next.t(ctx.guild, "unwarn_not_allowed", _emote="NO", user=user.name))

            else:
                _id = f"{ctx.guild.id}-{user.id}"
                if not self.db.warns.exists(_id):
                    self.db.warns.insert(self.schemas.Warn(_id, 0))
                    msgs.append(self.i18next.t(ctx.guild, "no_warns", _emote="NO"))
                else:
                    current = self.db.warns.get(_id, "warns")
                    if current < 1:
                        msgs.append(self.i18next.t(ctx.guild, "no_warns", _emote="NO"))
                    else:
                        new = (current - warns) if (current - warns) >= 0 else 0
                        self.db.warns.update(_id, "warns", new)
                
                        case = self.bot.utils.newCase(ctx.guild, "Unwarn", user, ctx.author, reason)
                        dm_result = await self.bot.utils.dmUser(
                            ctx.message, 
                            "unwarn", 
                            user, 
                            _emote="ANGEL", 
                            color=0x5cff9d,
                            moderator=ctx.message.author, 
                            warns=warns, 
                            guild_name=ctx.guild.name, 
                            reason=reason
                        )
                        
                        msgs.append(self.i18next.t(ctx.guild, "user_unwarned", _emote="YES", user=user, reason=reason, case=case, warns=warns))

                        await self.action_logger.log(
                            ctx.guild, 
                            "unwarn",
                            user=user,
                            user_id=user.id,
                            old_warns=current,
                            new_warns=new,
                            moderator=ctx.author,
                            moderator_id=ctx.author.id,
                            reason=reason,
                            case=case,
                            dm=dm_result
                        )
        
        await ctx.send("\n".join(msgs))



    @commands.command(aliases=["warns", "fetch"])
    @commands.has_guild_permissions(kick_members=True)
    async def check(
        self,
        ctx,
        user: DiscordUser
    ):
        """check_help"""
        _id = f"{ctx.guild.id}-{user.id}"
        warns = self.db.warns.get(_id, "warns") if self.db.warns.exists(_id) else 0

        muted = "✅" if self.db.mutes.exists(_id) else "❌"
        muted_until = f"<t:{round(self.db.mutes.get(_id, 'ending').timestamp())}>" if self.db.mutes.exists(_id) else "``N/A``"

        banned = "❌" if not await Permissions.is_banned(ctx, user) else "✅"

        e = Embed()
        e.set_author(
            name=f"{user} ({user.id})",
            icon_url=user.display_avatar
        )
        e.add_field(
            name="❯ Warns",
            value=f"``{warns}``"
        )
        e.add_field(
            name="❯ Muted",
            value=f"``{muted}``"
        )
        e.add_field(
            name="❯ Muted until",
            value=f"{muted_until}"
        )
        e.add_field(
            name="❯ Banned",
            value=f"``{banned}``"
        )

        await ctx.send(embed=e)



def setup(bot):
    bot.add_cog(WarnsPlugin(bot))