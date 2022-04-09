import discord
from discord.ext import commands

import logging; log = logging.getLogger()

from . import AutoModPlugin
from ..types import Embed, Emote



class ReactionRolesPlugin(AutoModPlugin):
    """Plugin for reaction roles"""
    def __init__(self, bot):
        super().__init__(bot)


    @AutoModPlugin.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        rrs = self.db.configs.get(payload.guild_id, "reaction_roles")
        if not f"{payload.message_id}" in rrs: return

        data = rrs[f"{payload.message_id}"]
        if len(data["pairs"]) < 1: return

        if payload.emoji.id == None:
            possible_name = payload.emoji.name
        else:
            possible_name = f"<:{payload.emoji.name}:{payload.emoji.id}>"

        role_id = [list(x.values())[1] for x in data["pairs"] if list(x.values())[0] == possible_name]
        if len(role_id) < 1: 
            return
        else:
            guild = self.bot.get_guild(payload.guild_id)
            role = guild.get_role(int(role_id[0]))

            if role != None:
                if role in payload.member.roles:
                    try:
                        await payload.member.remove_roles(
                            role
                        )
                    except Exception:
                        pass
                else:
                    try:
                        await payload.member.add_roles(
                            role
                        )
                    except Exception:
                        pass


    @AutoModPlugin.listener()
    async def on_raw_message_delete(self, payload: discord.RawMessageDeleteEvent):
        if payload.guild_id == None: return
        rrs = self.db.configs.get(payload.guild_id, "reaction_roles")
        if not f"{payload.message_id}" in rrs: return

        del rrs[f"{payload.message_id}"]
        self.db.configs.update(payload.guild_id, "reaction_roles", rrs)


    @commands.group(aliases=["rr"])
    @AutoModPlugin.can("manage_roles")
    async def reaction_roles(self, ctx):
        """
        reaction_roles_help
        examples:
        -reaction_roles add 543056846601191508 🟢 @GreenRole
        -reaction_roles remove 543056846601191508 @Greenrole
        -reaction_roles
        """
        if ctx.invoked_subcommand is None:
            rrs = self.db.configs.get(ctx.guild.id, "reaction_roles")
            if len(rrs) < 1:
                return await ctx.send(self.locale.t(ctx.guild, "no_rr", _emote="NO"))
            else:
                e = Embed(
                    title="Reaction roles"
                )
                for msg, data in rrs.items():
                    channel = ctx.guild.get_channel(int(data["channel"]))
                    e.add_field(
                        name=f"❯ {msg}{f' (#{channel.name})' if channel != None else ''}",
                        value=f"{f'[Jump to message](https://discord.com/channels/{ctx.guild.id}/{channel.id}/{msg})' if channel != None else ''}" + 
                        "{}".format(
                            "\n" if channel != None else ""
                        ) +
                        "\n".join(
                            [f"**•** {await ctx.guild.fetch_emoji(int(pair['emote'])) if pair['emote'][0].isdigit() else pair['emote']} → <@&{pair['role']}>" for pair in data["pairs"]]
                        )
                    )

                await ctx.send(embed=e)


    @reaction_roles.command()
    @AutoModPlugin.can("manage_roles")
    async def add(self, ctx, message_id: discord.Message, emote: Emote, role: discord.Role):
        """
        reaction_roles_add_help
        examples:
        -reaction_roles add 543056846601191508 🟢 @GreenRole
        """
        message = message_id
        rrs = self.db.configs.get(ctx.guild.id, "reaction_roles")
        if f"{message.id}" in rrs:
            data = rrs[f"{message.id}"]
        else:
            data = {
                "channel": f"{message.channel.id}",
                "pairs": []
            }
        if len(data["pairs"]) > 10:
            return await ctx.send(self.locale.t(ctx.guild, "max_rr", _emote="NO"))
        else:
            if len(message.reactions) > 10:
                return await ctx.send(self.locale.t(ctx.guild, "max_rr_reactions", _emote="NO"))
            else:
                if role.position >= ctx.guild.me.top_role.position:
                    return await ctx.send(self.locale.t(ctx.guild, "rr_role_too_high", _emote="NO"))
                elif f"{emote}" in [list(x.values())[0] for x in data["pairs"]]:
                    return await ctx.send(self.locale.t(ctx.guild, "rr_emoji_alr_bound", _emote="NO"))
                elif f"{role.id}" in [list(x.values())[1] for x in data["pairs"]]:
                    return await ctx.send(self.locale.t(ctx.guild, "rr_role_alr_bound", _emote="NO"))
                else:
                    try:
                        await message.add_reaction(
                            emote
                        )
                    except Exception as ex:
                        return await ctx.send(self.locale.t(ctx.guild, "fail", _emote="NO", exc=ex))
                    else:
                        data["pairs"].append({
                            "emote": f"{emote}",
                            "role": f"{role.id}"
                        })
                        rrs.update({
                            f"{message.id}": data
                        })
                        self.db.configs.update(ctx.guild.id, "reaction_roles", rrs)

                        await ctx.send(self.locale.t(ctx.guild, "set_rr", _emote="YES"))

    @reaction_roles.command()
    @AutoModPlugin.can("manage_roles")
    async def remove(self, ctx, message_id: discord.Message, role: discord.Role):
        """
        reaction_roles_remove_help
        examples:
        -reaction_roles remove 543056846601191508 @Greenrole
        """
        message = message_id
        rrs = self.db.configs.get(ctx.guild.id, "reaction_roles")
        if len(rrs) < 1:
            return await ctx.send(self.locale.t(ctx.guild, "no_rr", _emote="NO"))
        else:
            if not f"{message.id}" in rrs:
                return await ctx.send(self.locale.t(ctx.guild, "not_rr_msg", _emote="NO"))
            else:
                data = rrs[f"{message.id}"]
                if len([x for x in data["pairs"] if list(x.values())[1] == f"{role.id}"]) < 1:
                    return await ctx.send(self.locale.t(ctx.guild, "no_rr_role", _emote="NO"))
                else:
                    data["pairs"] = [x for x in data["pairs"] if list(x.values())[1] != f"{role.id}"]
                    if len(data["pairs"]) > 0:
                        rrs[f"{message.id}"] = data
                    else:
                        del rrs[f"{message.id}"]
                    self.db.configs.update(ctx.guild.id, "reaction_roles", rrs)

                    await ctx.send(self.locale.t(ctx.guild, "removed_rr", _emote="YES"))


async def setup(bot): await bot.register_plugin(ReactionRolesPlugin(bot))