import discord
from discord.ext import commands

import googletrans
import time
import requests
import re
import datetime
from PIL import Image
from io import BytesIO

from .PluginBlueprint import PluginBlueprint
from .Types import DiscordUser, Embed
from utils.Views import AboutView, HelpView
from utils.HelpUtils import getHelpForCommand



actual_plugin_names = {
    "AutomodPlugin": "Automod",
    "UtilityPlugin": "Utility",
    "ModerationPlugin": "Moderation",
    "WarnsPlugin": "Warning",
    "CasesPlugin": "Cases",
    "ConfigPlugin": "Configuration",
    "TagsPlugin": "Tags",
    "FiltersPlugin": "Filters",
    "StarboardPlugin": "Starboard"
}

class UtilityPlugin(PluginBlueprint):
    def __init__(self, bot):
        super().__init__(bot)
        self.google = googletrans.Translator()
        self.EMOJI_RE = re.compile(r"<:(.+):([0-9]+)>")
        self.CDN = "https://twemoji.maxcdn.com/2/72x72/{}.png"
        self.emote_stats = {}
        self.cached_users = {}
        


    def handle_cache_state(self, guild, user):
        _id = f"{guild.id}-{user.id}"
        if not self.db.stats.exists(_id):
            schema = self.schemas.UserStats(_id)
            self.db.stats.insert(schema)
            self.cached_users.update({_id: schema})
        else:
            if not _id in self.cached_users:
                data = self.db.stats.get_doc(_id)
                self.cached_users.update({_id: data})


    @commands.Cog.listener()
    async def on_stats_event(
        self,
        message: discord.Message
    ):
        if message.guild is None:
            return

        if self.db.configs.get(message.guild.id, "message_logging") is False:
            return
        
        _update = {}
        _id = f"{message.guild.id}-{message.author.id}"
        self.handle_cache_state(message.guild, message.author)
        _update.update({
            "total_sent": self.cached_users[_id]["messages"]["total_sent"]+1,
            "last": datetime.datetime.utcnow()
        })
        for k, v in {
            "total_emotes": len(self.EMOJI_RE.findall(message.content)),
            "total_pings": len(message.mentions),
            "total_attachments": len(message.attachments),
        }.items():
            if v > 0:
                _update.update({k: self.cached_users[_id]["messages"][k]+v})
                if k == "total_emotes":
                    if not _id in self.emote_stats:
                        emotes = self.cached_users[_id]["messages"]["used_emotes"]
                        self.emote_stats.update({_id: emotes})
                    else:
                        emotes = self.emote_stats[_id]

                    for name, eid in self.EMOJI_RE.findall(message.content):
                        eid = str(eid)
                        if not eid in emotes:
                            if len(emotes) <= 1:
                                _update.update({
                                    "most_used_emote": {
                                        "name": name,
                                        "id": eid,
                                        "used": 1
                                    }
                                })
                            emotes.update({eid: 1})
                        else:
                            emotes.update({eid: emotes[eid]+1})
                            top = max(emotes, key=emotes.get)
                            if emotes[top] <= emotes[eid]:
                                _update.update({
                                    "most_used_emote": {
                                        "name": name,
                                        "id": eid,
                                        "used": emotes[eid]
                                    }
                                })
                            else:
                                data = self.cached_users[_id]["messages"]["most_used_emote"]
                                _update.update({
                                    "most_used_emote": {
                                        "name": data["name"],
                                        "id": data["id"],
                                        "used": data["used"]+1
                                    }
                                })
                        self.emote_stats.update({_id: emotes})
                        _update.update({"used_emotes": self.emote_stats[_id]})

        new = self.cached_users[_id]["messages"]
        for k, v in _update.items(): new.update({k: v})
        self.db.stats.update_stats(_id, new)


    @commands.Cog.listener()
    async def on_message_delete(
        self,
        message: discord.Message
    ):
        if message.guild is None:
            return

        if self.db.configs.get(message.guild.id, "message_logging") is False:
            return

        _id = f"{message.guild.id}-{message.author.id}"
        self.handle_cache_state(message.guild, message.author)
        self.cached_users[_id]["messages"].update({"total_deleted": self.cached_users[_id]["messages"]["total_deleted"]+1})
        self.db.stats.update(_id, "messages", self.cached_users[_id]["messages"])
        
    
    @commands.command()
    async def about(
        self, 
        ctx
    ):
        """about_help"""
        e = Embed(
            title="AutoMod",
            description=self.i18next.t(ctx.guild, "about_text")
        )
        e.set_thumbnail(url=self.bot.user.avatar.with_size(1024))

        view = AboutView()
        await ctx.send(embed=e, view=view)


    @commands.command()
    async def ping(
        self, 
        ctx
    ):
        """ping_help"""
        bot = self.bot
        t1 = time.perf_counter()
        msg = await ctx.send("Pinging...")
        t2 = time.perf_counter()
        if msg == None:
            return await ctx.send(
                content="Pong! ``{}ms`` \n*Server Latency: ``{}ms``*"\
                .format(round((t2 - t1) * 1000), round(bot.latency * 1000, 2))
            )

        await msg.edit(
            content="Pong! ``{}ms`` \n*Server Latency: ``{}ms``*"\
            .format(round((t2 - t1) * 1000), round(bot.latency * 1000, 2))
        )


    @commands.command()
    async def help(
        self, 
        ctx, 
        *, 
        query: str = None
    ):
        """help_help"""
        if query is None:
            prefix = self.bot.get_guild_prefix(ctx.guild)
            valid_plugins = [self.bot.get_cog(x) for x in self.bot.cogs if x in self.bot.config.enabled_plugins_with_commands]

            e = Embed(
                title=self.i18next.t(ctx.guild, "help_title"),
                #description=self.i18next.t(ctx.guild, "help_footer", prefix=prefix)
            )
            e.set_footer(
                text=self.i18next.t(ctx.guild, "help_footer", prefix=prefix)
            )
            for p in valid_plugins:
                e.add_field(
                    name=f"❯ {actual_plugin_names[p.qualified_name]}",
                    value=" | ".join(f"``{prefix}{x}``" for x in p.get_commands())
                )
            
            view = HelpView(ctx.guild, self.bot, "None")
            await ctx.send(embed=e, view=view)
        else:
            query = "".join(query.splitlines())

            help_message = await getHelpForCommand(self, ctx, query)
            if help_message is None:
                return await ctx.send(self.i18next.t(ctx.guild, "invalid_command", _emote="NO"))
            else:
                await ctx.send(embed=help_message)


    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(manage_messages=True)
    async def server(
        self,
        ctx
    ):
        """server_help"""
        g = ctx.guild

        e = Embed()
        if ctx.guild.icon != None:
            e.set_thumbnail(
                url=ctx.guild.icon.url
            )
        e.add_field(
            name="❯ Information",
            value="• ID: {} \n• Owner: {} ({}) \n• Created at: <t:{}>"\
            .format(
                g.id, g.owner, g.owner.id, round(g.created_at.timestamp())
            )
        )
        e.add_field(
            name="❯ Channels",
            value="• Categories: {} \n• Text: {} \n• Voice: {}"\
            .format(
                len([x for x in g.channels if isinstance(x, discord.CategoryChannel)]),
                len(g.text_channels), 
                len(g.voice_channels)
            )
        )
        e.add_field(
            name="❯ Members",
            value="• Total: {} \n• Users: {} \n• Bots: {}"\
            .format(
                len(g.members), 
                len([x for x in g.members if not x.bot]), 
                len([x for x in g.members if x.bot])
            )
        )
        e.add_field(
            name="❯ Other",
            value="• Roles: {} \n• Emojis: {} \n• Features: {}"\
            .format(
                len(g.roles), 
                len(g.emojis), 
                ", ".join(g.features) if len(g.features) > 0 else "None"
            )
        )
        await ctx.send(embed=e)


    @commands.command(aliases=["whois", "info"])
    @commands.guild_only()
    @commands.has_permissions(manage_messages=True)
    async def userinfo(
        self,
        ctx,
        user: DiscordUser = None
    ):
        """userinfo_help"""
        if user is None:
            if ctx.message.reference == None:
                user = member = ctx.author
            else:
                user = member = ctx.message.reference.resolved.author
        else:
            member: discord.Member = ctx.guild.get_member(user.id) or None

        e = Embed(
            color=0xfe7e01 if member is None else member.color
        )
        e.set_thumbnail(
            url=user.display_avatar
        )
        e.add_field(
            name="❯ User Information",
            value="• ID: {} \n• Profile: {} \n• Created at: <t:{}>"\
            .format(
                user.id,
                user.mention, 
                round(member.created_at.timestamp())
            )
        )
        if member is not None:
            roles = [r.mention for r in reversed(member.roles) if r != ctx.guild.default_role]
            e.add_field(
                name="❯ Server Information",
                value="• Nickname: {} \n• Joined at: <t:{}> \n• Roles: {}"\
                .format(
                    member.nick,
                    round(member.joined_at.timestamp()),
                    len(roles)
                )
            )

            activity_data = self.db.stats.get_doc(member.id)
            e.add_field(
                name="❯ Activity",
                value="• Last message: {} \n• First Message: {}".format(
                    f"<t:{round((activity_data['messages']['last']).timestamp())}>" if activity_data != None else "Never",
                    f"<t:{round((activity_data['messages']['first']).timestamp())}>" if activity_data != None else "Never"
                ) 
            )
        warns = self.db.warns.get(f"{ctx.guild.id}-{user.id}", "warns")
        cases = list(filter(lambda x: x["guild"] == str(ctx.guild.id) and x["target_id"] == str(user.id), self.db.inf.find()))
        e.add_field(
            name="❯ Infractions",
            value="• Warns: {} \n• Cases: {}"\
            .format(
                warns if warns != None else "0",
                len(cases)
            )
        )
        await ctx.send(embed=e)


    @commands.command(aliases=["av"])
    @commands.has_permissions(manage_messages=True)
    async def avatar(
        self,
        ctx,
        user: discord.Member = None
    ):
        """avatar_help"""
        if user == None:
            user = ctx.author

        e = Embed(
            title="Avatar of {0.name}#{0.discriminator}".format(user)
        )
        e.set_image(
            url=user.display_avatar
        )

        await ctx.send(embed=e)


    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def jumbo(
        self,
        ctx,
        *,
        emotes: str
    ):
        """jumbo_help"""
        urls = []
        for e in emotes.split(" ")[:5]:
            if self.EMOJI_RE.match(e):
                _, eid = self.EMOJI_RE.findall(e)[0]
                urls.append("https://cdn.discordapp.com/emojis/{}.png".format(eid))
            else:
                url = self.CDN.format("-".join(
                    c.encode("unicode_escape").decode("utf-8")[2:].lstrip("0")
                    for c in e
                ))
                urls.append(url)

        width, height, images = 0, 0, []
        for url in urls:
            r = requests.get(url)
            try:
                r.raise_for_status()
            except requests.HTTPError:
                return await ctx.send(self.i18next.t(ctx.guild, "http_error", _emoji="NO"))

            img = Image.open(BytesIO(r.content))
            height = img.height if img.height > height else height
            width += img.width + 10
            images.append(img)
        
        image = Image.new("RGBA", (width, height))
        width_offset = 0
        for img in images:
            image.paste(img, (width_offset, 0))
            width_offset += img.width + 10

        combined = BytesIO()
        image.save(combined, "png", quality=55)
        combined.seek(0)
        await ctx.send(file=discord.File(combined, filename="emoji.png"))


    @commands.command()
    async def stats(
        self,
        ctx,
        user: discord.Member = None
    ):
        """stats_help"""
        if self.db.configs.get(ctx.guild.id, "message_logging") is False:
            return await ctx.send(self.i18next.t(ctx.guild, "msg_logging_deactivated", _emote="NO", prefix=self.bot.get_guild_prefix(ctx.guild)))
        
        if user is None:
            user = ctx.author
        
        _id = f"{ctx.guild.id}-{user.id}"
        if not self.db.stats.exists(_id):
            return await ctx.send(self.i18next.t(ctx.guild, "no_stats", _emote="NO"))

        if _id in self.cached_users:
            data = self.cached_users[_id]
        else:
            data = self.db.stats.get_doc(_id)
        data = data["messages"]
        
        e = Embed(
            title="Message Stats",
            description="These stats from {0.name}#{0.discriminator} we're started to be tracked when I joined this server.".format(user)
        )
        e.add_field(
            name="❯ Messages Sent",
            value=str(data["total_sent"]),
            inline=True
        )
        e.add_field(
            name="❯ Messages Deleted",
            value=str(data["total_deleted"]),
            inline=True
        )
        e.add_field(
            name="❯ Emotes Used",
            value=str(data["total_emotes"]),
            inline=True
        )
        e.add_field(
            name="❯ Total Mentions",
            value=str(data["total_pings"]),
            inline=True
        )
        e.add_field(
            name="❯ Total Attachments",
            value=str(data["total_attachments"]),
            inline=True
        )
        data = data["most_used_emote"]
        e.add_field(
            name="❯ Favorite Emote",
            value="{}(``{}``, used {} time{})".format(
                "<:{}:{}> ".format(
                    data["name"],
                    data["id"]
                ) if self.bot.get_emoji(int(data["id"])) != None else "",
                data["name"],
                data["used"],
                "" if data["used"] == 1 else "s"
            ) if data["id"] != "" else "None",
            inline=True
        )

        await ctx.send(embed=e)



def setup(bot): bot.add_cog(UtilityPlugin(bot))