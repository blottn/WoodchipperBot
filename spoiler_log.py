import re
import pickle
from thefuzz import fuzz, process


BELL_BEARING_NAMES = {
    "Smithing-Stone Miner's Bell Bearing [1]",
    "Smithing-Stone Miner's Bell Bearing [2]",
    "Smithing-Stone Miner's Bell Bearing [3]",
    "Smithing-Stone Miner's Bell Bearing [4]",
    "Somberstone Miner's Bell Bearing [1]",
    "Somberstone Miner's Bell Bearing [2]",
    "Somberstone Miner's Bell Bearing [3]",
    "Somberstone Miner's Bell Bearing [4]",
    "Somberstone Miner's Bell Bearing [5]",
}

GREAT_RUNE_NAMES = {
    "Godrick's Great Rune",
    "Great Rune of the Unborn",
    "Malenia's Great Rune",
    "Mohg's Great Rune",
    "Morgott's Great Rune",
    "Radahn's Great Rune",
    "Rykard's Great Rune"
}

OTHER_KEY_ITEM_NAMES = {
    "Academy Glintstone Key",
    "Carian Inverted Statue",
    "Dectus Medallion (Left)",
    "Dectus Medallion (Right)",
    "Discarded Palace Key",
    "Drawing-Room Key",
    "Haligtree Secret Medallion (Left)",
    "Haligtree Secret Medallion (Right)",
    "Pureblood Knight's Medal",
    "Rold Medallion",
    "Rusty Key"
}

PHYSICK_TEAR_NAMES = {
    "Crimson Crystal Tear",
    "Crimsonspill Crystal Tear",
    "Crimsonburst Crystal Tear",
    "Cerulean Crystal Tear",
    "Greenspill Crystal Tear",
    "Greenburst Crystal Tear",
    "Strength-knot Crystal Tear",
    "Dexterity-knot Crystal Tear",
    "Intelligence-knot Crystal Tear",
    "Faith-knot Crystal Tear",
    "Opaline Hardtear",
    "Speckled Hardtear",
    "Leaden Hardtear",
    "Magic-Shrouding Cracked Tear",
    "Flame-Shrouding Cracked Tear",
    "Lightning-Shrouding Cracked Tear",
    "Holy-Shrouding Cracked Tear",
    "Stonebarb Cracked Tear",
    "Spiked Cracked Tear",
    "Thorny Cracked Tear",
    "Twiggy Cracked Tear",
    "Winged Crystal Tear",
    "Windy Crystal Tear",
    "Crimson Bubbletear",
    "Crimsonwhorl Bubbletear",
    "Opaline Bubbletear",
    "Cerulean Hidden Tear",
    "Purifying Crystal Tear",
    "Ruptured Crystal Tear"
}

ITEM_REPLACEMENT_PATTERN = re.compile(r'^(.+) in (.+): (.+)\. Replaces (.+)\.$')

GREAT_RUNE_ACTIVATION_PATTERN = re.compile(r'^(.+) in .+: Activating \1. Replaces \1.$')

