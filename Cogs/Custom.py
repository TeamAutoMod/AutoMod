import discord
from discord.ext import commands

from i18n import Translator
from Utils import Logging, Utils

from Cogs.Base import BaseCog
from Database import Connector, DBUtils, Schemas



db = Connector.Database()


class Custom(BaseCog):
    def __init__(self, bot):
        super().__init__(bot)

    
    @commands.group(name="commands", aliases=["command", "cmd"])
    @commands.guild_only()
    @commands.bot_has_permissions(embed_links=True, external_emojis=True, add_reactions=True)
    async def command(self, ctx):
        """commands_help"""
        if ctx.invoked_subcommand is None:
            custom_commands = ["{}{}".format(ctx.prefix, x["cmdId"].split("-")[1]) for x in db.commands.find() if x["cmdId"].split("-")[0] == str(ctx.guild.id)]
            if len(custom_commands) == 0:
                await ctx.send(Translator.translate(ctx.guild, "no_custom_commands"))
            else:
                e = discord.Embed(
                    color=discord.Color.blurple(),
                    title=Translator.translate(ctx.guild, "custom_commands", guild=ctx.guild.name),
                    description="\n".join(custom_commands)
                )
                e.set_thumbnail(url=ctx.guild.icon_url)
                await ctx.send(embed=e)


    @command.command(aliases=["new", "add"])
    @commands.guild_only()
    async def create(self, ctx, trigger:str, *, reply: str = None):
        """create_help"""
        if len(trigger) == 0:
            await ctx.send(Translator.translate(ctx.guild, "no_trigger"))
        elif reply is None or reply == "":
            await ctx.send(Translator.translate(ctx.guild, "no_reply"))
        elif len(trigger) > 20:
            await ctx.send(Translator.translate(ctx.guild, "trigger_too_long"))
        else:
            trigger = trigger.lower()
            if trigger in ["{}".format(x["cmdId"].split("-")[1]) for x in db.commands.find() if x["cmdId"].split("-")[0] == str(ctx.guild.id)]:
                await ctx.send(Translator.translate(ctx.guild, "command_already_exists"))
            else:
                DBUtils.insert(db.commands, Schemas.command_schema(ctx.guild, trigger, reply, ctx.message.author))
                await ctx.send(Translator.translate(ctx.guild, "command_added", command=trigger))



    @command.command(aliases=["del", "remove"])
    @commands.guild_only()
    async def delete(self, ctx, trigger: str):
        """delete_help"""
        trigger = trigger.lower()
        if len(trigger) > 20:
            await ctx.send(Translator.translate(ctx.guild, "trigger_too_long"))
        elif len([x for x in db.commands.find() if x["cmdId"].split("-")[0] == str(ctx.guild.id)]) == 0:
            await ctx.send(Translator.translate(ctx.guild, "no_custom_commands"))
        elif trigger not in [x["cmdId"].split("-")[1] for x in db.commands.find() if x["cmdId"].split("-")[0] == str(ctx.guild.id)]:
            await ctx.send(Translator.translate(ctx.guild, "command_does_not_exist"))
        else:
            DBUtils.delete(db.commands, "cmdId", f"{ctx.guild.id}-{trigger}")
            await ctx.send(Translator.translate(ctx.guild, "command_removed", command=trigger))

    

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or message.webhook_id is not None:
            return
        if not hasattr(message.channel, "guild") or message.channel.guild is None:
            return
        
        automod = message.guild.me
        if automod is None:
            await Utils.get_member(self.bot, message.guild, self.bot.user.id)
        perms = message.channel.permissions_for(automod)
        if automod is None:
            return
        if not (perms.read_messages and perms.send_messages and perms.embed_links):
            return

        prefix = DBUtils.get(db.configs, "guildId", f"{message.guild.id}", "prefix")
        cmds = ["{}<*>{}".format(x["cmdId"].split("-")[1], x["reply"]) for x in db.commands.find() if x["cmdId"].split("-")[0] == str(message.guild.id)]
        if message.content.startswith(prefix, 0) and len(cmds) > 0:
            for cmd in cmds:
                trigger = cmd.split("<*>")[0]
                if message.content.lower() == prefix + trigger or (message.content.lower().startswith(trigger, len(prefix)) and message.content.lower()[len(prefix + trigger)] == " "):
                    reply = cmd.split("<*>")[1]
                    await message.channel.send(f"{reply}")

            
            
def setup(bot):
    bot.add_cog(Custom(bot))