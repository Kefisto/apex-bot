import discord
from discord.ext import commands
import re
from fuzzywuzzy import fuzz
import custom_commands
import buyer_command

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

MONITORED_CATEGORY_ID = 1253302501323702285
TARGET_CATEGORY_ID = 932712057546080316
TRIGGER_MESSAGE = "запросил разрешение на закрытие этого обращения"
SIMILARITY_THRESHOLD = 80

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    custom_commands.setup(bot, move_channel, MONITORED_CATEGORY_ID)
    buyer_command.setup(bot)
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(f"Failed to sync commands: {e}")



#хуйня

@bot.event
async def on_message(message):
    await process_message(message)
    await bot.process_commands(message)

@bot.event
async def on_interaction(interaction):
    if interaction.type == discord.InteractionType.application_command:
        await process_message(interaction)
async def process_message(message_or_interaction):
    if isinstance(message_or_interaction, discord.Interaction):
        channel = message_or_interaction.channel
        content = get_interaction_content(message_or_interaction)
    else:
        channel = message_or_interaction.channel
        content = get_message_content(message_or_interaction)

    if channel.category_id == MONITORED_CATEGORY_ID:
        print(f"Новое сообщение/взаимодействие в канале {channel.name}:")
        print(f"Содержимое: {content}")

        if content is not None and content != '' and check_trigger(content):
            print("Обнаружено триггерное сообщение!")
            await move_channel(channel)
        elif content is not None and content != '' and content.startswith('/closerequest'):
            print("Обнаружена команда /closerequest!")
            await move_channel(channel, str(TARGET_CATEGORY_ID))
        elif content is not None and content != '' and '883083155953836072' in content:  # Add the command ID here
            print("Обнаружена команда с указанным идентификатором!")
            await move_channel(channel, TARGET_CATEGORY_ID)  # Add the target category ID here
        else:
            if content is None or content == '':
                print("Пустое содержимое. Канал не будет перемещен.")
            else:
                print("Триггерное сообщение не обнаружено.")



#говнокод



def get_message_content(message):
    if message.content:
        return message.content.lower()
    elif message.embeds:
        embed = message.embeds[0]
        content = ""
        if embed.title:
            content += embed.title + " "
        if embed.description:
            content += embed.description + " "
        for field in embed.fields:
            content += field.name + " " + field.value + " "
        return content.lower() if content else None
    return None

def get_interaction_content(interaction):
    if interaction.data and 'options' in interaction.data:
        content = ' '.join([str(option['value']) for option in interaction.data['options']])
        return content.lower() if content else None
    return None
def check_trigger(content):
    if content is None:
        return False

    # Метод 1: Частичное совпадение
    if "запросил разрешение" in content and "закрытие" in content:
        print("Сработал метод 1: Частичное совпадение")
        return True

    # Метод 2: Нечеткое сравнение
    similarity = fuzz.partial_ratio(TRIGGER_MESSAGE, content)
    if similarity >= SIMILARITY_THRESHOLD:
        print(f"Сработал метод 2: Нечеткое сравнение (схожесть: {similarity}%)")
        return True

    # Метод 3: Регулярное выражение
    if re.search(r'запросил.*разрешение.*закрытие.*обращения', content):
        print("Сработал метод 3: Регулярное выражение")
        return True

    return False


async def move_channel(channel, target_category_id: str):
    target_category = bot.get_channel(int(target_category_id))
    if target_category:
        await channel.edit(category=target_category)
        await channel.send(f"Канал перемещен в категорию {target_category.name}")
        print(f"Канал {channel.name} перемещен в категорию {target_category.name}")
    else:
        print(f"Ошибка: категория с ID {target_category_id} не найдена")


bot.run('')
