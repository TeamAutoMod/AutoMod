# type: ignore

import asyncio
import discord
from discord.ext import commands

import logging; log = logging.getLogger()
from twitchAPI.twitch import Twitch
from twitchAPI.eventsub import EventSub
from toolbox import S as Object
from typing import Union
import asyncio

from .. import AutoModPluginBlueprint, ShardedBotInstance
from ...types import Embed, E
from ...schemas import Alert



class AlertsPlugin(AutoModPluginBlueprint):
    """Plugin for alerts"""
    def __init__(
        self, 
        bot: ShardedBotInstance
    ) -> None:
        super().__init__(bot)
        self._event_sub: EventSub = None # for type hint
        self._twitch: Twitch = None
        self._stream_data = {}
        if hasattr(self.config, "twitch_callback_url"):
            if self.config.twitch_callback_url != "":
                self.bot.loop.create_task(self._init_twitch_event_sub())


    def cog_unload(
        self
    ) -> None:
        try:
            self._event_sub.stop()
        except Exception:
            pass


    async def _init_twitch_event_sub(
        self
    ) -> None:
        twitch = self._twitch = Twitch(
            self.config.twitch_app_id, 
            self.config.twitch_secret
        ); twitch.authenticate_app([])

        sub = EventSub(
            self.config.twitch_callback_url,  
            self.config.twitch_app_id,
            8080,
            twitch
        ); sub.wait_for_subscription_confirm = False
        setattr(self, "_event_sub", sub)

        self._event_sub.unsubscribe_all()
        self._event_sub.start()

        for streamer in self.db.alerts.find({}):
            try:
                obj = Object(list((twitch.get_users(logins=[streamer["id"]])).values())[0][0])
                sub_id = self._event_sub.listen_channel_update(obj.id, self.on_live)
            except Exception as ex:
                log.warn(f"Failed to add event listener for streamer {streamer['id']} - {ex}"); sub_id = None
            else:
                self._stream_data.update({
                    obj.display_name.lower(): {
                        "offline_image_url": obj.offline_image_url,
                        "profile_image_url": obj.profile_image_url,
                        "sub_id": sub_id
                    }
                })


    def get_channel(
        self,
        channel_id: int
    ) -> Union[
        discord.TextChannel,
        None
    ]:
        return self.bot.get_channel(channel_id)


    async def on_live(
        self,
        data: dict
    ) -> None:
        data = Object(data)
        
        name = data.event.broadcaster_user_login
        send_to = self.db.alerts.get(name.lower(), "in")
        if send_to == None: return
        if len(send_to) < 1: return

        for _, cid in send_to.items():
            channel = self.get_channel(int(cid))
            if channel != None:
                e = Embed(
                    None,
                    color=0x6441a5,
                    title=f"**{data.event.title}**"
                )
                e.set_author(
                    name=f"{name} - Twitch",
                    icon_url=self._stream_data[name.lower()].get(
                        "profile_image_url",
                        "https://cdn.pixabay.com/photo/2021/12/10/16/38/twitch-6860918_960_720.png"
                    ),
                    url=f"https://twitch.tv/{name}"
                )
                e.set_image(
                    url="https://wallpaperset.com/w/full/1/e/6/116482.jpg"
                )
                e.set_footer(
                    text=f"Now live, playing {data.event.category_name}"
                )
                try:
                    asyncio.run_coroutine_threadsafe(
                        channel.send(embed=e),
                        loop=self.bot.loop
                    )
                except Exception:
                    pass


    def get_alerts(
        self,
        guild: discord.Guild
    ) -> dict:
        active = {}
        for streamer in self.db.alerts.find({}):
            if str(guild.id) in streamer["in"]:
                active.update({
                    streamer["id"]: streamer["in"][str(guild.id)]
                })
        return active


    async def unsub_callback(
        self
    ) -> None:
        pass


    alerts = discord.app_commands.Group(
        name="alerts",
        description="👾 Configure Twitch alerts",
        default_permissions=discord.Permissions(manage_guild=True)
    )
    @alerts.command(
        name="show",
        description="👾 Shows all current Twitch alerts"
    )
    @discord.app_commands.default_permissions(manage_guild=True)
    async def alerts_show(
        self,
        ctx: discord.Interaction
    ) -> None:
        """
        alerts_show_help
        examples:
        -alerts show
        """
        active = self.get_alerts(ctx.guild)
        
        if len(active) < 1:
            return await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "no_alerts", _emote="NO", cmd=f"</alerts add:{self.bot.internal_cmd_store.get('alerts')}>"), 0))
        
        e = Embed(
            ctx,
            title="Twitch Alerts"
        )
        for streamer, cid in active.items():
            e.add_field(
                name=f"**❯ __{streamer}__**",
                value=f"> **Channel:** <#{cid}>"
            )
        
        await ctx.response.send_message(embed=e)


    @alerts.command(
        name="add",
        description="✅ Adds a new Twitch alert"
    )
    @discord.app_commands.describe(
        streamer="The streamer you want to add the alert for",
        channel="The channel where the alert should be posted"
    )
    @discord.app_commands.default_permissions(manage_guild=True)
    async def alerts_add(
        self,
        ctx: discord.Interaction,
        streamer: str,
        channel: discord.TextChannel
    ) -> None:
        """
        alerts_add_help
        examples:
        -alerts add xqc #live
        """
        raw = self._twitch.get_users(logins=[streamer])
        if len(raw) < 1:
            return await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "no_streamer", _emote="NO"), 0))

        if len(self.get_alerts(ctx.guild)) > 6:
            return await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "max_alerts", _emote="NO"), 0))

        try:
            self._event_sub.listen_channel_update(
                Object(list(raw.values())[0][0]).id, 
                self.on_live
            )
        except Exception:
            pass

        streamer = streamer.lower()
        doc = self.db.alerts.get_doc(streamer)
        if doc != None:
            _in = doc["in"]
            if str(ctx.guild.id) in _in:
                await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "streamer_exists", _emote="NO"), 0))
            else:
                _in.update({
                    f"{ctx.guild.id}": f"{channel.id}"
                })
                self.db.alerts.update(streamer, "in", _in)
                await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "streamer_added", _emote="YES", streamer=streamer, channel=channel.mention), 1))
        else:
            self.db.alerts.insert(Alert(streamer, ctx.guild, channel))
            await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "streamer_added", _emote="YES", streamer=streamer, channel=channel.mention), 1))


    @alerts.command(
        name="remove",
        description="❌ Removes the alert for a streamer"
    )
    @discord.app_commands.describe(
        streamer="The streamer you want to remove the alert for"
    )
    @discord.app_commands.default_permissions(manage_guild=True)
    async def alerts_remove(
        self,
        ctx: discord.Interaction,
        streamer: str,
    ) -> None:
        """
        alerts_remove_help
        examples:
        -alerts remove xqc
        """
        raw = self._twitch.get_users(logins=[streamer])
        if len(raw) < 1:
            return await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "no_streamer", _emote="NO"), 0))

        if len(self.get_alerts(ctx.guild)) < 1:
            return await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "no_alerts", _emote="NO", cmd=f"</alerts add:{self.bot.internal_cmd_store.get('alerts')}>"), 0))

        streamer = streamer.lower()
        doc = self.db.alerts.get_doc(streamer)
        if doc == None:
            await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "no_alert", _emote="NO"), 0))
        else:
            _in = doc["in"]
            if not str(ctx.guild.id) in _in:
                await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "no_alert", _emote="NO"), 0))
            else:
                del _in[str(ctx.guild.id)]
                self.db.alerts.update(streamer, "in", _in)

                try:
                    self._twitch.delete_eventsub_subscription(self._stream_data.get("sub_id"))
                except Exception:
                    pass

                await ctx.response.send_message(embed=E(self.locale.t(ctx.guild, "streamer_removed", _emote="YES", streamer=streamer), 1))


async def setup(bot) -> None: await bot.register_plugin(AlertsPlugin(bot))