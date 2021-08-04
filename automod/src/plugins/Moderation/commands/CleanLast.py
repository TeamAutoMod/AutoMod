import datetime
import time

from ..sub.CleanMessages import cleanMessages



async def run(plugin, ctx, duration, excess):
    if duration.unit is None:
        duration.unit = excess

    after = datetime.datetime.utcfromtimestamp(time.time() - duration.to_seconds(ctx))
    await cleanMessages(
        plugin, 
        ctx, 
        "Last", 
        500, 
        lambda m: True,
        after=after
    )