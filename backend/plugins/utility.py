import discord
from discord.ext import commands

import time
import re
import requests
from PIL import Image
from io import BytesIO

from . import AutoModPlugin
from ..types import Embed, DiscordUser
from ..views import AboutView



ACTUAL_PLUGIN_NAMES = {
    "UtilityPlugin": "Utility",
    "ModerationPlugin": "Moderation",
    "ConfigPlugin": "Configuration",
    "TagsPlugin": "Custom Commands",
    "CasesPlugin": "Cases"
}
EMOJI_RE = re.compile(r"<:(.+):([0-9]+)>")
CDN = "https://twemoji.maxcdn.com/2/72x72/{}.png"


def get_help_embed(plugin, ctx, cmd):
    plugin.bot.help_command.context = ctx
    name = ctx.bot.help_command.get_command_signature(cmd)
    help_message = plugin.locale.t(ctx.guild, f"{cmd.help}")
    if name[-1] == " ": name = name[:-1]

    e = Embed(
        title=f"``{name.replace('...', '')}``"
    )
    e.add_field(
        name="❯ Description", 
        value=help_message
    )

    if isinstance(cmd, commands.GroupMixin) and hasattr(cmd, "all_commands"):
        actual_subcommands = {}
        for k, v in cmd.all_commands.items():
            if not v in actual_subcommands.values():
                actual_subcommands[k] = v

        if len(actual_subcommands.keys()) > 0:
            e.add_field(name="❯ Subcommands", value=", ".join([f"``{x}``" for x in actual_subcommands.keys()]), inline=True)

    return e


def get_command_help(plugin, ctx, query):
    cmd = plugin.bot
    layers = query.split(" ")

    while len(layers) > 0:
        layer = layers.pop(0)
        if hasattr(cmd, "all_commands") and layer in cmd.all_commands.keys():
            cmd = cmd.all_commands[layer]
        else:
            cmd = None; break
    
    if cmd != None and cmd != plugin.bot.all_commands:
        return get_help_embed(plugin, ctx, cmd)
    else:
        return None


