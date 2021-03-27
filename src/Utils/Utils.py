import logging
import subprocess
from subprocess import Popen
import os
import json
import asyncio
import datetime
import argparse
import numpy as np

from Utils import Logging
from Database import Connector, DBUtils

from collections import namedtuple, OrderedDict, Collection
from discord import NotFound, DiscordException



log = logging.getLogger(__name__)

BOT = None
CONFIG = None
LOADED_CONFIG = False
invalid_users = []
user_cache = OrderedDict()
db = Connector.Database()

def init(actual_bot):
    global BOT
    BOT = actual_bot


def init_config():
    global CONFIG, LOADED_CONFIG
    try:
        with open("./Config/config.json", "r") as f:
            CONFIG = json.load(f)
            LOADED_CONFIG = True
    except Exception as ex:
        log.error(f"[Config] Error while trying to set the master variables: {ex}")



def from_config(key):
    global CONFIG, LOADED_CONFIG
    if not LOADED_CONFIG:
        init_config()
    try:
        return CONFIG[key]
    except KeyError:
        log.error(f"[Config] Couldn't find anything for {key} in master.json")


async def clean_shutdown(bot, trigger):
    log.info(f"[Info] AutoMod is shutting down, triggered by {trigger}")
    await bot.logout()
    await bot.close()


async def get_user(user_id, fetch=True):
    user = BOT.get_user(user_id)
    if user is None:
        if user_id in invalid_users:
            return None
    
        if user_id in user_cache:
            return user_cache[user_id]
        if fetch:
            try:
                user = await BOT.fetch_user(user_id)
                if len(user_cache) >= 10:
                    user_cache.popitem()
                user_cache[user_id] = user
            except NotFound:
                invalid_users.append(user_id)
                return None
    return user



async def get_member(bot, guild, uid):
    member = guild.get_member(uid)
    if member is None and guild.id in bot.missing_guilds:
        try:
            member = await guild.fetch_member(uid)
        except DiscordException:
            return None
    return member



def trim_msg(msg, char_limit):
    if len(msg) < char_limit - 4:
        return msg
    return "{}...".format(msg[:char_limit-4])


async def basic_cleaning(ctx, search): # simply cleans the bots messages
    deleted = 0
    async for msg in ctx.history(limit=search, before=ctx.message):
        if msg.author == ctx.me:
            await msg.delete()
            deleted += 1
    return deleted


async def complex_cleaning(ctx, search): # also cleans messages that have the bots prefix in them
    prefix = DBUtils.get(db.configs, "guildId", f"{ctx.guild.id}", "prefix")

    def check(m):
        return m.author == ctx.me or m.content.startswith(prefix)
        
    deleted = await ctx.channel.purge(limit=search, check=check, before=ctx.message)
    return len(deleted)


async def perform_shell_code(cmd):
    _popen = Popen(cmd, cwd=os.getcwd(), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    while _popen.poll() is None:
        await asyncio.sleep(1)
    output, error = _popen.communicate()
    return _popen.returncode, output.decode("utf-8").strip(), error.decode("utf-8").strip()


async def get_version():
    code, output, error = await perform_shell_code("git rev-parse --short FETCH_HEAD")
    return output


def is_close(root, to_check, threshold: float) -> bool:
    rows = len(root) + 1
    cols = len(to_check) + 1
    distance = np.zeros((rows, cols), dtype=int)

    for i in range(1, rows):
        for k in range(1, cols):
            distance[i][0] = i
            distance[0][k] = k


    for col in range(1, cols):
        for row in range(1, rows):
            if root[row-1] == to_check[col-1]:
                cost = 0
            else:
                cost = 2
            
            distance[row][col] = min(distance[row-1][col] + 1, distance[row][col-1] + 1, distance[row-1][col-1] + cost)

    ratio = ((len(root) + len(to_check)) - distance[row][col]) / (len(root) + len(to_check)) * 100
    return ratio >= threshold


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument(
        "--total_shards", "-shards", help="Amount of shards to start the bot with"
    )
    return p.parse_args()