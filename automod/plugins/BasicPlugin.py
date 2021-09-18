import discord
from discord.ext import commands

import googletrans
import time

from .PluginBlueprint import PluginBlueprint
from .Types import DiscordUser, Embed
from utils.Views import AboutView, HelpView
from utils.HelpGenerator import getHelpForCommand



class BasicPlugin(PluginBlueprint):
    def __init__(self, bot):
        super().__init__(bot)
        self.google = googletrans.Translator()

    
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
            e = Embed(
                title=self.i18next.t(ctx.guild, "help_title"),
                description=self.i18next.t(ctx.guild, "help_description", prefix=self.bot.get_guild_prefix(ctx.guild))
            )
            e.set_image(
                url="https://cdn.discordapp.com/attachments/874097242598961152/888160308227629076/banner.png"
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
            user = member = ctx.author
        else:
            member = None if ctx.guild is None else await self.bot.utils.getUser(user.id)

        e = Embed(
            color=None if member is None else member.color
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



def setup(bot):
    bot.add_cog(BasicPlugin(bot))