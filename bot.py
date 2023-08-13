import asyncio
import discord
import os
from discord.ext.commands import Bot
from dotenv import load_dotenv
from spoiler_log import LogParseException, SpoilerLog


load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

INTENTS = discord.Intents.default()
INTENTS.message_content = True

bot = Bot(command_prefix='!', intents=INTENTS)
bot.spoiler_log = SpoilerLog()


@bot.event
async def on_ready():
    print(f'{bot.user.name} is ready to chop some logs!')


@bot.event
async def on_message(message):
    if message.author != bot.user:
        for attachment in message.attachments:
            body = await attachment.read()

            try:
                bot.spoiler_log.add_log_lines(body.decode().split('\r\n'))
            except (LogParseException, UnicodeDecodeError):
                continue

            await message.channel.send('Got it! Log file added and chopped 🪓')
            break

        await bot.process_commands(message)


async def main():
    async with bot:
        await bot.load_extension('cogs.item_placements')
        await bot.load_extension('cogs.boss_placements')
        await bot.load_extension('cogs.options')

        await bot.start(TOKEN)


if __name__ == '__main__':
    asyncio.run(main())
