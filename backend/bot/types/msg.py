# type: ignore

import discord
from discord.ext import commands

import re
from typing import Union, Tuple, Optional



class Message(commands.Converter):
    async def convert(self, ctx: discord.Interaction, argument: str) -> Union[discord.Message, Exception]:
        guild_id, message_id, channel_id = PartialMessageConverter._get_id_matches(ctx, argument)

        message = ctx._client._connection._get_message(message_id)
        if message:
            return message

        channel = PartialMessageConverter._resolve_channel(ctx, guild_id, channel_id)
        if not channel or not isinstance(channel, discord.abc.Messageable):
            raise commands.ChannelNotFound(channel_id)
            
        try:
            return await channel.fetch_message(message_id)
        except discord.NotFound:
            raise commands.MessageNotFound(argument)
        except discord.Forbidden:
            raise commands.ChannelNotReadable(channel)


class PartialMessageConverter(commands.Converter):
    @staticmethod
    def _get_id_matches(ctx: discord.Interaction, argument: str) -> Tuple[Optional[int], int, int]:
        id_regex = re.compile(r'(?:(?P<channel_id>[0-9]{15,20})-)?(?P<message_id>[0-9]{15,20})$')
        link_regex = re.compile(
            r'https?://(?:(ptb|canary|www)\.)?discord(?:app)?\.com/channels/'
            r'(?P<guild_id>[0-9]{15,20}|@me)'
            r'/(?P<channel_id>[0-9]{15,20})/(?P<message_id>[0-9]{15,20})/?$'
        )

        match = id_regex.match(argument) or link_regex.match(argument)
        if not match:
            raise commands.MessageNotFound(argument)

        data = match.groupdict()
        channel_id = discord.utils._get_as_snowflake(data, 'channel_id') or ctx.channel.id
        message_id = int(data['message_id'])
        guild_id = data.get('guild_id')

        if guild_id is None:
            guild_id = ctx.guild and ctx.guild.id
        elif guild_id == '@me':
            guild_id = None
        else:
            guild_id = int(guild_id)

        return guild_id, message_id, channel_id


    @staticmethod
    def _resolve_channel(ctx: discord.Interaction, guild_id: Optional[int], channel_id: Optional[int]) -> Optional[Union[discord.TextChannel, discord.Thread]]:
        if channel_id is None:
            return ctx.channel

        if guild_id is not None:
            guild = ctx._client.get_guild(guild_id)
            if guild is None:
                return None
            return guild._resolve_channel(channel_id)

        return ctx._client.get_channel(channel_id)


    async def convert(self, ctx: discord.Interaction, argument: str) -> discord.PartialMessage:
        guild_id, message_id, channel_id = self._get_id_matches(ctx, argument)
        channel = self._resolve_channel(ctx, guild_id, channel_id)

        if not channel or not isinstance(channel, discord.abc.Messageable):
            raise commands.ChannelNotFound(channel_id)

        return discord.PartialMessage(channel=channel, id=message_id)