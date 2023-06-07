import asyncio
import wizwalker
from wizwalker import Keycode, HotkeyListener, ModifierKeys, utils
# from wizwalker import WizWalker
from wizwalker.client_handler import ClientHandler
from wizwalker.memory import Window
from loguru import logger


try:
    from wizwalker.memory import MagicSchool
except ImportError:
    from enum import Enum

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
class SlackPack():
    def __init__(self, client):
        self.client = client
        self.root_window = client.root_window
        self.mouse_handler = client.mouse_handler
        self.tabs = [
            "Tab_Hat",
            "Tab_Robe",
            "Tab_Shoes",
            "Tab_Weapon",
            "Tab_Athame",
            "Tab_Amulet",
            "Tab_Ring"
            ]
        self.item_compare = ["compareNewItem", "compareEquipped"]
        self.clients_school = None
        self.highest_damage = 0
        self.highest_damage_index = 1

    async def is_control_grayed(self, button):
        return await button.read_value_from_offset(688, "bool")


    async def get_window_from_path(self, root_window: Window, name_path):
        async def _recurse_follow_path(window, path):
            if len(path) == 0:
                return window

            for child in await window.children():
                if await child.name() == path[0]:
                    found_window = await _recurse_follow_path(child, path[1:])
                    if not found_window is False:
                        return found_window

            return False

        return await _recurse_follow_path(root_window, name_path)


    async def wait_for_window_to_exist(self, parent_window, name, delay=0):
        if type(name) is str:
            while len(w := await parent_window.get_windows_with_name(name)) == 0:
                (delay > 0) and await asyncio.sleep(delay)

            return w[0]

        elif type(name) is list:
            while not (w := await self.get_window_from_path(parent_window, name)):
                (delay > 0) and await asyncio.sleep(delay)

            return w


    async def scan(self):
        self.highest_damage_index = None
        self.highest_damage = 0
        for instance in await self.client.client_object.inactive_behaviors():
            if await instance.read_type_name() == "ClientMagicSchoolBehavior":
                # make this a memory object
                address = await instance.read_base_address()
                school_id = await self.client.hook_handler.read_typed(address + 128, "unsigned int")
                school = str(MagicSchool(school_id))
                parse_school = school.split('.')
                self.clients_school = parse_school[1]
        for i in range(1, 9):
            x = 0
            try:
                selected_item = await self.get_window_from_path(self.root_window, ["WorldView", "DeckConfiguration", f"InventorySpellbookPage", f"Item_{i}"])
                valid = await self.is_control_grayed(selected_item)
                if valid:
                    continue

                fist_path = await self.get_window_from_path(selected_item, ["fist"])

                if await fist_path.is_visible():
                    x = 1
                await self.mouse_handler.set_mouse_position_to_window(selected_item)

                popup = await self.wait_for_window_to_exist(self.root_window, ["WorldView", f"{self.item_compare[x]}", "ControlWidget", "mainLayout"])
                window = await self.get_window_from_path(self.root_window, ["WorldView", f"{self.item_compare[x]}", "ControlWidget", "mainLayout"])
                child = await window.children()
                for stat in range(len(child)):
                    line_of_stat = await child[stat].maybe_text()
                    line_of_stat = line_of_stat.lower()
                    if "damage" in line_of_stat:
                        if self.clients_school in line_of_stat:
                            cluttered_damage_stat = await child[stat].maybe_text()
                            plus_position = cluttered_damage_stat.find('+')
                            neat_damage = int(cluttered_damage_stat[plus_position + 1:plus_position + 3])
                            if neat_damage > self.highest_damage:
                                self.highest_damage = neat_damage
                                self.highest_damage_index = i

                await self.mouse_handler.set_mouse_position(200, 200)
            except AttributeError:
                continue
        if self.highest_damage_index == 1:
            return None
        return self.highest_damage_index


    async def open_and_parse_backpack_contents(self):
        # Check if string contains icon (school) and damage (school)  

        while not await self.get_window_from_path(self.root_window, ["WorldView", "DeckConfiguration", "InventorySpellbookPage"]):
            await self.client.send_key(Keycode.B, 0.1)
            await asyncio.sleep(.2)

        left_button = await self.get_window_from_path(self.root_window, ['WorldView', 'DeckConfiguration', 'InventorySpellbookPage', 'leftscroll'])
        right_button = await self.get_window_from_path(self.root_window, ['WorldView', 'DeckConfiguration', 'InventorySpellbookPage', 'rightscroll'])
        
        for tab in self.tabs:
            await self.client.mouse_handler.click_window_with_name(tab)
            if await left_button.is_visible():
                while not await self.is_control_grayed(left_button):
                    await self.mouse_handler.click_window(left_button)
                while not await self.is_control_grayed(right_button):
                    if (index := await self.scan()) is not None:

                        await self.mouse_handler.click_window_with_name(f"Item_{index}")
                        await self.mouse_handler.click_window_with_name("Equip_Item")
                    await self.mouse_handler.click_window(right_button)
                    print(index)
            if (index := await self.scan()) is not None:
                await self.mouse_handler.click_window_with_name(f"Item_{index}")
                await self.mouse_handler.click_window_with_name("Equip_Item")


    async def main(self):
        await self.open_and_parse_backpack_contents()


async def run():
    walker = ClientHandler()
    client = walker.get_new_clients()[0]
    print("Activating Hooks....")
    try:
        await client.activate_hooks()
        await client.mouse_handler.activate_mouseless()
        
        slack_pack = SlackPack(client)
        try:
            await slack_pack.main()
        except SlackPackError:
            print("Finished SlackPacking")
    finally:
        print("Closing SlackPack")
        await walker.close()

# Start
if __name__ == "__main__":
    asyncio.run(run())
