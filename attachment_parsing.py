import discord
from spoiler_log import SpoilerLog, LogParseException


async def parse_message_attachments(message : discord.Message):
    for attachment in message.attachments:
        spoiler_log = None
        body = await attachment.read()

        try:
            spoiler_log = SpoilerLog(body.decode().split('\r\n'))         
        except (LogParseException, UnicodeDecodeError):
            continue

        if spoiler_log:
            return (spoiler_log, attachment.filename, message.created_at)
