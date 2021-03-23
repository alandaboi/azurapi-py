import os
import json
import requests
import re

from .utils import *

# Constant URLs
MAIN_URL = 'https://raw.githubusercontent.com/AzurAPI'
PRIMARY_BRANCH = '/azurapi-js-setup/master'
SHIP_LIST = f'{MAIN_URL}{PRIMARY_BRANCH}/ships.json'
CHAPTER_LIST = f'{MAIN_URL}{PRIMARY_BRANCH}/chapters.json'
EQUIPMENT_LIST = f'{MAIN_URL}{PRIMARY_BRANCH}/equipments.json'
VERSION_INFO = f'{MAIN_URL}{PRIMARY_BRANCH}/version-info.json'
MEMORIES_INFO = f'{MAIN_URL}{PRIMARY_BRANCH}/memories.json'
AVAILABLE_LANGUAGES = ['en', 'cn', 'jp', 'kr', 'code', 'official']
FACTIONS = [['USS', 'Eagle Union'], ['HMS', 'Royal Navy'], ['IJN', 'Sakura Empire'], ['KMS', 'Ironblood'],
            ['ROC', 'Eastern Radiance'], ['SN', 'North Union'], ['FFNF', 'Iris Libre'], ['MNF', 'Vichya Dominion'],
            ['RN', 'Sardegna Empire'], ['HDN', 'Neptunia'], ['Bilibili'], ['Utawarerumono'], ['KizunaAI']]


