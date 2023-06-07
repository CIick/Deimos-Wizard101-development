import asyncio
import time

import wizwalker
from wizwalker import Keycode, HotkeyListener, ModifierKeys, utils
# from wizwalker import WizWalker
from wizwalker.client_handler import ClientHandler
from wizwalker.memory import Window
from src.utils import *
from src.paths import *
from wizwalker.memory.memory_reader import MemoryReadError
from wizwalker.memory.memory_objects.window import (DynamicDeckListControl,
                                                    DynamicSpellListControl,
                                                    SpellListControl,
                                                    DeckListControl,
                                                    DeckListControlSpellEntry,
                                                    SpellListControlSpellEntry)
from wizwalker.extensions.scripting.utils import _maybe_get_named_window
import re
from loguru import logger

try:
    from wizwalker.memory import MagicSchool
except ImportError:
    from enum import Enum


    # In case enum isn't imported, we import it
    # Below Magic School class is for determining what class the user is for calculating
    # Example: If we have an item that is equippable that has Death Damage for our Life Wizard we want to skip that value
    class MagicSchool(Enum):
        ice = 72777
        sun = 78483
        life = 2330892
        fire = 2343174
        star = 2625203
        myth = 2448141
        moon = 2504141
        death = 78318724
        storm = 83375795
        gardening = 663550619
        castle_magic = 806477568
        whirly_burly = 931528087
        balance = 1027491821
        shadow = 1429009101
        fishing = 1488274711
        cantrips = 1760873841


class SlackPackError(Exception):
    """SlackPack Error"""


# @logger.catch
class DeckCheck:
    def __init__(self, client):
        self.client = client
        self.root_window = client.root_window
        self.mouse_handler = client.mouse_handler
        self.schools = [
            'life',
            'fire',
            'myth',
            'ice',
            'death',
            'balance',
            'storm',
        ]
        self.tabs = [
            "Tab_Hat",
            "Tab_Robe",
            "Tab_Shoes",
            "Tab_Weapon",
            "Tab_Athame",
            "Tab_Amulet",
            "Tab_Ring"
        ]
        self.clients_school = None
        self.neat_damage = 0
        self.neat_maxhealth = 0
        self.neat_accuracy = 0
        self.neat_resist = 0
        self.neat_criticalrating = 0
        self.neat_piercing = 0
        self.neat_pips = 0
        self.current_equipped_item = 0
        self.current_new_item = 0


        self._deck_config_window = None

    async def wait_for_window_to_exist(self, parent_window, name, delay=0):
        # Waits for window to exist before acting
        if type(name) is str:
            while len(w := await parent_window.get_windows_with_name(name)) == 0:
                (delay > 0) and await asyncio.sleep(delay)

            return w[0]
        elif type(name) is list:
            while not (w := await get_window_from_path(parent_window, name)):
                (delay > 0) and await asyncio.sleep(delay)

            return w

    async def open_and_parse_deck(self, client):
        # Opens deck, parses through spells tabs
        async with client.mouse_handler:
            await asyncio.sleep(3)
            while not await get_window_from_path(self.root_window, ['WorldView', 'DeckConfiguration', 'DeckConfigurationWindow']):
                await self.client.send_key(Keycode.P, 0.1)
                await asyncio.sleep(.2)
                # Wait for backpack to be open
            next_page = await get_window_from_path(self.root_window,  ['WorldView', 'DeckConfiguration', 'DeckConfigurationWindow', 'ControlSprite', 'DeckPage', 'PageDown'])
            prev_page = await get_window_from_path(self.root_window, ['WorldView', 'DeckConfiguration', 'DeckConfigurationWindow', 'ControlSprite', 'DeckPage', 'PageUp'])
            if await next_page.is_visible():
                while not await is_control_grayed(next_page):
                    await self.mouse_handler.click_window(next_page)
                    if await self.scan_cards() is not None:
                        print('Checking cards')
                        pass
                while not await is_control_grayed(prev_page):
                    await self.mouse_handler.click_window(prev_page)
                    # Above while loop resets to first page of spells
        while await get_window_from_path(self.root_window, ['WorldView', 'DeckConfiguration', 'DeckConfigurationWindow']):
            await self.client.send_key(Keycode.P, 0.1)
            await asyncio.sleep(.2)


    async def scan_cards(self):
        pass

    async def main(self, client):
        await self.open_and_parse_deck(client)



async def run():
    walker = ClientHandler()
    client = walker.get_new_clients()[0]
    print("Activating Hooks....")
    try:
        await client.activate_hooks()
        slack_pack = DeckCheck(client)
        try:
            await slack_pack.main(slack_pack)
        except SlackPackError:
            print("Finished DeckCheck")
    finally:
        print("Closing DeckCheck")
        await walker.close()


# Start
if __name__ == "__main__":
    asyncio.run(run())
