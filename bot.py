import discord
import os
from dotenv import load_dotenv
from attachment_parsing import parse_message_attachments


load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

INTENTS = discord.Intents.default()
INTENTS.message_content = True

bot = discord.Bot(intents=INTENTS)


@bot.event
async def on_ready():
    print(f'{bot.user.name} is ready to chop some logs!')


@bot.event
async def on_message(message):
    if message.author != bot.user:
        parse_result = await parse_message_attachments(message)

        if parse_result:
            bot.spoiler_log = parse_result[0]
            await message.channel.send(f'Got it! Log file added and chopped. 🪓 Here is your seed: `{bot.spoiler_log.seed}`. 🌰')


bot.load_extension('cogs.item_placements')
bot.load_extension('cogs.boss_placements')
bot.load_extension('cogs.misc')


bot.run(TOKEN)
