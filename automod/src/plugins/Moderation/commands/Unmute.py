from ..sub.UnmuteUser import unmuteUser
from ....utils import Permissions


async def run(plugin, ctx, user):
    await unmuteUser(plugin, ctx, user)