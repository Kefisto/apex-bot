import disnake
from disnake.ext import commands
import asyncio

intents = disnake.Intents.default()
intents.messages = True
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

MONITORED_CATEGORY_ID = [1253302501323702285, 909692673957453824]
BOT_TOKEN = 'MTI5OTA0NDg0Mzk2MzU0NzY0OQ.G3NY2p.6RZIRIXp8ONf9CQtCgI8fyQlEWPc2dKMcLQAzU'

# ID категорий
PROCESSING_CATEGORY_ID = 1253302501323702285  # ID категории "обработка"
WAITING_CATEGORY_ID = 909692673957453824     # ID категории "ожидание"
CLOSING_CATEGORY_ID = 932712057546080316      # ID категории "закрытие"
@bot.event
async def on_ready():
    print(f'Бот {bot.user} запущен!')
@bot.event
async def on_ready():
    print(f'Бот {bot.user} запущен!')

@bot.event
async def on_message(message):
    if message.type == disnake.MessageType.application_command:
        await asyncio.sleep(1)
        message = await message.channel.fetch_message(message.id)
        if message.embeds:
            embed = message.embeds[0]
            if embed.title and "Запрос на закрытие" in embed.title:
                channel = message.channel
                if channel.category_id != CLOSING_CATEGORY_ID:
                    category = bot.get_channel(CLOSING_CATEGORY_ID)
                    if category:
                        await channel.edit(category=category)
                        await message.channel.send(f'Канал перемещён в категорию: {category.name}')
                    else:
                        await message.channel.send('Не удалось найти категорию для перемещения канала.')
                else:
                    await message.channel.send('Канал уже находится в нужной категории.')
    await bot.process_commands(message)

def has_required_role():
    async def predicate(interaction: disnake.ApplicationCommandInteraction):
        role_id = 894248720579842108
        role = interaction.guild.get_role(role_id)
        if role is None:
            await interaction.response.send_message("Роль не найдена.", ephemeral=True)
            return False
        if role not in interaction.user.roles:
            await interaction.response.send_message("У вас нет необходимой роли для использования этой команды.", ephemeral=True)
            return False
        return True
    return commands.check(predicate)

class MoveChannelCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="move", description="Переместить канал в выбранную категорию")
    async def move_channel(
        self, 
        interaction: disnake.ApplicationCommandInteraction,
        category: str = commands.Param(choices=["обработка", "ожидание", "закрытие"], description="Выберите категорию для перемещения")
    ):
        await interaction.response.defer(ephemeral=True)
        channel = interaction.channel
        if channel.category_id not in MONITORED_CATEGORY_ID:
            await interaction.followup.send("Этот канал нельзя переместить, так как он не находится в отслеживаемой категории.", ephemeral=True)
            return


        category_id = {
            "обработка": PROCESSING_CATEGORY_ID,
            "ожидание": WAITING_CATEGORY_ID,
            "закрытие": CLOSING_CATEGORY_ID
        }.get(category)

        if category_id:
            target_category = interaction.guild.get_channel(category_id)
            if target_category:
                await channel.edit(category=target_category)
                await interaction.followup.send(f"Канал перемещен в категорию: {target_category.name}", ephemeral=True)
            else:
                await interaction.followup.send("Не удалось найти выбранную категорию.", ephemeral=True)
        else:
            await interaction.followup.send("Некорректный выбор категории.", ephemeral=True)

class BuyerCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="buyer", description="Выдать роль покупателя")
    @commands.check(has_required_role())
    async def buyer_command(self, interaction: disnake.ApplicationCommandInteraction, user: disnake.Member = None):
        await interaction.response.defer(ephemeral=True)
        role_id = 894248720579842108
        role = interaction.guild.get_role(role_id)

        if role is None:
            await interaction.followup.send("Роль покупателя не найдена.", ephemeral=True)
            return

        target_user = user or interaction.user

        if role in target_user.roles:
            await interaction.followup.send(f"У {'вас' if target_user == interaction.user else target_user.mention} уже есть роль покупателя.", ephemeral=True)
        else:
            await target_user.add_roles(role)
            await interaction.followup.send(f"{'Вам' if target_user == interaction.user else target_user.mention} выдана роль покупателя!", ephemeral=True)

if __name__ == "__main__":
    bot.add_cog(MoveChannelCommand(bot))
    bot.add_cog(BuyerCommand(bot))
    bot.run(BOT_TOKEN)