class AzurAPI:

    def __init__(self, offline=True, folder=os.getcwd()):
        if not folder.endswith('/'):
            folder += '/'
        if offline:
            try:
                self.ship_list = json.load(open(folder + 'ships.json', 'r'))
                self.chapter_list = json.load(open(folder + 'chapters.json', 'r'))
                self.equipment_list = json.load(open(folder + 'equipments.json', 'r'))
                self.version_info = json.load(open(folder + 'version-info.json', 'r'))
                self.memories_info = json.load(open(folder + 'ships.json', 'r'))
            except FileNotFoundError as e:
                print(e)
                print('Local files not found. Please relocate or boot in online mode.')
        else:
            self.ship_list = requests.get(SHIP_LIST).json()
            self.chapter_list = requests.get(CHAPTER_LIST).json()
            self.equipment_list = requests.get(EQUIPMENT_LIST).json()
            self.version_info = requests.get(VERSION_INFO).json()
            self.memories_info = requests.get(MEMORIES_INFO).json()
            with open(folder + 'ships.json', 'w') as outfile:
                json.dump(self.ship_list, outfile)
            with open(folder + 'chapters.json', 'w') as outfile:
                json.dump(self.chapter_list, outfile)
            with open(folder + 'equipments.json', 'w') as outfile:
                json.dump(self.equipment_list, outfile)
            with open(folder + 'version-info.json', 'w') as outfile:
                json.dump(self.version_info, outfile)
            with open(folder + 'memories.json', 'w') as outfile:
                json.dump(self.memories_info, outfile)
        self.folder = folder

    def update(self):
        newest_version = requests.get(VERSION_INFO).json()
        if newest_version['ships']['version-number'] > self.version_info['ships']['version-number'] or \
                newest_version['equipments']['version-number'] > self.version_info['equipments']['version-number']:
            with open(self.folder + 'version-info.json', 'w') as outfile:
                json.dump(self.version_info, outfile)

    def get_ship(self, identifier):
        try:
            return self.get_ship_by_name(identifier)
        except (ValueError, UnknownShipException):
            try:
                return self.get_ship_by_id(identifier)
            except UnknownShipException:
                raise UnknownShipException

    def get_ship_by_name(self, name):
        ship = next(
            (item for item in self.ship_list if
             name.lower() in [value.lower() for value in item['names'].values() if value is not None]), None)
        if ship is None:
            raise UnknownShipException('No ship found with given name')
        return ship

    def get_ship_by_id(self, ship_id):
        if len(ship_id) < 3:
            ship_id = '0' + ship_id
        ship = next(
            (item for item in self.ship_list if item['id'] == ship_id))
        if ship is None:
            raise UnknownShipException('No ship found with given id')
        return ship

    def get_version(self):
        ships_version = self.version_info['ships']['version-number']
        equipments_version = self.version_info['equipments']['version-number']
        return f'Ships Version: {ships_version} | Equipments Version: {equipments_version}'

    def get_all_ships_by_language(self, language):
        if language not in AVAILABLE_LANGUAGES:
            raise UnknownLanguageException('Language not supported.')
        return [ship for ship in self.ship_list if ship.get('names')[language] is not None]

    def get_all_ships_en(self):
        return self.get_all_ships_by_language('en')

    def get_all_ships_cn(self):
        return self.get_all_ships_by_language('cn')

    def get_all_ships_jp(self):
        return self.get_all_ships_by_language('jp')

    def get_all_ships_kr(self):
        return self.get_all_ships_by_language('kr')

    def get_all_ships_code(self):
        return self.get_all_ships_by_language('code')

    def get_ship_by_language(self, name, language):
        ship_list = self.get_all_ships_by_language(language)
        ship = next(
            (item for item in ship_list if
             name.lower() in [value.lower() for value in item['names'].values() if value is not None]), None)
        if ship is None:
            raise UnknownShipException('No ship found with given name and language')
        return ship

    def get_ship_en(self, name):
        return self.get_ship_by_language(name, 'en')

    def get_ship_cn(self, name):
        return self.get_ship_by_language(name, 'cn')

    def get_ship_jp(self, name):
        return self.get_ship_by_language(name, 'jp')

    def get_ship_kr(self, name):
        return self.get_ship_by_language(name, 'kr')

    def get_ship_code(self, name):
        return self.get_ship_by_language(name, 'code')

    def get_ship_by_faction(self, faction):
        faction = faction.lower()
        indexes = [ind for ind, i in enumerate(FACTIONS) if len([j for j in i if faction == j.lower()]) > 0]
        if len(indexes) == 0:
            raise UnknownFactionException(f'Faction: {faction} not found.')
        faction = FACTIONS[indexes[0]][-1]
        return [ship for ship in self.ship_list if ship['nationality'] == faction]

    def get_chapter(self, chapter, **kwargs):
        [chapter, stage] = re.split(r'\D+', chapter)
        diff = kwargs.get('diff', None)
        if not self.chapter_list[chapter][stage]:
            raise UnknownChapterException(f'Unknown Chapter: {chapter}-{stage}.')
        elif diff is not None:
            if not self.chapter_list[chapter][stage][diff]:
                raise UnknownDifficultyException(f'Unknown difficulty: {chapter}-{stage} ({diff})/')
            else:
                return self.chapter_list[chapter][stage][diff]
        else:
            return self.chapter_list[chapter][stage]

    def get_memories(self, memory):
        memories = self.memories_info
        for key in memory.keys():
            if memory.lower() == key.lower():
                return memories[key]
        raise UnknownMemoryException(f'Unable to view {memory} memory.')

    def get_all_equipments(self):
        return self.equipment_list

    def get_all_equipments_by_language(self, language):
        if language.lower() not in AVAILABLE_LANGUAGES:
            raise UnknownLanguageException(f'Language {language} not found.')
        if language.lower() in ['code', 'official']:
            return self.equipment_list
        return [item for item in self.equipment_list if item['names'][language] is not None]

    def get_equipment_by_language(self, name, language):
        if language.lower() not in AVAILABLE_LANGUAGES:
            raise UnknownLanguageException(f'Language {language} not found.')
        if language.lower() in ['code', 'official']:
            return [item for item in self.equipment_list if name in item.key()]
        return [item for item in self.equipment_list if name in item['names'][language]]

    def get_equipment_en(self, name):
        return self.get_equipment_by_language(name, 'en')

    def get_equipment_cn(self, name):
        return self.get_equipment_by_language(name, 'cn')

    def get_equipment_jp(self, name):
        return self.get_equipment_by_language(name, 'jp')

    def get_equipment_kr(self, name):
        return self.get_equipment_by_language(name, 'kr')

    def get_equipment_code(self, name):
        return self.get_equipment_by_language(name, 'code')
