import discord
from discord import app_commands

REQUIRED_ROLE_ID = 948978940096159744

class MoveChannelCommand(app_commands.Command):
    @staticmethod
    def get_category_choices():
        return [
            app_commands.Choice(name="Обращение в обработке", value="1253302501323702285"),
            app_commands.Choice(name="Ожидание ответа", value="909692673957453824"),
            app_commands.Choice(name="Ожидание закрытия", value="932712057546080316")
        ]

    def __init__(self, move_channel_func, monitored_category_id):
        super().__init__(
            name="move_channel",
            description="Переместить текущий канал в выбранную категорию",
            callback=self.move_channel_callback
        )
        self.move_channel_func = move_channel_func
        self.monitored_category_id = monitored_category_id
        self.category_choices = self.get_category_choices()

    @app_commands.describe(category="Выберите категорию для перемещения канала")
    @app_commands.choices(category=get_category_choices())
    async def move_channel_callback(self, interaction: discord.Interaction, category: str):
        if not self.has_required_role(interaction):
            await interaction.response.send_message("У вас нет прав для использования этой команды.", ephemeral=True)
            return
        channel = interaction.channel
        if channel.category_id == self.monitored_category_id:
            category_id = int(category)
            await self.move_channel_func(channel, category_id)
            category_name = next((choice.name for choice in self.category_choices if choice.value == category), "Unknown")
            await interaction.response.send_message(f"Канал {channel.name} был перемещен в категорию {category_name}.", ephemeral=True)
        else:
            await interaction.response.send_message("Этот канал нельзя переместить, так как он не находится в отслеживаемой категории.", ephemeral=True)

    def has_required_role(self, interaction: discord.Interaction):
        required_role = interaction.guild.get_role(REQUIRED_ROLE_ID)
        if required_role is None:
            return False
        return required_role in interaction.user.roles

def setup(bot, move_channel_func, monitored_category_id):
    bot.tree.add_command(MoveChannelCommand(move_channel_func, monitored_category_id))
