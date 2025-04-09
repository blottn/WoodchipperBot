import re
import discord
import logging
from pathlib import Path
from discord import Option
from discord.ext import commands
from thefuzz import fuzz, process
from spoiler_log import BOSS_INFO_BY_NAME, BOSS_INFO_BY_ID
from response_chunking import send_chunked_response


logging.getLogger('thefuzz').setLevel(logging.ERROR)


def get_best_boss_name(text):
    choices = list(BOSS_INFO_BY_NAME.keys())

    for i, choice in enumerate(choices):
        if fuzz.partial_ratio('Radagon of the Golden Order', choice) >= 90:
            del choices[i]
            choices = [choice] + choices
            break

    if (best_match := process.extractOne(text, choices))[1] >= 90:
        return best_match[0]


def get_bosses_combine_phases(ctx : discord.AutocompleteContext):
    with_phases_split = {
        phase_name: combined_name
    for combined_name in BOSS_INFO_BY_NAME.keys() for phase_name in combined_name.split(' / ')}

    best_matches : list[tuple] = process.extract(ctx.value, with_phases_split.keys())

    return [
        with_phases_split[match]
    for match, score in sorted(best_matches, key=lambda t: t[1], reverse=True) if score >= 90]


def get_bosses_split_phases(ctx : discord.AutocompleteContext):
    best_matches : list[tuple] = process.extract(ctx.value, {info[0] for info in BOSS_INFO_BY_ID.values()})
    return [match for match, score in sorted(best_matches, key=lambda t: t[1], reverse=True) if score >= 90]


def get_guild_boss_list_names(ctx : discord.AutocompleteContext):
    path_stems = {path.stem for path in Path(f'Boss Lists/{ctx.interaction.guild_id}').glob('*.txt')}

    return sorted([
        path_stem for path_stem in path_stems
    if path_stem.lower().startswith(ctx.value.lower())])


def get_all_boss_list_names(ctx : discord.AutocompleteContext):
    path_stems = {
        path.stem for path in Path(f'Boss Lists/{ctx.interaction.guild_id}').glob('*.txt')
    } | {
        path.stem for path in Path('Boss Lists').glob('*.txt')
    }

    return sorted([
        path_stem for path_stem in path_stems
    if path_stem.lower().startswith(ctx.value.lower())])