# Members are of the form (Name, Is Major Boss?, Is In Core Progression?, Boss ID #1[, Boss ID #2])
NOTED_BOSS_IDS = [
    ("Margit, the Fell Omen", True, True, 10000850),
    ("Godrick the Grafted", True, True, 10000800),
    ("Red Wolf of Radagon", True, False, 14000850),
    ("Rennala, Queen of the Full Moon", True, False, 14000801, 14000800),
    ("Starscourge Radahn", True, False, 1052380800),
    ("Draconic Tree Sentinel", False, True, 1045520800),
    ("Goldfrey, First Elden Lord", True, True, 11000850),
    ("Morgott, the Omen King", True, True, 11000800),
    ("Fire Giant", True, True, 1052520801, 1052520800),
    ("Godskin Duo", True, True, 13000850),
    ("Beast Clergyman / Maliketh, the Black Blade", True, True, 13000801, 13000800),
    ("Sir Gideon Ofnir, the All-Knowing", True, True, 11050850),
    ("Godfrey, First Elden Lord / Hoarah Loux, Warrior", True, True, 11050801, 11050800),
    ("Radagon of the Golden Order / Elden Beast", True, True, 19000810, 19000800),
    ("Leonine Misbegotten", True, False, 1043300800),
    ("Royal Knight Loretta", True, False, 1035500800),
    ("Dragonkin Soldier of Nokstella", True, False, 12010800),
    ("Magma Wyrm Makar", True, False, 39200800),
    ("Elemer of the Briar", True, False, 1039540800),
    ("Mohg, the Omen", True, False, 35000800),
    ("Mimic Tear", True, False, 12020850),
    ("Ancestor Spirit", True, False, 12080800),
    ("Regal Ancestor Spirit", True, False, 12090800),
    ("Valiant Gargoyles", True, False, 12020800),
    ("Fia's Champions", True, False, 12030800),
    ("Godskin Noble", True, False, 16000850),
    ("God-Devouring Serpent / Rykard, Lord of Blasphemy", True, False, 16000801, 16000800),
    ("Commander Niall", True, False, 1051570800),
    ("Loretta, Knight of the Haligtree", True, False, 15000850),
    ("Malenia, Blade of Miquella", True, False, 15000800),
    ("Astel, Naturalborn of the Void", True, False, 12040800),
    ("Mohg, Lord of Blood", True, False, 12050800),
    ("Dragonlord Placidusax", True, False, 13000830)
]

BOSS_REPLACEMENT_PATTERN = re.compile(r'^Replacing .+ \(#(\d+)\) in .+: (.+) \(#\d+\) from.*$')

with open('boss_ids.p', 'rb') as f:
    BOSS_IDS = pickle.load(f)


# the only reason this method is so complicated is because of "radagon"
# matching "Red Wolf of Radagon" before "Radagon of the Golden Order"

def _get_best_boss_replacement_match(boss_name):
    match_tuples = process.extract(boss_name, BOSS_IDS.keys())

    if match_tuples[0][1] == match_tuples[1][1]:
        for t in zip(match_tuples[0][0].split(' '), match_tuples[1][0].split(' ')):
            if fuzz.ratio(boss_name, t[0]) > fuzz.ratio(boss_name, t[1]):
                return match_tuples[0][0]
            elif fuzz.ratio(boss_name, t[0]) < fuzz.ratio(boss_name, t[1]):
                return match_tuples[1][0]

    return match_tuples[0][0]

class LogParseException(Exception):
    def __init__(self, message):
        super().__init__(message)

class UnknownItemException(Exception):
    def __init__(self, message):
        super().__init__(message)


