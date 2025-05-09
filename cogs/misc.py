import discord
import platform
from discord import Option
from discord.ext import commands
from attachment_parsing import parse_message_attachments


DATE_FORMATTING_STRING = r'%#d %B %Y' if platform.system() == 'Windows' else r'%-d %B %Y'

TIME_FORMATTING_STRING = r'%#I:%M %p' if platform.system() == 'Windows' else r'%-I:%M %p'


class Misc(commands.Cog, name='Miscellaneous'):
    def __init__(self, bot):
        self.bot = bot
    
    @discord.slash_command(name='show-seed', description='Displays the seed associated with the current log file.')
    async def show_seed(self, ctx : discord.ApplicationContext):
        try:
            response = f'Here is the seed of the current spoiler log file: `{self.bot.spoiler_log.seed}` 🌰.'
        except AttributeError:
            response = "Looks like you haven't uploaded a spoiler log file yet. 🤓 Try uploading one and then trying your command again."

        ctx.respond(response)

    @discord.slash_command(name='use-last-spoiler-log', description='Sets the current spoiler log to be the last one sent in this channel.')
    async def use_last_spoiler_log(self, 
        ctx : discord.ApplicationContext, 
        limit : Option(int, description='The number of messages to search through.', default=100),
        include_attachment_info : Option(str, 
            description='Whether to include the filename of the attachment and the date and time it was sent.', 
            choices=['yes', 'no'], 
            default='yes'
        )
    ):
        await ctx.response.defer()

        response = f"I couldn't find an attachment to any of the last {limit} messages that looked like a spoiler log file to me. 🤔 " + \
            'Perhaps try widening the extent of my search by setting a larger `limit`.'

        async for message in ctx.channel.history(limit=limit):
            parse_result = await parse_message_attachments(message)

            if parse_result:
                spoiler_log, attachment_filename, message_datetime = parse_result

                if include_attachment_info == 'yes':
                    response = f'Got it! Log file `{attachment_filename}` ' + \
                        f'with seed `{self.bot.spoiler_log.seed}` ' + \
                        f'(from {message_datetime.strftime(DATE_FORMATTING_STRING)} ' + \
                        f'at {message_datetime.strftime(TIME_FORMATTING_STRING)}) added and chopped. 🪓'
                else:
                    response = f'Got it! Log file added and chopped. 🪓 Here is your seed: `{self.bot.spoiler_log.seed}`. 🌰'

                self.bot.spoiler_log = spoiler_log
                break

        await ctx.followup.send(response)

    @discord.slash_command(name='help', description='Displays this help message.')
    async def help(self, ctx : discord.ApplicationContext):
        response = '```'

        for cog_name, cog in self.bot.cogs.items():
            response += f'{cog_name}:\n'

            for command in cog.walk_commands():
                response += f'\t{command.name}\t{command.description}\n'

        response += '```'
        await ctx.respond(response)


def setup(bot):
    bot.add_cog(Misc(bot))
