import discord

import asyncio



async def finishCleaning(plugin, channel_id):
    await asyncio.sleep(1)
    del plugin.cleaning[channel_id]


async def cleanMessages(plugin, ctx, category, amount, predicate, before=None, after=None, check_amount=None):
    if not hasattr(plugin, "cleaning"):
        plugin.cleaning = dict()
    count = 0

    if ctx.channel.id in plugin.cleaning:
        return await ctx.send(plugin.i18next.t(ctx.guild, "already_cleaning", _emote="WARN"))
    plugin.cleaning[ctx.channel.id] = set()

    try:
        def check(msg):
            nonlocal count
            match = predicate(msg) and count < amount
            if match:
                count += 1
            return match

        # limit = min(amount, 500) if check_amount is None else check_amount
        # fetched = await ctx.channel.history(
        #     limit=limit,
        #     before=before if before else None,
        #     after=after
        # ).flatten()
        # if len(fetched) <= limit:
        #     limit = len(fetched)
        # else:
        #     limit = limit

        try:
            deleted = await ctx.channel.purge(
                limit=min(amount, 500) if check_amount is None else check_amount, 
                check=check, 
                before=before if before else None,
                after=after
            )
        except discord.Forbidden:
            raise
        except discord.NotFound:
            await asyncio.sleep(1)
            await ctx.send(plugin.i18next.t(ctx.guild, "already_cleaned", _emote="WARN"))
        
        else:
            await ctx.send(plugin.i18next.t(ctx.guild, "messages_deleted", _emote="YES", count=len(deleted), plural="" if len(deleted) == 1 else "s"), delete_after=5)
            await plugin.action_logger.log(
                ctx.guild,
                "clean",
                moderator=ctx.message.author,
                moderator_id=ctx.message.author.id,
                count=len(deleted),
                plural="" if len(deleted) == 1 else "s",
                category=category,
                channel=ctx.message.channel.mention
            )
        
    except Exception as ex:
        plugin.bot.loop.create_task(finishCleaning(plugin, ctx.channel.id))
        await ctx.send(plugin.i18next.t(ctx.guild, "clean_fail", _emote="NO", exc=ex))
    
    plugin.bot.loop.create_task(finishCleaning(plugin, ctx.channel.id))