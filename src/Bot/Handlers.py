import os
import sys
import asyncio
import discord
import concurrent
import traceback
import sentry_sdk
import aiohttp
from concurrent.futures._base import CancelledError
from aiohttp import ClientOSError, ServerDisconnectedError

from datetime import datetime
import time
import logging

from discord import Message, TextChannel, DMChannel, HTTPException, Guild, ConnectionClosed
from discord.ext import commands

from i18n import Translator
from Database import Connector, DBUtils, Schemas
from Utils import Logging, guild_info, Utils, Pages, Emotes
from Utils import Context as context
from Utils.Constants import GREEN_TICK, RED_TICK, SALUTE


log = logging.getLogger(__name__)


db = Connector.Database()


cogs = Utils.from_config("COGS")
async def init_bot(bot):
    bot.locked = True
    try:
        langs = Utils.from_config("SUPPORTED_LANGS")
        await Translator.init_translator(langs)
        await Emotes.init_emotes()

        await Logging.init(bot)
        t = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

        Utils.init(bot)

        _version = await Utils.get_version()
        bot.version = _version
        now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        bot.last_reload = f"{now} UTC"


    except Exception as ex:
        bot.locked = False
        log.error(f"{ex}")
        raise ex
    bot.locked = False




async def on_ready(bot):
    try:
        if not bot.READY:
            log.info(f"AutoMod is starting up with {bot.total_shards} shards")
            bot.fetch_guilds()
            
            await init_bot(bot)
            try:
                for signame in ("SIGTERM", "SIGINT"):
                    asyncio.get_event_loop().add_signal_handler(getattr(signal, signame), lambda: asyncio.ensure_future(Utils.clean_shutdown(bot, signame)))
            except Exception:
                pass


            if not hasattr(bot, "uptime"):
                bot.uptime = datetime.utcnow()

            loaded = 0
            for cog in cogs:
                try:
                    bot.load_extension("Plugins.%s" % (cog))
                    loaded += 1
                    log.info(f"Successfully loaded {cog}")
                except Exception as e:
                    log.error("Error while loading %s: %s" % (cog, e))
            log.info(f"AutoMod running at full speed, now starting cache filling!")
            t = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
            bot.READY = True
        else:
            pass # bot is ready
        
        bot.missing_guilds = []
        bot.missing_guilds = {g.id for g in bot.guilds}
        if bot.loading_task is not None:
            bot.loading_task.cancel()
        bot.loading_task = asyncio.create_task(fill_cache(bot))
    except Exception as e:
        log.error(f"Error while starting, aborting! \n{e}")



async def fill_cache(bot):
    try:
        while len(bot.missing_guilds) > 0:
            start_time = time.time()
            old = len(bot.missing_guilds)
            while len(bot.missing_guilds) > 0: 
                try:
                    tasks = [asyncio.create_task(cache_guild(bot, guild_id)) for guild_id in bot.missing_guilds]
                    await asyncio.wait_for(await asyncio.gather(*tasks), 600)
                except (CancelledError, concurrent.futures._base.CancelledError, asyncio.exceptions.CancelledError):
                    pass
                except concurrent.futures._base.TimeoutError:
                    if old == len(bot.missing_guilds):
                        log.info("Timed out while fetching member chunks.")
                        for t in tasks:
                            t.cancel()
                        await asyncio.sleep(1)
                        continue
                except Exception as e:
                    log.error(f"Fetching member info failed: \n{e}")
                else:
                    if old == len(bot.missing_guilds):
                        log.error("Timed out while fetching member chunks.")
                        for t in tasks:
                            t.cancel()
                        continue
            end_time = time.time()
            time_needed = (end_time - start_time)
            log.info("Finished fetching members in {}".format(time_needed))

            # check for guilds that aren't in the DB for some reason (added during downtime etc)
            log.info("Filling up missing guilds")
            for g in [x for x in bot.guilds if isinstance(x, discord.Guild)]:
                if not DBUtils.get(db.configs, "guildId", f"{g.id}", "prefix"):
                    try:
                        DBUtils.insert(db.configs, Schemas.guild_schema(g))
                        log.info(f"Filled missing guild: {g}")
                    except Exception as ex:
                        log.error(f"Error while trying to fill up missing guild {g}: \n{ex}")
            log.info("Fill-up task completed!")
            end_time2 = time.time()
            t = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
            log.info(f"Finished building the internal cache in {round(end_time2 - start_time, 2)} seconds")
            bot.initial_fill_complete = True
    except Exception as e:
        await log.error(f"Guild fetching failed \n{e}")
    finally:
        bot.cache.build(_return=False)
        bot.loading_task = None



async def cache_guild(bot, guild_id):
    guild = bot.get_guild(guild_id)
    try:
        await guild.chunk(cache=True)
    except Exception:
        pass
    if guild_id in bot.missing_guilds:
        bot.missing_guilds.remove(guild_id)


now = None

