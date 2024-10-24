import discord
from discord import app_commands

class MoveChannelCommand(app_commands.Command):
    def __init__(self, move_channel_func, monitored_category_id):
        super().__init__(
            name="move_channel",
            description="Переместить текущий канал в целевую категорию",
            callback=self.move_channel_callback
        )
        self.move_channel_func = move_channel_func
        self.monitored_category_id = monitored_category_id

    async def move_channel_callback(self, interaction: discord.Interaction):
        channel = interaction.channel
        if channel.category_id == self.monitored_category_id:
            await self.move_channel_func(channel)
            await interaction.response.send_message(f"Канал {channel.name} был перемещен в целевую категорию.", ephemeral=True)
        else:
            await interaction.response.send_message("Этот канал нельзя переместить, так как он не находится в отслеживаемой категории.", ephemeral=True)

def setup(bot, move_channel_func, monitored_category_id):
    bot.tree.add_command(MoveChannelCommand(move_channel_func, monitored_category_id))