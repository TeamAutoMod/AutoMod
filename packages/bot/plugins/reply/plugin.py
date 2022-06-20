import discord
from discord.ext import commands

from typing import Literal
from toolbox import S as Object
import logging; log = logging.getLogger()

from .. import AutoModPlugin, ShardedBotInstance
from ...types import Embed
from ...modals import AutoReplyModal
from ...views import ChoiceView



class AutoReplyPlugin(AutoModPlugin):
    """Plugin for auto replies"""
    def __init__(self, bot: ShardedBotInstance) -> None:
        super().__init__(bot)


    @discord.app_commands.command()
    @discord.app_commands.guilds()
    async def auto_reply(self, i: discord.Interaction, option: Literal["show", "add", "remove"]):
        """
        auto_reply_help
        """
        option = option.lower()
        ar = self.db.configs.get(i.guild.id, "replies")

        if option == "show":
            if len(ar) < 1: return await i.response.send_message(self.locale.t(i.guild, "no_replies", _emote="NO"))

            e = Embed(
                None,
                title="Auto Replies"
            )
            for name, data in ar.items():
                e.add_field(
                    name=f"__**{name}",
                    value="> **• Triggers:** {} \n> **• Reply:** \n```\n{}\n```".format(
                        ", ".join([f"``{x}``" for x in data["triggers"]]),
                        data["reply"]
                    )
                )
            await i.response.send_message(embed=e)
        elif option == "add":
            async def on_submit(_i: discord.Interaction):
                name: str = _i.data["components"][0]["components"][0]["value"]
                triggers: list = _i.data["components"][1]["components"][0]["value"].split(", ")
                reply: str = _i.data["components"][2]["components"][0]["value"]

                if name.lower() in [x.lower() for x in ar.keys()]:
                    await _i.response.send_message(self.locale.t(_i.guild, "reply_exists", _emote="NO"))
                else:
                    ar.update({
                        name: {
                            "triggers": triggers,
                            "reply": reply
                        }
                    })
                    self.db.configs.update(_i.guild.id, "replies", ar)

                    await _i.response.send_message(self.locale.t(_i.guild, "added_reply", _emote="YES"))

            await i.response.send_modal(AutoReplyModal(self.bot, on_submit))
        elif option == "remove":
            if len(ar) < 1: return await i.response.send_message(self.locale.t(i.guild, "no_replies", _emote="NO"))

            view = ChoiceView(
                "Select the reply you want to delete",
                i.guild,
                list(ar.keys())
            )
            await i.response.send_message(view=view, ephemeral=True)



    @AutoModPlugin.listener()
    async def on_interaction(self, i: discord.Interaction) -> None:
        if i.type == discord.InteractionType.component:
            cid = i.data["custom_id"]
            if "replies" in cid:
                guild = self.bot.get_guild(int(cid.split(":")[0]))
                if guild == None:
                    await i.response.defer(ephemeral=True)
                else:
                    name = i.data["values"][0]
                    ar = self.db.configs.get(i.guild.id, "replies")

                    if not name.lower() in [x.lower() for x in ar.keys()]:
                        await i.response.edit_message(
                            content=self.locale.t(guild, "reply_doesnt_exist", _emote="NO"),
                            view=None
                        )
                    else:
                        del ar[name]
                        self.db.configs.update(guild.id, "replies", ar)

                        await i.response.edit_message(
                            content=self.locale.t(guild, "removed_reply", _emote="YES"),
                            view=None
                        )


async def setup(bot) -> None: await bot.register_plugin(AutoReplyPlugin(bot))