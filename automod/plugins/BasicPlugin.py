import discord
from discord.ext import commands

import googletrans
import time
import requests
import re
from PIL import Image
from io import BytesIO

from .PluginBlueprint import PluginBlueprint
from .Types import DiscordUser, Embed
from utils.Views import AboutView, HelpView
from utils.HelpGenerator import getHelpForCommand



class BasicPlugin(PluginBlueprint):
    def __init__(self, bot):
        super().__init__(bot)
        self.google = googletrans.Translator()
        self.EMOJI_RE = re.compile(r"<:(.+):([0-9]+)>")
        self.CDN = "https://twemoji.maxcdn.com/2/72x72/{}.png"

    
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
            allowed_mentions=discord.AllowedMentions(replied_user=False), 
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
            e = Embed(
                title=self.i18next.t(ctx.guild, "help_title"),
                description=self.i18next.t(ctx.guild, "help_description", prefix=self.bot.get_guild_prefix(ctx.guild))
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
            value="• ID: {} \n• Owner: {} ({})"\
            .format(
                g.id, g.owner, g.owner.id
            )
        )
        e.add_field(
            name="❯ Channels",
            value="• Text: {} \n• Voice: {}"\
            .format(
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
            value="• Roles: {} \n• Emojis: {} \n• Created at: <t:{}>\n• Features: {}"\
            .format(
                len(g.roles), 
                len(g.emojis), 
                round(g.created_at.timestamp()),
                ", ".join(g.features) if len(g.features) > 0 else "None"
            )
        )
        await ctx.send(embed=e)


    @commands.command(aliases=["whois"])
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
            member = ctx.guild.get_member(user.id) or None

        e = Embed(
            color=0xfe7e01 if member is None else member.color
        )
        e.set_thumbnail(
            url=user.display_avatar
        )
        e.add_field(
            name="❯ Information",
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
                value="• Joined at: <t:{}> \n• Roles: {}"\
                .format(
                    round(member.joined_at.timestamp()),
                    len(roles)
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



def setup(bot):
    bot.add_cog(BasicPlugin(bot))