class SpoilerLog:
    def __init__(self, log_lines):
        if (m := re.match(r'^.*seed:(\d+).*$', log_lines[0])):
            self.log_lines = log_lines
            self.seed = m.group(1)
        else:
            raise LogParseException(
                f'Could not parse line "{log_lines[0]}".'
            )

        self.boss_id_dict = {}
        self.item_dict = {}

        self.reveal_bell_bearing_locations = True
        self.reveal_key_item_locations = True
        self.reveal_physick_tear_locations = True
        self.reveal_boss_replacements = True

    def identify_item_locations(self):
        items_to_find = (
            BELL_BEARING_NAMES if self.reveal_bell_bearing_locations else set()
        ) | (
            (GREAT_RUNE_NAMES | OTHER_KEY_ITEM_NAMES) if self.reveal_key_item_locations else set()
        ) | (
            PHYSICK_TEAR_NAMES if self.reveal_physick_tear_locations else set()
        )

        for line in self.log_lines[self.log_lines.index('-- Spoilers:'):]:
            if not items_to_find:
                break

            if (m := ITEM_REPLACEMENT_PATTERN.match(line)) and not GREAT_RUNE_ACTIVATION_PATTERN.match(line):
                item_name = m.group(1)

                try:
                    items_to_find.remove(item_name)
                except KeyError:
                    continue

                item_location_tuple = (m.group(2), m.group(3))
                replacement_item_name = m.group(4)

                if item_name == replacement_item_name:
                    item_location_tuple += ('itself',)
                elif (replacement_item_name in GREAT_RUNE_NAMES) or (replacement_item_name in OTHER_KEY_ITEM_NAMES):
                    item_location_tuple += (replacement_item_name,)
                    
                self.item_dict[item_name] = item_location_tuple

    def reveal_item_location(self, item_name):
        if not self.item_dict:
            self.identify_item_locations()

        ret = []

        for t in (match_tuples := process.extract(item_name, self.item_dict.keys(), scorer=fuzz.token_set_ratio)):
            if t[1] == match_tuples[0][1]:
                item_location_tuple = self.item_dict[t[0]]
                desc = f'"{t[0]}" is in {item_location_tuple[0]}, {item_location_tuple[1][0].lower()}{item_location_tuple[1][1:]}'

                try:
                    if (replacement_item_name := item_location_tuple[2]) == 'itself':
                        desc += ' (replacing itself).'
                    else:
                        desc += f' (replacing "{replacement_item_name}").'
                except IndexError:
                    desc += '.'

                ret.append(desc)
            else:
                break

        return ret
    
    def reveal_all_item_locations(self):
        if not self.item_dict:
            self.identify_item_locations()

        item_sets = (
            [GREAT_RUNE_NAMES, OTHER_KEY_ITEM_NAMES] if self.reveal_key_item_locations else []
        ) + (
            [BELL_BEARING_NAMES] if self.reveal_bell_bearing_locations else []
        )
        
        return [
            [self.reveal_item_location(item_name)[0] for item_name in sorted(item_set)]
        for item_set in item_sets]

    def identify_boss_replacements(self):
        if self.reveal_boss_replacements:
            start_ix = self.log_lines.index('-- Boss placements')
            end_ix = self.log_lines.index('-- Miniboss placements')

            for line in self.log_lines[start_ix:end_ix]:
                if (m := BOSS_REPLACEMENT_PATTERN.match(line)):
                    boss_id = int(m.group(1))

                    # case handling for otherwise ambiguous/confusing boss names
                    if boss_id == 30120800:
                        val = 'Misbegotten Warrior & Perfumer Tricia'
                    elif boss_id == 31180800:
                        val = 'Miranda the Blighted Bloom & Omenkiller'
                    elif boss_id == 1051360800:
                        val = 'Crucible Knight & Misbegotten Warrior'
                    elif boss_id == 30030800:
                        val = 'Spiritcaller Snail (Crucible Knight)'
                    elif boss_id == 31220800:
                        val = 'Spiritcaller Snail (Godskin Duo)'
                    else:
                        val = m.group(2)

                    self.boss_id_dict[boss_id] = val

    def reveal_boss_replacement(self, boss_name):
        if not self.boss_id_dict:
            self.identify_boss_replacements()

        best_match = _get_best_boss_replacement_match(boss_name)
        return f'{best_match} → {self.boss_id_dict[BOSS_IDS[best_match]]}'

    def reveal_major_boss_replacements(self):
        if self.reveal_boss_replacements:
            if not self.boss_id_dict:
                self.identify_boss_replacements()

            return [f'{boss_replacement_tuple[0]} → ' + \
                ' / '.join(self.boss_id_dict[boss_id] for boss_id in boss_replacement_tuple[3:])
            for boss_replacement_tuple in NOTED_BOSS_IDS if boss_replacement_tuple[1]]
    
    def reveal_core_progression_boss_replacements(self):
        if self.reveal_boss_replacements:
            if not self.boss_id_dict:
                self.identify_boss_replacements()

            return [f'{boss_replacement_tuple[0]} → ' + \
                ' / '.join(self.boss_id_dict[boss_id] for boss_id in boss_replacement_tuple[3:])
            for boss_replacement_tuple in NOTED_BOSS_IDS if boss_replacement_tuple[2]]
        
    def reveal_custom_list_boss_replacements(self, boss_list):
        if self.reveal_boss_replacements:
            if not self.boss_id_dict:
                self.identify_boss_replacements()

            return [
                f'{boss_name} → {self.boss_id_dict[BOSS_IDS[boss_name]]}'
            for boss_name in boss_list]
