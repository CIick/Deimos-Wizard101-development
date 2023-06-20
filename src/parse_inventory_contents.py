import re
import operator as op
from wizwalker.extensions.scripting.utils import _maybe_get_named_window
from src.utils import *
import asyncio
from wizwalker.client_handler import ClientHandler
import pyperclip

class ParsePack:
    def __init__(self, client: "Client"):
        self.client = client
        self.spell_book_is_open = None
        self.inventory_page = None

    async def open(self):
        pass

    async def close(self):
        pass

    async def __aenter__(self):
        await self.open()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def _check_if_window_is_visible(self, window: str):
        try:
            self.window = await _maybe_get_named_window(self.client.root_window, window)
        except ValueError:
            self.window = None
        return self.window

    @staticmethod
    def remove_special_chars(text):
        pattern = r'[^a-zA-Z0-9, ]+'
        cleaned_text = re.sub(pattern, '', text)
        return cleaned_text

    async def attempt_to_close_all_windows(self) -> None:
        # Logic for attempting to close:
        # 2nd spellbook page being opened, shop window being open, and final spell book being open.
        try:
            try:
                async with self.client.mouse_handler:
                    await self.client.mouse_handler.click_window_with_name('Close_Button')
                await asyncio.sleep(1)
            except ValueError:
                logger.debug(f"Client {self.client.title} - Attempted to close inventory window that didn't exist")
            try:
                async with self.client.mouse_handler:
                    await self.client.mouse_handler.click_window_with_name('exit')
                await asyncio.sleep(1)
            except ValueError:
                logger.debug(f"Client {self.client.title} - Attempted to close inventory window that didn't exist")
            try:
                async with self.client.mouse_handler:
                    await self.client.mouse_handler.click_window_with_name('Close_Button')
                await asyncio.sleep(1)
            except ValueError:
                logger.debug(f"Client {self.client.title} - Attempted to close inventory window that didn't exist")
        except ValueError:
            logger.debug(f'Client {self.client.title} - Attempted to close inventory windows')

    async def open_and_select_backpack_all_tab(self) -> None:
        def reg(m):
            return m.group(1)
        await self.attempt_to_close_all_windows()
        # General Logic for detecting if spell book is open, if it's open we need to make sure its on the right tab
        # To Keep it simple, we are starting on Backpack tab, moving to Housing, and Finally Jewels (for now at least)
        # If spell book is not open, it returns none. We go into the "none if statement" and open the spellbook
        if not await self._check_if_window_is_visible('DeckConfiguration'):
            # print('Spell book not open, manually opening spellbook')
            spellbook = await _maybe_get_named_window(self.client.root_window, "btnSpellbook")
            async with self.client.mouse_handler:
                await self.client.mouse_handler.click_window(spellbook)
            await asyncio.sleep(.2)
        # If current page isnt inventory page it returns none. We go into the "none if-statement" and open the inventory
        if not await self._check_if_window_is_visible('InventorySpellbookPage'):
            # print('Current page is not backpack, switch to backpack page')
            select_inventory_tab = await _maybe_get_named_window(self.client.root_window, "Inventory")
            async with self.client.mouse_handler:
                await self.client.mouse_handler.click_window(select_inventory_tab)
            await asyncio.sleep(.5)
        try:
            quick_sell_tab = await _maybe_get_named_window(self.client.root_window, "QuickSell_Item")
        except ValueError:
            # Clicked too quick
            await asyncio.sleep(3)
            quick_sell_tab = await _maybe_get_named_window(self.client.root_window, "QuickSell_Item")
        # I don't think we can detect if the user is on the 'All Equipments Tab', so we just click it no matter what
        async with self.client.mouse_handler:
            await self.client.mouse_handler.click_window(quick_sell_tab)
        await asyncio.sleep(1)

        select_all_tab = await _maybe_get_named_window(self.client.root_window, 'ShopCategory_All')
        async with self.client.mouse_handler:
            await self.client.mouse_handler.click_window(select_all_tab)
        await asyncio.sleep(.2)

        # Check what page the user is on. If they aren't on the first page, set them to the first page
        left_button = await _maybe_get_named_window(self.client.root_window, 'leftscroll')
        right_button = await _maybe_get_named_window(self.client.root_window, 'rightscroll')

        dupped_list_of_inventory_items = []
        if await left_button.is_visible():
            while not await is_control_grayed(left_button):
                async with self.client.mouse_handler:
                    await asyncio.sleep(.2)
                    await self.client.mouse_handler.click_window(left_button)
        while not await is_control_grayed(right_button):
            async with self.client.mouse_handler:
                await asyncio.sleep(.2)
                await self.read_each_item()
                list_of_inventory_items = await self.read_each_item()
                dupped_list_of_inventory_items.append(list_of_inventory_items)
                await self.client.mouse_handler.click_window(right_button)
        # Below reads final page contents. The while loop breaks, and we want to read the final page of items.
        list_of_inventory_items = await self.read_each_item()
        await asyncio.sleep(.2)
        dupped_list_of_inventory_items.append(list_of_inventory_items)
        master_list_of_inventory_items = []
        # Removing items that are duplicates, we only need one copy in the list of items we sell
        for i in dupped_list_of_inventory_items:
            if op.countOf(dupped_list_of_inventory_items, i) >= 1 and (i not in master_list_of_inventory_items):
                master_list_of_inventory_items.append(i)

        # paperclip doesn't like lists, so we convert it to a sting
        messy_master_string_of_inventory_items: str = ','.join(map(str, master_list_of_inventory_items))

        _master_string_of_inventory_items = self.remove_special_chars(messy_master_string_of_inventory_items)

        # Below was the only way I could get it to remove the damn two trailing char's I didn't want.....
        # master_string_of_inventory_items = re.sub("(.*)(.{2}$)", reg, _master_string_of_inventory_items)

        pyperclip.copy(_master_string_of_inventory_items)
        logger.debug(f'Client {self.client.title} - copied items in backpack to clipboard')
        async with self.client.mouse_handler:
            await self.client.mouse_handler.click_window_with_name('exit')
        async with self.client.mouse_handler:
            await self.client.mouse_handler.click_window_with_name('Close_Button')

    async def read_each_item(self) -> list:
        list_of_items_in_inventory_dupes = []
        for i in range(0, 10):
            # We set the path for 'i' which is the item we want to check if we can sell it
            item = await get_window_from_path(self.client.root_window, ["WorldView", "shopGUI", "buyWindow", "column0", f"shoplist{i}"])
            # We set the mouse position over the item to read the meta data of the item
            messy_item_name = await item.read_wide_string_from_offset(616)
            lower_item_name_illegal_characters = messy_item_name.lower()
            item_name = re.sub('[^A-Za-z0-9 ]+', '', lower_item_name_illegal_characters)
            list_of_items_in_inventory_dupes.append(item_name)
        # list_of_items_in_inventory = dict.fromkeys(list_of_items_in_inventory_dupes)
        # return list_of_items_in_inventory
        return list_of_items_in_inventory_dupes
#
# async def main():
#     walker = ClientHandler()
#     client = walker.get_new_clients()[0]
#
#     try:
#         print('Preparing')
#         await client.activate_hooks()
#         async with ParsePack(client) as parse_pack:
#             await flash_trash.open_and_select_backpack_all_tab()
#
#     finally:
#         print("Closing Flash Trash")
#         await walker.close()
#
#
# if __name__ == "__main__":
#     asyncio.run(main())
#


        