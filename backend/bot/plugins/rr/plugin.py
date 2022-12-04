# type: ignore

import discord
from discord.ext import commands

from typing import Union
import logging; log = logging.getLogger()

from .. import AutoModPluginBlueprint, ShardedBotInstance
from ...types import Embed, Emote, Message, E



class ReactionRolesPlugin(AutoModPluginBlueprint):
    """Plugin for reaction roles"""
    def __init__(
        self, 
        bot: ShardedBotInstance
    ) -> None:
        super().__init__(bot)
        self.msg_cache = {}


    async def get_message(
        self,
        channel_id: int,
        msg_id: int
    ) -> Union[
        discord.Message,
        None
    ]:
        if msg_id in self.msg_cache:
            return self.msg_cache[msg_id]
        else:
            try:
                channel = self.bot.get_channel(channel_id)
                msg = await channel.fetch_message(msg_id)
            except Exception:
                msg = None
            else:
                self.msg_cache[msg_id] = msg
            finally:
                return msg


    @AutoModPluginBlueprint.listener()
    async def on_raw_reaction_add(
        self, 
        payload: discord.RawReactionActionEvent
    ) -> None: 
        if f"{payload.user_id}" == f"{self.bot.user.id}": return
        if payload.member.bot == True: return

        rrs = self.db.configs.get(payload.guild_id, "reaction_roles")
        if not f"{payload.message_id}" in rrs: return

        data = rrs[f"{payload.message_id}"]
        if len(data["pairs"]) < 1: return

        if payload.emoji.id == None:
            possible_name = payload.emoji.name
        else:
            possible_name = f"<{'a' if payload.emoji.animated else ''}:{payload.emoji.name}:{payload.emoji.id}>"

        role_id = [list(x.values())[1] for x in data["pairs"] if list(x.values())[0] == possible_name]
        if len(role_id) < 1: 
            return
        else:
            guild = self.bot.get_guild(payload.guild_id)
            role = guild.get_role(int(role_id[0]))

            if role != None:
                if role not in payload.member.roles:
                    try:
                        await payload.member.add_roles(
                            role
                        )
                    except Exception:
                        pass


    @AutoModPluginBlueprint.listener()
    async def on_raw_reaction_remove(
        self, 
        payload: discord.RawReactionActionEvent
    ) -> None:
        if f"{payload.user_id}" == f"{self.bot.user.id}": return

        rrs = self.db.configs.get(payload.guild_id, "reaction_roles")
        if not f"{payload.message_id}" in rrs: return

        data = rrs[f"{payload.message_id}"]
        if len(data["pairs"]) < 1: return

        if payload.emoji.id == None:
            possible_name = payload.emoji.name
        else:
            possible_name = f"<{'a' if payload.emoji.animated else ''}:{payload.emoji.name}:{payload.emoji.id}>"

        role_id = [list(x.values())[1] for x in data["pairs"] if list(x.values())[0] == possible_name]
        if len(role_id) < 1: 
            return
        else:
            guild = self.bot.get_guild(payload.guild_id)
            if guild.chunked: await self.bot.chunk_guild(guild)

            role = guild.get_role(int(role_id[0]))
            member = guild.get_member(payload.user_id)
            if member.bot == True: return

            if role != None:
                if role in member.roles:
                    try:
                        await member.remove_roles(
                            role
                        )
                    except Exception:
                        pass


    @AutoModPluginBlueprint.listener()
    async def on_raw_message_delete(
        self, 
        payload: discord.RawMessageDeleteEvent
    ) -> None:
        if payload.guild_id == None: return
        rrs = self.db.configs.get(payload.guild_id, "reaction_roles")
        if not f"{payload.message_id}" in rrs: return

        del rrs[f"{payload.message_id}"]
        self.db.configs.update(payload.guild_id, "reaction_roles", rrs)


    rr = discord.app_commands.Group(
        name="reaction-roles",
        description="🎭 Configure reaction roles",
        default_permissions=discord.Permissions(manage_roles=True)
    )
    @rr.command(
        name="list",
        description="🎭 Shows a list of active reaction roles"
    )
    @discord.app_commands.default_permissions(manage_roles=True)
    async def show(
        self, 
        ctx: discord.Interaction
    ) -> None:
        """
        reaction_roles_help
        examples:
        -reaction-roles list
        """
        rrs = {
            k: v for k, v in self.db.configs.get(
                ctx.guild.id, 
                "reaction_roles"
            ).items() if self.bot.get_channel(int(v['channel'])) != None
        }
        if len(rrs) < 1:
            return await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "no_rr", _emote="NO"), 0))
        else:
            e = Embed(
                ctx,
                title="Reaction roles"
            )
            for i, (msg, data) in enumerate(rrs.items()):
                channel = ctx.guild.get_channel(int(data["channel"]))

                if (i+1) % 2 == 0: e.add_fields([e.blank_field(True, 10)])
                e.add_field(
                    name=f"**__{msg}__**",
                    value="{}".format(
                        f"**• Channel:** {f'<#{channel.id}>' if channel != None else '#unkown'}"
                    ) +
                    "\n{}".format(
                        f"{f'**• Message:** [Here](https://discord.com/channels/{ctx.guild.id}/{channel.id}/{msg})' if channel != None else ''}"
                    ) + 
                    "{}".format(
                        "\n" if channel != None else ""
                    ) +
                    "\n".join(
                        [f"**•** {self.bot.get_emoji(int(pair['emote'])) if pair['emote'][0].isdigit() else pair['emote']} → <@&{pair['role']}>" for pair in data["pairs"]]
                    ),
                    inline=True
                )

            await ctx.response.send_message(embed=e)


    @rr.command(
        name="add",
        description="✅ Adds a new reaction role"
    )
    @discord.app_commands.describe(
        message_id="The message the reaction should be added to",
        emote="The emote of the reaction (custom or default emotes)",
        role="The role users should receive when reacting"
    )
    @discord.app_commands.default_permissions(manage_roles=True)
    async def add(
        self, 
        ctx: discord.Interaction, 
        message_id: str, 
        emote: str, 
        role: discord.Role
    ) -> None:
        """
        reaction_roles_add_help
        examples:
        -reaction-roles add 543056846601191508 🟢 @GreenRole
        """
        try:
            emote = await Emote().convert(ctx, emote)
        except Exception as ex:
            return self.error(ctx, ex)
        
        try:
            message = await Message().convert(ctx, message_id)
        except Exception as ex:
            return self.error(ctx, ex)
        else:
            if message == None: return self.error(ctx, commands.BadArgument("Message not found"))
            if not message.id in self.msg_cache: self.msg_cache[message_id] = message

        rrs = self.db.configs.get(ctx.guild.id, "reaction_roles")
        if f"{message.id}" in rrs:
            data = rrs[f"{message.id}"]
        else:
            data = {
                "channel": f"{message.channel.id}",
                "pairs": []
            }
        if len(data["pairs"]) > 10:
            return await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "max_rr", _emote="NO"), 0), ephemeral=True)
        else:
            if len(message.reactions) > 10:
                return await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "max_rr_reactions", _emote="NO"), 0), ephemeral=True)
            else:
                if role.position >= ctx.guild.me.top_role.position:
                    return await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "rr_role_too_high", _emote="NO"), 0), ephemeral=True)
                elif role.is_default() == True:
                    return await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "no_default_role", _emote="NO"), 0), ephemeral=True)
                elif role.is_assignable() == False:
                    return await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "cant_assign_role", _emote="NO"), 0), ephemeral=True)
                elif f"{emote}" in [list(x.values())[0] for x in data["pairs"]]:
                    return await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "rr_emoji_alr_bound", _emote="NO"), 0), ephemeral=True)
                elif f"{role.id}" in [list(x.values())[1] for x in data["pairs"]]:
                    return await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "rr_role_alr_bound", _emote="NO"), 0), ephemeral=True)
                else:
                    try:
                        await message.add_reaction(
                            emote
                        )
                    except Exception as ex:
                        return await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "fail", _emote="NO", exc=ex), 0), ephemeral=True)
                    else:
                        data["pairs"].append({
                            "emote": f"{emote}",
                            "role": f"{role.id}"
                        })
                        rrs.update({
                            f"{message.id}": data
                        })
                        self.db.configs.update(ctx.guild.id, "reaction_roles", rrs)

                        await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "set_rr", _emote="YES"), 1), ephemeral=True)


    @rr.command(
        name="remove",
        description="❌ Removes an exisitng reaction role"
    )
    @discord.app_commands.describe(
        message_id="The message of the reaction role",
        role="The role you want to remove"
    )
    @discord.app_commands.default_permissions(manage_roles=True)
    async def remove(
        self, 
        ctx: discord.Interaction, 
        message_id: str, 
        role: discord.Role
    ) -> None:
        """
        reaction_roles_remove_help
        examples:
        -reaction-roles remove 543056846601191508 @Greenrole
        """
        rrs = self.db.configs.get(ctx.guild.id, "reaction_roles")
        if len(rrs) < 1:
            return await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "no_rr", _emote="NO"), 0), ephemeral=True)
        else:
            if not f"{message_id}" in rrs:
                return await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "not_rr_msg", _emote="NO"), 0), ephemeral=True)
            else:
                data = rrs[f"{message_id}"]
                if len([x for x in data["pairs"] if list(x.values())[1] == f"{role.id}"]) < 1:
                    return await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "no_rr_role", _emote="NO"), 0), ephemeral=True)
                else:
                    msg = await self.get_message(int(data["channel"]), int(message_id))
                    if msg != None:
                        try:
                            await msg.remove_reaction(
                                [x for x in data["pairs"] if list(x.values())[1] == f"{role.id}"][0].get("emote"), 
                                ctx.guild.me
                            )
                        except Exception:
                            pass

                    data["pairs"] = [x for x in data["pairs"] if list(x.values())[1] != f"{role.id}"]
                    if len(data["pairs"]) > 0:
                        rrs[f"{message_id}"] = data
                    else:
                        del rrs[f"{message_id}"]
                    self.db.configs.update(ctx.guild.id, "reaction_roles", rrs)

                    await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "removed_rr", _emote="YES"), 1), ephemeral=True)


async def setup(
    bot: ShardedBotInstance
) -> None: await bot.register_plugin(ReactionRolesPlugin(bot))