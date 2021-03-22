import discord
from discord.ext import commands
import asyncio

from i18n import Translator
from Utils import Logging, Utils

from Cogs.Base import BaseCog
from Database import Connector, DBUtils, Schemas



db = Connector.Database()


class Custom(BaseCog):
    def __init__(self, bot):
        super().__init__(bot)
        self.command_cache = dict()
        self.bot.loop.create_task(self.cache_commands())

    
    async def cache_commands(self):
        while len(self.command_cache) < len([_ for _ in db.commands.find()]):
            await asyncio.sleep(10)
            for doc in db.commands.find():
                gid = doc["cmdId"].split("-")[0]
                trigger = doc["cmdId"].split("-")[1]
                reply = doc["reply"]
                if not gid in self.command_cache:
                    self.command_cache[gid] = [{"trigger": trigger, "reply": reply}]
                else:
                    if not trigger in [x["trigger"] for x in self.command_cache[gid]]:
                        self.command_cache[gid].append({"trigger": trigger, "reply": reply})
                    else:
                        pass


    
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
                    title=Translator.translate(ctx.guild, "custom_commands", guild_name=ctx.guild.name),
                    description="\n".join(custom_commands)
                )
                e.set_thumbnail(url=ctx.guild.icon_url)
                await ctx.send(embed=e)


    @command.command(aliases=["new", "add"])
    @commands.guild_only()
    async def create(self, ctx, trigger: str, *, reply: str = None):
        """create_help"""
        if len(trigger) == 0:
            await ctx.send(Translator.translate(ctx.guild, "no_trigger", _emote="THINK"))
        elif reply is None or reply == "":
            await ctx.send(Translator.translate(ctx.guild, "no_reply", _emote="THINK"))
        elif len(trigger) > 20:
            await ctx.send(Translator.translate(ctx.guild, "trigger_too_long"))
        else:
            trigger = trigger.lower()
            if trigger in ["{}".format(x["cmdId"].split("-")[1]) for x in db.commands.find() if x["cmdId"].split("-")[0] == str(ctx.guild.id)]:
                await ctx.send(Translator.translate(ctx.guild, "command_already_exists"))
            else:
                DBUtils.insert(db.commands, Schemas.command_schema(ctx.guild, trigger, reply, ctx.message.author))
                try:
                    self.command_cache[str(ctx.guild.id)].append({"trigger": trigger, "reply": reply})
                except Exception:
                    self.command_cache[str(ctx.guild.id)] = [{"trigger": trigger, "reply": reply}]
                finally:
                    await ctx.send(Translator.translate(ctx.guild, "command_added", _emote="YES", command=trigger))



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
            possible = []
            for cmd in [x["cmdId"].split("-")[1].lower() for x in db.commands.find() if x["cmdId"].split("-")[0] == str(ctx.guild.id)]:
                if Utils.is_close(trigger, cmd, 75.0):
                    possible.append(cmd)
                else:
                    pass
            if len(possible) > 0:
                await ctx.send(Translator.translate(ctx.guild, "command_does_not_exist_but_possible", possible="\n".join(possible)))
            else:
                await ctx.send(Translator.translate(ctx.guild, "command_does_not_exist"))

        else:
            DBUtils.delete(db.commands, "cmdId", f"{ctx.guild.id}-{trigger}")
            self.command_cache[str(ctx.guild.id)] = [_ for _ in self.command_cache[str(ctx.guild.id)] if _["trigger"].lower() != trigger]
            await ctx.send(Translator.translate(ctx.guild, "command_removed", _emote="YES", command=trigger))

    

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
        if message.author.id == self.bot.user.id:
            return

        prefix = DBUtils.get(db.configs, "guildId", f"{message.guild.id}", "prefix")
        try:
            cmds = self.command_cache[str(message.guild.id)]
        except KeyError:
            return
        if message.content.startswith(prefix, 0) and len(cmds) > 0:
            for entry in cmds:
                trigger = entry["trigger"]
                if message.content.lower() == prefix + trigger or (message.content.lower().startswith(trigger, len(prefix)) and message.content.lower()[len(prefix + trigger)] == " "):
                    reply = entry["reply"]
                    return await message.channel.send(f"{reply}")

            
            
def setup(bot):
    bot.add_cog(Custom(bot))