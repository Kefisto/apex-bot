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
class BuyerCommand(app_commands.Command):
    def __init__(self, bot):
        super().__init__(
            name="buyer",
            description="Выдать роль покупателя",
            callback=self.buyer_command
        )
        self.bot = bot

    @app_commands.describe(user="Пользователь, которому нужно выдать роль покупателя")
    @has_required_role()
    async def buyer_command(self, interaction: discord.Interaction, user: discord.Member = None):
        role_id = 894248720579842108
        role = interaction.guild.get_role(role_id)

        if role is None:
            await interaction.response.send_message("Роль покупателя не найдена.", ephemeral=True)
            return

        target_user = user or interaction.user

        if role in target_user.roles:
            await interaction.response.send_message(f"У {'вас' if target_user == interaction.user else target_user.mention} уже есть роль покупателя.", ephemeral=True)
        else:
            await target_user.add_roles(role)
            await interaction.response.send_message(f"{'Вам' if target_user == interaction.user else target_user.mention} выдана роль покупателя!", ephemeral=True)

def setup(bot):
    bot.tree.add_command(BuyerCommand(bot))

