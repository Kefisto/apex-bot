import discord
from discord import app_commands

def has_required_role():
    async def predicate(interaction: discord.Interaction):
        required_role_id = 948978940096159744
        required_role = interaction.guild.get_role(required_role_id)
        if required_role is None:
            await interaction.response.send_message("Требуемая роль для использования команды не найдена.", ephemeral=True)
            return False
        if required_role not in interaction.user.roles:
            await interaction.response.send_message("У вас нет прав для использования этой команды.", ephemeral=True)
            return False
        return True
    return app_commands.check(predicate)

class MoveChannelCommand(app_commands.Command):
    def __init__(self, move_channel_func, monitored_category_id):
        super().__init__(
            name="move_channel",
            description="Переместить текущий канал в выбранную категорию",
            callback=self.move_channel_callback
        )
        self.move_channel_func = move_channel_func
        self.monitored_category_id = monitored_category_id

    @has_required_role()
    async def move_channel_callback(self, interaction: discord.Interaction, category: app_commands.Choice[int]):
        channel = interaction.channel
        if channel.category_id == self.monitored_category_id:
            await self.move_channel_func(channel, category.value)
            await interaction.response.send_message(f"Канал {channel.name} был перемещен в категорию {category.name}.", ephemeral=True)
        else:
            await interaction.response.send_message("Этот канал нельзя переместить, так как он не находится в отслеживаемой категории.", ephemeral=True)

def setup(bot, move_channel_func, monitored_category_id):
    move_command = MoveChannelCommand(move_channel_func, monitored_category_id)
    move_command.add_check(has_required_role())

    @move_command.autocomplete('category')
    async def category_autocomplete(interaction: discord.Interaction, current: str):
        choices = [
            app_commands.Choice(name="Обращение в обработке", value=1253302501323702285),
            app_commands.Choice(name="Ожидание ответа", value=909692673957453824),
            app_commands.Choice(name="Ожидание закрытия", value=932712057546080316)
        ]
        return choices

    bot.tree.add_command(move_command)
