import discord
from discord.ext import commands



class NotCachedError(commands.CheckFailure):
    pass



class PostParseError(commands.BadArgument):
    def __init__(self, type, error):
        super().__init__(None)
        self.type = type
        self.error = error


arg_ex = {
    "user": "User mention (@User) or User ID (814511071942934598)",
    "reason": "Reason for the action (optional)",

    "restriction": "What to restrict (embed, emoji, tag)",
    "channel": "Channel mention (#channel) or Channel ID (874097242598961152)",

    "plugin": "Plugin to load/unload",
    "warn": "The amount of warns this punishment is for",

    "guild_id": "A server ID (697814384197632050)",
    "users": "A list of User mentions (@User) or User IDs (697487580522086431) seperated by commas",

    "warns": "Warns to give (between 1 and 100)",
    "role_or_channel": "Role mention (@role), Channel mention (#channel), Role ID (874105666221010954) or Channel ID (874097242598961152)",

    "text": "A text that can include spaces",
    "prefix": "A new prefix",

    "action": "The action to take (ban, kick, mute or None)",
    "time": "A time/duration, for example 10m or 24h",

    "query": "Query to search by (command or subcommand name)",

    "join": "Joined during this time, for example 10m or 24h",
    "age": "Account created during this time, for example 10m or 24h",

    "chars": "List of characters",
    "state": "State of the feature, either on or off",

    "case": "A case by its ID (1)",
    "amount": "Amount of messages",

    "length": "A duration, for example 10m or 24h",
    "cmd": "Some Python code",

    "trigger": "The name of the tag",
    "reply": "The content of the tag (can include spaces)",

    "mentions": "The amount of mentions allowed per message",
    "lines": "The amount of line breaks allowed per message",

    "name": "Name of the filter, has to be a single word",
    "words": "Words in the filter, seperated by commas (word1, word 2, word 3)"
}