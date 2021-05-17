import discord

import asyncio

from ...Types import Embed



o1 = "- Warn"
o2 = "- Ban"
o3 = "- Kick"
o4 = "- Mute (1 Minute)"
o5 = "- Mute (10 Minutes)"
o6 = "- Mute (30 Minutes)"
o7 = "- Mute (1 Hour)"
o8 = "- Just delete the message"


syntax = {
    o1: "warn",
    o2: "ban",
    o3: "kick",
    o4: "mute_60",
    o5: "mute_600",
    o6: "mute_1800",
    o7: "mute_3600",
    o8: "delete"
}


num_emotes = {
    1: "1️⃣",
    2: "2️⃣",
    3: "3️⃣",
    4: "4️⃣",
    5: "5️⃣",
    6: "6️⃣",
    7: "7️⃣",
    8: "8️⃣"
}



def get_options(*options) -> str:
    options = options
    out = list()
    for i, inp in enumerate(options):
        out.append(f"{num_emotes[i+1]} {inp}")
    
    return "\n".join(out)


def get_emotes(opt_amount):
    out = list()
    for i in range(0, opt_amount):
        out.append(num_emotes[i+1])

    return out


def get_punishment_for_reaction(*options):
    options = options
    out = dict()
    for i, inp in enumerate(options):
        out[num_emotes[i+1]] = syntax[inp]

    return out


options = {
    "invite_censor": {
        "pretty_name": "Invite Censorship",
        "options": get_options(o1, o4, o5, o6, o7, o8),
        "emotes": get_emotes(6),
        "reaction_punishments": get_punishment_for_reaction(o1, o4, o5, o6, o7, o8)
    },
    "word_censor": {
        "pretty_name": "Word Censorship",
        "options": get_options(o1, o4, o5, o6, o7, o8),
        "emotes": get_emotes(6),
        "reaction_punishments": get_punishment_for_reaction(o1, o4, o5, o6, o7, o8)
    },
    "file_censor": {
        "pretty_name": "File Censorship",
        "options": get_options(o1, o4, o5, o6, o7, o8),
        "emotes": get_emotes(6),
        "reaction_punishments": get_punishment_for_reaction(o1, o4, o5, o6, o7, o8)
    },
    "zalgo_censor": {
        "pretty_name": "Zalgo Censorship",
        "options": get_options(o1, o4, o5, o6, o7, o8),
        "emotes": get_emotes(6),
        "reaction_punishments": get_punishment_for_reaction(o1, o4, o5, o6, o7, o8)
    },
    "caps_censor": {
        "pretty_name": "Caps Censorship",
        "options": get_options(o1, o4, o5, o6, o7, o8),
        "emotes": get_emotes(6),
        "reaction_punishments": get_punishment_for_reaction(o1, o4, o5, o6, o7, o8)
    },
    "spam_detection": {
        "pretty_name": "Spam Detection",
        "options": get_options(o1, o2, o3, o4, o5, o6, o7),
        "emotes": get_emotes(7),
        "reaction_punishments": get_punishment_for_reaction(o1, o2, o3, o4, o5, o6, o7)
    },
    "mention_spam": {
        "pretty_name": "Mention Spam",
        "options": get_options(o1, o4, o5, o6, o7, o8),
        "emotes": get_emotes(6),
        "reaction_punishments": get_punishment_for_reaction(o1, o4, o5, o6, o7, o8)
    },
    "max_warns": {
        "pretty_name": "Max Warns",
        "options": get_options(o2, o3, o4, o5, o6, o7),
        "emotes": get_emotes(6),
        "reaction_punishments": get_punishment_for_reaction(o2, o3, o4, o5, o6, o7)
    },
}


async def setPunishment(plugin, ctx, _type):
    t = options[_type]

    e = Embed(
        title="Punishment Config", 
        description="Set a punishment for ``{}``".format(t["pretty_name"])
    )
    e.add_field(
        name="Pick an option by reacting",
        value=t["options"]
    )

    msg = await ctx.send(embed=e)
    for emoji in t["emotes"]:
        await msg.add_reaction(emoji)

    def check(reaction, user):
        return user == ctx.author and str(reaction.emoji) in t["emotes"]

    while True:
        try:
            reaction, user = await plugin.bot.wait_for("reaction_add", timeout=30, check=check)

            new_punishment = t["reaction_punishments"][str(reaction)]

            current = plugin.db.configs.get(ctx.guild.id, "actions")
            current[_type] = new_punishment
            current = plugin.db.configs.update(ctx.guild.id, "actions", current)

            try:
                await msg.delete()
            except discord.NotFound:
                pass
            finally:
                await ctx.send(plugin.translator.translate(ctx.guild, "updated_punishment", _emote="YES", _type=t["pretty_name"]))
                break

        except asyncio.TimeoutError:
            try:
                await msg.delete()
            except discord.NotFound:
                pass
            finally:
                await ctx.send(plugin.translator.translate(ctx.guild, "aborting"))
                break