async def check_mutes(bot):
    while True: # all guilds need to be fetched for this
        await asyncio.sleep(10)
        try:
            if len([_ for _ in db.mutes.find()]) > 0:   
                for mute in db.mutes.find():
                    guild = bot.get_guild(int(mute["mute_id"].split("-")[0]))
                    target = discord.utils.get(guild.members, id=int(mute["mute_id"].split("-")[1]))

                    if datetime.utcnow() > mute["ending"]:
                        try:
                            mute_role_id = DBUtils.get(db.configs, "guildId", f"{guild.id}", "muteRole")
                            mute_role = guild.get_role(int(mute_role_id))
                            
                            await target.remove_roles(mute_role)
                        except Exception:
                            pass
                        else:
                            on_time = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
                            await Logging.log_to_guild(guild.id, "memberLogChannel", Translator.translate(guild, "log_unmute", _emote="UNMUTE", on_time=on_time, user=target, user_id=target.id))
                            DBUtils.delete(db.mutes, "mute_id", f"{mute['mute_id'].split('-')[0]}-{mute['mute_id'].split('-')[1]}")
                    else:
                        pass
        except AttributeError:
            # this happens if the guild object is a NoneType (most likely because it hasn't been cached yet)
            pass




async def on_message(bot, message: Message):
    if bot.initial_fill_complete and message.guild is not None:
        try:
            await message.guild.chunk(cache=True)
            log.info("Cached a missing guild: {}".format(str(guild.id)))
        except Exception:
            pass
    if message.author.bot:
        if message.author.id == bot.user.id:
            bot.own_messages += 1
        else:
            bot.bot_messages += 1
        return
    ctx = await bot.get_context(message, cls=context.Context)
    bot.user_messages += 1
    if ctx.valid and ctx.command is not None:
        bot.command_count = bot.command_count + 1
        if isinstance(ctx.channel, DMChannel) or ctx.guild is None:
            return
        elif isinstance(ctx.channel, TextChannel) and not ctx.channel.permissions_for(ctx.channel.guild.me).send_messages:
            try:
                await ctx.author.send(Translator.translate(ctx.guild, "cant_send_message"))
            except Exception:
                pass
        else:
            await bot.invoke(ctx)



async def on_guild_join(bot, guild: Guild):
    if guild.id in Utils.from_config("BLOCKED_GUILDS"):
        log.info(f"Someone tried adding me to blocked guild {guild.name} ({guild.id})")
        await guild.leave()
    else:
        bot.missing_guilds.add(guild.id)
        await guild.chunk(cache=True)
        bot.missing_guilds.remove(guild.id)
        DBUtils.insert(db.configs, Schemas.guild_schema(guild))
        await Logging.guild_log(bot, f"I was added to a new guild: {guild.name} ({guild.id}).")



async def on_guild_remove(bot, guild: Guild):
    DBUtils.delete(db.configs, "guildId", f"{guild.id}")
    await Logging.guild_log(bot, f"I was removed from a guild: {guild.name} ({guild.id})") 



async def on_guild_update(before, after):
    if before.name != after.name:
        DBUtils.update(db.configs, "guildId", f"{before.id}", "guildName", f"{after.name}")


class NotCachedException(commands.CheckFailure):
    pass


def replace_lookalikes(text):
    for k, v in {"`": "ˋ"}.items():
        text = text.replace(k, v)
    return text




class PostParseError(commands.BadArgument):

    def __init__(self, type, error):
        super().__init__(None)
        self.type = type
        self.error = error



async def on_command_error(bot, ctx, error):
    if isinstance(error, NotCachedException):
        if bot.loading_task is not None:
            if bot.initial_fill_complete:
                await ctx.send(Translator.translate(ctx.guild, "still_caching"))
            else:
                await ctx.send(Translator.translate(ctx.guild, "still_getting_member_info"))
        else:
            await ctx.send(Translator.translate(ctx.guild, "just_joined"))
    if isinstance(error, commands.BotMissingPermissions):
        await ctx.send(Translator.translate(ctx.guild, "missing_bot_perms", _emote="LOCK"))
    elif isinstance(error, commands.CommandNotFound):
        pass
    elif isinstance(error, commands.MissingRequiredArgument):
        param = list(ctx.command.params.values())[min(len(ctx.args) + len(ctx.kwargs), len(ctx.command.params))]
        bot.help_command.context = ctx
        usage = bot.help_command.get_command_signature(ctx.command)
        arg = param._name
        await ctx.send(Translator.translate(ctx.guild, "missing_arg", _emote="NO", arg=arg, usage=usage))
    elif isinstance(error, PostParseError):
        bot.help_command.context = ctx
        usage = bot.help_command.get_command_signature(ctx.command)
        arg = error.type
        real_error = error.error
        await ctx.send(Translator.translate(ctx.guild, "arg_parse_error", _emote="NO", arg=arg, error=real_error, usage=usage))
    elif isinstance(error, commands.BadArgument):
        param = list(ctx.command.params.values())[min(len(ctx.args) + len(ctx.kwargs), len(ctx.command.params))]
        bot.help_command.context = ctx
        usage = bot.help_command.get_command_signature(ctx.command)
        arg = param._name
        real_error = replace_lookalikes(str(error))
        await ctx.send(Translator.translate(ctx.guild, "arg_parse_error", _emote="NO", arg=arg, error=real_error, usage=usage))
    elif isinstance(error, commands.CommandNotFound):
        return
    elif isinstance(error, commands.CommandOnCooldown):
        await ctx.send(Translator.translate(ctx.guild, "on_cooldown", retry_after=round(error.retry_after)))
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send(Translator.translate(ctx.guild, "missing_user_perms", _emote="LOCK"))
