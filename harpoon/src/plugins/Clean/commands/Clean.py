import discord
from discord.ext import commands

import shlex
import traceback
import logging

from ..Types import Arguments
from ....utils.RegEx import getPattern
from ..functions.GetBeforeAfter import getBeforeAfter
from ..functions.RunClean import runClean



log = logging.getLogger(__name__)


async def run(plugin, ctx, amount, args):
    try:
        amount = int(amount)
        if amount < 1 or amount > 200:
            return await ctx.send(plugin.t(ctx.guild, "invalid_amount", _emote="WARN"))

        if args is None:
            await runClean(plugin, ctx, amount)
            return 

        p = Arguments(add_help=False, allow_abbrev=False)
        p.add_argument("-user", nargs="+")


        p.add_argument("-contains", nargs="+")
        p.add_argument("-starts", nargs="+")
        p.add_argument("-ends", nargs="+")

        p.add_argument("-or", action="store_true", dest="_or")
        p.add_argument("-not", action="store_true", dest="_not")

        p.add_argument("-emojis", action="store_true")

        p.add_argument("-bots", action="store_const", const=lambda m: m.author.bot)
        p.add_argument("-embeds", action="store_const", const=lambda m: len(m.embeds))
        p.add_argument("-files", action="store_const", const=lambda m: len(m.attachments))
        p.add_argument("-reactions", action="store_const", const=lambda m: len(m.reactions))

        p.add_argument("-after", type=int)
        p.add_argument("-before", type=int)

        try:
            args = p.parse_args(shlex.split(args))
        except Exception as ex:
            return await ctx.send(f"{plugin.emotes.get('WARN')} {ex}")
        
        pr = []
        if args.bots:
            pr.append(args.bots)
        
        if args.embeds:
            pr.append(args.embeds)

        if args.files:
            pr.append(args.files)

        if args.reactions:
            pr.append(args.reactions)

        if args.emojis:
            custom_emote = getPattern(r"<:(\w+):(\d+)>")
            pr.append(lambda m: custom_emote.search(m.content))

        if args.user:
            targets = []
            converter = commands.MemberConverter()
            for t in args.user:
                try:
                    target = await converter.convert(ctx, t)
                    targets.append(target)
                except Exception as ex:
                    return await ctx.send(str(ex))
                
            pr.append(lambda m: m.author in targets)

        if args.contains:
            pr.append(lambda m: any(s in m.content for s in args.contains))
        
        if args.starts:
            pr.append(lambda m: any(m.content.startswith(s) for s in args.starts))

        if args.ends:
            pr.append(lambda m: any(m.content.endswith(s) for s in args.ends))
        
        o = all if not args._or else any
        def check(m):
            r = o(p(m) for p in pr)
            if args._not:
                return not r
            return r
        
        amount = max(0, min(300, amount))

        before, after = getBeforeAfter(ctx, args.before, args.after)
        await runClean(plugin, ctx, amount, check=check, before=before, after=after)
    except Exception:
        ex = traceback.format_exc()
        log.error(f"Error in command clean - {ex}")