class UtilityPlugin(AutoModPlugin):
    """Plugin for all utility commands"""
    def __init__(self, bot):
        super().__init__(bot)


    @commands.command()
    async def ping(self, ctx):
        """ping_help"""
        # REST API
        msg_t1 = time.perf_counter()
        msg = await ctx.send("Pinging...")
        msg_t2 = time.perf_counter()

        # Database
        db_t1 = time.perf_counter()
        self.db.command("ping")
        db_t2 = time.perf_counter()

        # Shard
        shard = self.bot.get_shard(ctx.guild.shard_id)
        
        await msg.edit(content="• **Rest:** {}ms \n• **Client:** {}ms \n• **Shard:** {}ms \n• **Database:** {}ms".format(
            round((msg_t2 - msg_t1) * 1000),
            round(self.bot.latency * 1000),
            round(shard.latency * 1000),
            round((db_t2 - db_t1) * 1000)
        ))


    @commands.command()
    async def about(self, ctx):
        """about_help"""
        e = Embed(
            title="AutoMod",
            description=self.locale.t(ctx.guild, "about_description")
        )
        e.set_thumbnail(url=ctx.guild.me.display_avatar)
        e.add_fields([
            {
                "name": "❯ Stats",
                "value": "> **• Guilds:** {} \n> **• Users:** {} \n> **• Shards:** {}"\
                .format(
                    len(self.bot.guilds),
                    len(self.bot.users),
                    len(self.bot.shards)
                )
            },
            {
                "name": "❯ Usage",
                "value": "> **• Commands:** {} \n> **• Custom Commands:** {}"\
                .format(
                    self.bot.used_commands,
                    self.bot.used_tags
                )
            }
        ])
        await ctx.send(embed=e, view=AboutView(self.bot))


    @commands.command()
    async def help(self, ctx, *, query: str = None):
        """help_help"""
        if query == None:
            prefix = self.get_prefix(ctx.guild)

            e = Embed(
                title="Command List",
                description=self.locale.t(ctx.guild, "help_desc", prefix=prefix)
            )
            for p in [self.bot.get_plugin(x) for x in self.bot.plugins if x in ACTUAL_PLUGIN_NAMES]:
                cmds = p.get_commands()
                e.add_field(
                    name=f"❯ {ACTUAL_PLUGIN_NAMES[p.qualified_name]} [{len(cmds)}]",
                    value=", ".join([f"``{x}``" for x in cmds])
                )
            
            await ctx.send(embed=e)
        else:
            query = "".join(query.splitlines())

            _help = get_command_help(self, ctx, query)
            if _help == None:
                return await ctx.send(self.locale.t(ctx.guild, "invalid_command", _emote="NO"))
            else:
                await ctx.send(embed=_help)



    @commands.command(aliases=["av"])
    async def avatar(self, ctx, user: discord.Member = None):
        """avatar_help"""
        if user == None: user = ctx.author

        e = Embed(
            title="{0.name}#{0.discriminator}'s Avatar".format(user)
        )
        e.set_image(
            url=user.display_avatar
        )

        await ctx.send(embed=e)


    @commands.command()
    async def jumbo(self, ctx, *, emotes: str):
        """jumbo_help"""
        urls = []
        for e in emotes.split(" ")[:5]:
            if EMOJI_RE.match(e):
                _, eid = EMOJI_RE.findall(e)[0]
                urls.append("https://cdn.discordapp.com/emojis/{}.png".format(eid))
            else:
                url = CDN.format("-".join(
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
                return await ctx.send(self.locale.t(ctx.guild, "http_error", _emote="NO"))

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

    
    @commands.command(aliases=["info", "userinfo", "user"])
    @AutoModPlugin.can("manage_messages")
    async def whois(self, ctx, user: DiscordUser = None):
        """whois_help"""
        if user == None:
            if ctx.message.reference == None:
                user = member = ctx.author
            else:
                user = member = ctx.message.reference.resolved.author
        else:
            member = discord.Member = ctx.guild.get_member(user.id) or None

        e = Embed()
        e.set_thumbnail(
            url=user.display_avatar
        )
        e.add_field(
            name="❯ User Information",
            value="> **• ID:** {} \n> **• Profile:** {} \n> **• Created at:** <t:{}>"\
            .format(
                user.id,
                user.mention, 
                round(user.created_at.timestamp())
            )
        )
        if member is not None:
            roles = [r.mention for r in reversed(member.roles) if r != ctx.guild.default_role]

            warns = self.db.warns.get(f"{ctx.guild.id}-{user.id}", "warns")
            cases = list(filter(lambda x: x["guild"] == str(ctx.guild.id) and x["user_id"] == str(user.id), self.db.cases.find()))

            e.add_fields([
                {
                    "name": "❯ Server Information",
                    "value": "> **• Nickname:** {} \n> **• Joined at:** <t:{}> \n> **• Roles:** {}"\
                    .format(
                        member.nick,
                        round(member.joined_at.timestamp()),
                        len(roles)
                    )
                },
                {
                    "name": "❯ Infractions",
                    "value": "> **• Warns:** {} \n> **• Cases:** {}"\
                    .format(
                        warns if warns != None else "0",
                        len(cases)
                    )
                }

            ])
            await ctx.send(embed=e)


    @commands.command(aliases=["guild", "serverinfo"])
    @commands.guild_only()
    @AutoModPlugin.can("manage_messages")
    async def server(self, ctx):
        """server_help"""
        g = ctx.guild

        e = Embed()
        if ctx.guild.icon != None:
            e.set_thumbnail(
                url=ctx.guild.icon.url
            )
        
        e.add_fields([
            {
                "name": "❯ Information",
                "value": "> **• ID:** {} \n> **• Owner:** {} ({}) \n> **• Created at:** <t:{}>"\
                .format(
                    g.id, g.owner, g.owner.id, round(g.created_at.timestamp())
                )
            },
            {
                "name": "❯ Channels",
                "value": "> **• Categories:** {} \n> **• Text:** {} \n> **• Voice:** {}"\
                .format(
                    len([x for x in g.channels if isinstance(x, discord.CategoryChannel)]),
                    len(g.text_channels), 
                    len(g.voice_channels)
                )
            },
            {
                "name": "❯ Members",
                "value": "> **• Total:** {} \n> **• Users:** {} \n> **• Bots:** {}"\
                .format(
                    len(g.members), 
                    len([x for x in g.members if not x.bot]), 
                    len([x for x in g.members if x.bot])
                )
            },
            {
                "name": "❯ Other",
                "value": "> **• Roles:** {} \n> **• Emojis:** {} \n> **• Features:** {}"\
                .format(
                    len(g.roles), 
                    len(g.emojis), 
                    ", ".join(g.features) if len(g.features) > 0 else "None"
                )
            }
        ])
        await ctx.send(embed=e)


def setup(bot): bot.register_plugin(UtilityPlugin(bot))