class BossPlacements(commands.Cog, name='Boss Placements'):
    def __init__(self, bot):
        self.bot = bot

    @discord.slash_command(name='show-boss-replacement', description='Reveals which boss replaces a specified boss.')
    async def show_boss_replacement(self, 
        ctx : discord.ApplicationContext,
        boss_name : Option(str, description='The name of the original boss.', autocomplete=get_bosses_combine_phases),
        spoiler : Option(str, description='Whether to mark the result as a spoiler.', choices=['yes', 'no'], default='no')
    ):
        try:
            response = f"{boss_name} → {' / '.join(self.bot.spoiler_log.get_boss_replacement(boss_name))}"
        except KeyError:
            response = "I don't know about that boss. 😔 You might have mistyped it."
        except AttributeError:
            response = "Looks like you haven't uploaded a spoiler log file yet. 🤓 Try uploading one and then trying your command again."

        await send_chunked_response(ctx, response, add_spoiler_tags=(spoiler == 'yes'))

    @discord.slash_command(name='show-boss-location', description='Reveals the location of a specified boss.')
    async def show_boss_location(self,
        ctx : discord.ApplicationContext,
        boss_name : Option(str, description='The name of the boss.', autocomplete=get_bosses_split_phases),
        spoiler : Option(str, description='Whether to mark the result as a spoiler.', choices=['yes', 'no'], default='no')
    ):
        try:
            if (old_boss_info := self.bot.spoiler_log.locate_boss(boss_name)):
                response = '\n'.join([f'{info[0]} ({info[1]}) → {boss_name}' for info in old_boss_info])
            else:
                response = "I don't know about that boss. 😔 You might have mistyped it."
        except AttributeError:
            response = "Looks like you haven't uploaded a spoiler log file yet. 🤓 Try uploading one and then trying your command again."

        await send_chunked_response(ctx, response, add_spoiler_tags=(spoiler == 'yes'))

    @discord.slash_command(name='show-boss-list-replacements', description='Reveals which bosses replace those in a specified list.')
    async def show_boss_list_replacements(self,
        ctx : discord.ApplicationContext,
        list_name : Option(str, description='The name of the boss list.', autocomplete=get_all_boss_list_names),
        spoiler : Option(str, description='Whether to mark the result as a spoiler.', choices=['yes', 'no'], default='no')
    ):
        try:
            with open(f'Boss Lists/{ctx.guild_id}/{list_name}.txt') as f:
                boss_list_text = f.read()
        except FileNotFoundError:
            with open(f'Boss Lists/{list_name}.txt') as f:
                boss_list_text = f.read()

        response = ''

        for boss_name in re.split(r'\n+', boss_list_text):
            try:
                response += f'* {boss_name} → {' / '.join(self.bot.spoiler_log.get_boss_replacement(boss_name))}\n'
            except KeyError:
                pass
            except AttributeError:
                response = "Looks like you haven't uploaded a spoiler log file yet. 🤓 Try uploading one and then trying your command again."
                break

        await send_chunked_response(ctx, response, add_spoiler_tags=(spoiler == 'yes'))

    @discord.slash_command(name='boss-location-in-list', description='Reveals whether a specified boss replaces any of the bosses in a specified list.')
    async def boss_location_in_list(self,
        ctx : discord.ApplicationContext,
        boss_name : Option(str, description='The name of the boss.', autocomplete=get_bosses_split_phases),
        list_name : Option(str, description='The name of the boss list.', autocomplete=get_all_boss_list_names),
        spoiler : Option(str, description='Whether to mark the result as a spoiler.', choices=['yes', 'no'], default='no')
    ):
        try:
            with open(f'Boss Lists/{ctx.guild_id}/{list_name}.txt') as f:
                boss_list_text = f.read()
        except FileNotFoundError:
            with open(f'Boss Lists/{list_name}.txt') as f:
                boss_list_text = f.read()

        response = 'No.'

        for match in re.finditer(r'(.+)(\n*)', boss_list_text):
            try:
                if boss_name in self.bot.spoiler_log.get_boss_replacement(match.group(1)):
                    response = 'Yes.'
                    break
            except KeyError:
                pass
            except AttributeError:
                response = "Looks like you haven't uploaded a spoiler log file yet. 🤓 Try uploading one and then trying your command again."
                break

        await send_chunked_response(ctx, response, add_spoiler_tags=(spoiler == 'yes'))

    @discord.slash_command(name='create-boss-list', description='Creates a custom boss list from attachment or message content.')
    async def create_boss_list(self,
        ctx : discord.ApplicationContext,
        list_name : str
    ):
        list_file_path = f'Boss Lists/{ctx.interaction.guild_id}/{list_name}.txt'

        if Path(list_file_path).exists():
            response = f'The custom boss list `{list_name}` already exists. Use `/replace-boss-list` to replace its contents.'
        else:
            if ctx.message.attachments:
                old_list_body = await ctx.message.attachments[0].read()
                new_list_body = ''

                for match in re.finditer(r'(.+)(\n*)', old_list_body.decode()):
                    if (best_match := get_best_boss_name(match.group(1))):
                        new_list_body += best_match + match.group(2)
                    else:
                        new_list_body += match.group(1)

                with open(list_file_path, 'w') as f:
                    f.write(new_list_body)
            else:
                with open(list_file_path, 'w') as f:
                    f.write(ctx.message.content)

            response = f'The custom boss list `{list_name}` has been created. 👍'

        ctx.respond(response)

    @discord.slash_command(name='replace-boss-list', description='Replaces the contents of an existing custom boss list.')
    async def replace_boss_list(self,
        ctx : discord.ApplicationContext,
        list_name : Option(str, description='The name of the boss list.', autocomplete=get_guild_boss_list_names)
    ):
        list_file_path = f'Boss Lists/{ctx.interaction.guild_id}/{list_name}.txt'

        if ctx.message.attachments:
            old_list_body = await ctx.message.attachments[0].read()
            new_list_body = ''

            for match in re.finditer(r'(.+)(\n*)', old_list_body.decode()):
                if (best_match := get_best_boss_name(match.group(1))):
                    new_list_body += best_match + match.group(2)
                else:
                    new_list_body += match.group(1)

            with open(list_file_path, 'w') as f:
                f.write(new_list_body)
        else:
            with open(list_file_path, 'w') as f:
                f.write(ctx.message.content)

        ctx.respond(f'The contents of the custom boss list `{list_name}` have been replaced. 👍')

    @discord.slash_command(name='rename-boss-list', description='Renames a custom boss list.')
    async def rename_boss_list(self,
        ctx : discord.ApplicationContext,
        list_name : Option(str, description='The name of the boss list.', autocomplete=get_guild_boss_list_names),
        new_name : str
    ):
        Path(f'Boss Lists/{ctx.interaction.guild_id}/{list_name}.txt').rename(
            Path(f'Boss Lists/{ctx.interaction.guild_id}/{new_name}.txt')
        )

        ctx.respond(f'The custom boss list `{list_name}` has been renamed `{new_name}`.')

    @discord.slash_command(name='delete-boss-list', description='Deletes a custom boss list.')
    async def delete_boss_list(self,
        ctx : discord.ApplicationContext,
        list_name : Option(str, description='The name of the boss list.', autocomplete=get_guild_boss_list_names)
    ):
        Path(f'Boss Lists/{ctx.interaction.guild_id}/{list_name}.txt').unlink()
        ctx.respond(f'The custom boss list `{list_name}` has been deleted. ❌')


def setup(bot):
    bot.add_cog(BossPlacements(bot))
