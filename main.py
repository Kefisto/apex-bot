import discord
from discord.ext import commands
import re
from fuzzywuzzy import fuzz

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

MONITORED_CATEGORY_ID = 1253302501323702285  # ID категории, которую нужно мониторить
TARGET_CATEGORY_ID = 932712057546080316  # ID категории, куда нужно перемещать каналы
TRIGGER_MESSAGE = "запросил разрешение на закрытие этого обращения"
SIMILARITY_THRESHOLD = 80  # Порог схожести для нечеткого сравнения (0-100)

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')

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
        
        if content is None or check_trigger(content):
            print("Обнаружено триггерное сообщение или пустое содержимое!")
            await move_channel(channel)
        else:
            print("Триггерное сообщение не обнаружено.")

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
        return True
    
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

async def move_channel(channel):
    target_category = bot.get_channel(TARGET_CATEGORY_ID)
    if target_category:
        await channel.edit(category=target_category)
        await channel.send(f"Канал перемещен в категорию {target_category.name}")
        print(f"Канал {channel.name} перемещен в категорию {target_category.name}")
    else:
        print(f"Ошибка: категория с ID {TARGET_CATEGORY_ID} не найдена")

bot.run('MTI5OTA0NDg0Mzk2MzU0NzY0OQ.G3NY2p.6RZIRIXp8ONf9CQtCgI8fyQlEWPc2dKMcLQAzU')