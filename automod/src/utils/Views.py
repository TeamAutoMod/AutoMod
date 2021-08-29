import discord
from discord.ui import Button, View


class Confirm(Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.green, label="Confirm")
    
    async def callback(self, interaction):
        try:
            await self.view.confirm_callback(interaction)
        except discord.NotFound:
            pass
    


class Cancel(Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.red, label="Cancel")
    
    async def callback(self, interaction):
        await self.view.cancel_callback(interaction)   



class ConfirmView(View):
    def __init__(self, guild_id, on_confirm, on_cancel, on_timeout, check, timeout=30):
        super().__init__(timeout=timeout)
        self.add_item(Confirm())
        self.add_item(Cancel())

        self.guild_id = guild_id

        self.on_confirm = on_confirm
        self.on_cancel = on_cancel
        self.timeout_callback = on_timeout
        self.check = check

    async def on_timeout(self):
        await self.timeout_callback()
    
    async def confirm_callback(self, interaction):
        if await self.exec_check(interaction):
            await self.on_confirm(interaction)
            self.stop()

    async def cancel_callback(self, interaction):
        if await self.exec_check(interaction):
            await self.on_cancel(interaction)
            self.stop()

    async def exec_check(self, interaction):
        if not self.check:
            return True
        if self.check(interaction):
            return True
        await self.refuse(interaction)
        return False

    async def refuse(self, interaction):
        interaction.response.send_message("Invalid interactor", ephermal=True)



class Link(Button):
    def __init__(self, _url, _label, *args, **kwargs):
        super().__init__(*args, style=discord.ButtonStyle.link, url=_url, label=_label, **kwargs)



class LinkView(View):
    def __init__(self, _guild, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_item(Link(_url=f"https://localhost:3000/guilds/{_guild.id}", _label="View dashboard"))


class AboutView(View):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_item(Link(_url="https://discord.gg/S9BEBux", _label="Support"))
        self.add_item(Link(_url="https://top.gg/bot/697487580522086431/vote", _label="Vote"))