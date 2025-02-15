import re
import copy
import discord
from pathlib import Path
from discord import Option
from discord.ext import commands
from response_chunking import send_chunked_response


def get_items(ctx : discord.AutocompleteContext):
    return [item for item in ctx.bot.spoiler_log.item_dict.keys() if item.lower().startswith(ctx.value.lower())]


def get_guild_item_list_names(ctx : discord.AutocompleteContext):
    path_stems = {path.stem for path in Path(f'Item Lists\\{ctx.interaction.guild_id}').glob('*.txt')}

    return sorted([
        path_stem for path_stem in path_stems
    if path_stem.lower().startswith(ctx.value.lower())])


def get_all_item_list_names(ctx : discord.AutocompleteContext):
    path_stems = {
        path.stem for path in Path(f'Item Lists\\{ctx.interaction.guild_id}').glob('*.txt')
    } | {
        path.stem for path in Path('Item Lists').glob('*.txt')
    }

    return sorted([
        path_stem for path_stem in path_stems
    if path_stem.lower().startswith(ctx.value.lower())])


class ItemPlacements(commands.Cog, name='Item Placements'):
    def __init__(self, bot):
        self.bot = bot

    @discord.slash_command(name='show-item', description='Reveals the location(s) of a specified item.')
    async def show_item(self,
        ctx: discord.ApplicationContext,
        item_name : Option(str, description='The name of the item.', autocomplete=get_items),
        spoiler : Option(str, description='Whether to mark the result as a spoiler.', choices=['yes', 'no'], default='no')
    ):
        try:
            item_location_set = copy.deepcopy(self.bot.spoiler_log.single_item_locations(item_name))

            if len(item_location_set) > 1:
                response = f'{item_name} is in:'

                for item_location, location_description, _ in item_location_set:
                    response += f'\n* {item_location}, {location_description[0].lower()}{location_description[1:]}.'
            else:
                item_location, location_description, _ = item_location_set.pop()
                response = f'{item_name} is in {item_location}, {location_description[0].lower()}{location_description[1:]}.'
        except KeyError:
            if item_name == 'Rold Medallion':
                response = "Sorry, I can't find the Rold Medallion. " + \
                    "Are you sure it would have been placed in the open world given your randomization settings? 🤔"
            else:
                response = f'I don\'t know about "{item_name}". 😔 You might have mistyped it.'
        except AttributeError:
            response = "Looks like you haven't uploaded a spoiler log file yet. 🤓 Try uploading one and then trying your command again."

        await send_chunked_response(ctx, response, add_spoiler_tags=(spoiler == 'yes'))

    @discord.slash_command(name='show-item-list', description='Reveals the location(s) of items in a specified list.')
    async def show_items_in_list(self, 
        ctx : discord.ApplicationContext,
        list_name : Option(str, description='The name of the item list.', autocomplete=get_all_item_list_names),
        spoiler : Option(str, description='Whether to mark the result as a spoiler.', choices=['yes', 'no'], default='no')
    ):
        try:
            with open(f'Item Lists\\{ctx.guild_id}\\{list_name}.txt') as f:
                item_list_text = f.read()
        except FileNotFoundError:
            with open(f'Item Lists\\{list_name}.txt') as f:
                item_list_text = f.read()

        item_location_dict = copy.deepcopy(self.bot.spoiler_log.item_list_locations(
            re.split(r'\n+', item_list_text)
        ))

        response = ''

        for match in re.finditer(r'(.+)\n?(\n*)', item_list_text):
            try:
                item_location_set = item_location_dict[(item_name := match.group(1))]

                if len(item_location_set) > 1:
                    response += f'* {item_name}:\n'

                    for item_location, location_description, old_item in item_location_set:
                        response += f'\n  * {item_location}, {location_description[0].lower()}{location_description[1:]}'

                        if item_name == old_item:
                            response += ' (replacing itself).'
                        elif old_item in item_location_dict.keys():
                            response += f' (replacing {old_item}).'
                        else:
                            response += '.'

                        response += '\n'
                else:
                    item_location, location_description, old_item = item_location_set.pop()
                    response += f'* {item_name} is in {item_location}, {location_description[0].lower()}{location_description[1:]}'

                    if item_name == old_item:
                        response += ' (replacing itself).'
                    elif old_item in item_location_dict.keys():
                        response += f' (replacing {old_item}).'
                    else:
                        response += '.'

                    response += '\n'

                response += match.group(2)
            except KeyError:
                pass
            except AttributeError:
                response = "Looks like you haven't uploaded a spoiler log file yet. 🤓 Try uploading one and then trying your command again."
                break

        await send_chunked_response(ctx, response, add_spoiler_tags=(spoiler == 'yes'))

    @discord.slash_command(name='create-item-list', description='Creates a custom item list from attachment or message content.')
    async def create_item_list(self,
        ctx : discord.ApplicationContext,
        list_name : str
    ):
        list_file_path = f'Item Lists\\{ctx.interaction.guild_id}\\{list_name}.txt'

        if Path(list_file_path).exists():
            response = f'The custom item list `{list_name}` already exists. Use `/replace-item-list` to replace its contents.'
        else:
            if ctx.message.attachments:
                list_body = await ctx.message.attachments[0].read()

                with open(list_file_path, 'wb') as f:
                    f.write(list_body)
            else:
                with open(list_file_path, 'w') as f:
                    f.write(ctx.message.content)

            response = f'The custom item list `{list_name}` has been created. 👍'

        ctx.respond(response)

    @discord.slash_command(name='replace-item-list', description='Replaces the contents of an existing custom item list.')
    async def replace_item_list(self,
        ctx : discord.ApplicationContext,
        list_name : Option(str, description='The name of the item list.', autocomplete=get_guild_item_list_names)
    ):
        list_file_path = f'Item Lists\\{ctx.interaction.guild_id}\\{list_name}.txt'

        if ctx.message.attachments:
            list_body = await ctx.message.attachments[0].read()

            with open(list_file_path, 'wb') as f:
                f.write(list_body)
        else:
            with open(list_file_path, 'w') as f:
                f.write(ctx.message.content)

        ctx.respond(f'The contents of the custom item list `{list_name}` have been replaced. 👍')

    @discord.slash_command(name='rename-item-list', description='Renames a custom item list.')
    async def rename_item_list(self,
        ctx : discord.ApplicationContext,
        list_name : Option(str, description='The name of the item list.', autocomplete=get_guild_item_list_names),
        new_name : str
    ):
        Path(f'Item Lists\\{ctx.interaction.guild_id}\\{list_name}.txt').rename(
            Path(f'Item Lists\\{ctx.interaction.guild_id}\\{new_name}.txt')
        )

        ctx.respond(f'The custom item list `{list_name}` has been renamed `{new_name}`.')

    @discord.slash_command(name='delete-item-list', description='Deletes a custom item list.')
    async def delete_item_list(self,
        ctx : discord.ApplicationContext,
        list_name : Option(str, description='The name of the item list.', autocomplete=get_guild_item_list_names)
    ):
        Path(f'Item Lists\\{ctx.interaction.guild_id}\\{list_name}.txt').unlink()
        ctx.respond(f'The custom item list `{list_name}` has been deleted. ❌')


def setup(bot):
    bot.add_cog(ItemPlacements(bot))
