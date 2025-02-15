import discord
from discord import Option
from discord.ext import commands
from attachment_parsing import parse_message_attachments


class Misc(commands.Cog, name='Miscellaneous'):
    def __init__(self, bot):
        self.bot = bot


    @discord.slash_command(name='use-last-spoiler-log', description='Sets the current spoiler log to be the last one sent in this channel.')
    async def use_last_spoiler_log(self, 
        ctx : discord.ApplicationContext, 
        limit : Option(int, description='The number of messages to search through.', default=100),
        include_attachment_info : Option(str, description='Whether to include the filename of the attachment and the date and time it was sent.', choices=['yes', 'no'], default='yes')
    ):
        response = f"I couldn't find an attachment to any of the last {limit} messages that looked like a spoiler log file to me. 🤔 " + \
            'Perhaps try widening the extent of my search by setting a larger `limit`.'

        channel_history = await ctx.channel.history(limit=limit)

        for message in channel_history:
            parse_result = await parse_message_attachments(message)

            if parse_result:
                spoiler_log, attachment_filename, message_datetime = parse_result

                if include_attachment_info == 'yes':
                    response = f'Got it! Log file `{attachment_filename}` ' + \
                        f"(from {message_datetime.strftime('%-d %B %Y')} " + \
                        f"at {message_datetime.strftime('%-I:%M %p')}) added and chopped. 🪓"
                else:
                    response = 'Got it! Log file added and chopped. 🪓'

                self.bot.spoiler_log = spoiler_log
                break

        await ctx.respond(response)


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
