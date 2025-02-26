import re
import json
from collections import defaultdict


ITEM_REPLACEMENT_PATTERN = re.compile(r'^(.+) in (.+): (.+)\. Replaces (.+)\.$')

GREAT_RUNE_ACTIVATION_PATTERN = re.compile(r'^(.+) in .+: Activating \1. Replaces \1.$')

BOSS_REPLACEMENT_PATTERN = re.compile(r'^Replacing .+ \(#(\d+)\) in .+: (.+) \(#\d+\) from.*$')


with open('boss_info_by_name.json') as f:
    BOSS_INFO_BY_NAME = json.load(f)

with open('boss_info_by_id.json') as f:
    BOSS_INFO_BY_ID = json.load(f)


class LogParseException(Exception):
    pass


class SpoilerLog:
    def __init__(self, log_lines):
        if (m := re.match(r'^.*seed:(\d+).*$', log_lines[0])):
            self.log_lines = log_lines
            self.seed = m.group(1)
        else:
            raise LogParseException(
                f'Could not parse line "{log_lines[0]}".'
            )

        self.item_dict = defaultdict(lambda: set())

        for line in self.log_lines[self.log_lines.index('-- Spoilers:'):]:
            if (m := ITEM_REPLACEMENT_PATTERN.match(line)) and not GREAT_RUNE_ACTIVATION_PATTERN.match(line):
                # {New Item: (Item Location, Location Description, Old Item)}
                self.item_dict[m.group(1)].add(m.groups()[1:])

        self.item_dict = dict(self.item_dict)
        self.boss_dict = {}

        boss_start_ix = 1 + self.log_lines.index('-- Boss placements')
        boss_end_ix = self.log_lines.index('-- Miniboss placements')

        for line in self.log_lines[boss_start_ix : boss_end_ix]:
            if (m := BOSS_REPLACEMENT_PATTERN.match(line)):
                # {ID of Old Boss: Name of New Boss}
                self.boss_dict[m.group(1)] = m.group(2)

    def single_item_locations(self, item_name):
        return self.item_dict[item_name]
    
    def item_list_locations(self, item_list):
        return {item: self.item_dict[item] for item in item_list if item in self.item_dict.keys()}

    def get_boss_replacement(self, boss_name):
        return [self.boss_dict[boss_id] for boss_id in BOSS_INFO_BY_NAME[boss_name]]
    
    def locate_boss(self, boss_name):
        return [
            BOSS_INFO_BY_ID[boss_id]
        for boss_id, new_boss_name in self.boss_dict.items() if new_boss_name == boss_name]
