import asyncio
import re
from wizwalker.extensions.scripting.utils import _maybe_get_named_window
from src.utils import *
from src.items_to_quick_sell import *
from loguru import logger


# TODO - We need to check if the trying to get a window fails, if it fails we break from the sell action
class FlashTrash:
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

    async def check_if_client_is_close_to_max_gold(self) -> bool:
        select_character_stats_for_max_gold_calculation = await _maybe_get_named_window(self.client.root_window, 'CharStats')
        async with self.client.mouse_handler:
            await self.client.mouse_handler.click_window(select_character_stats_for_max_gold_calculation)

        window_of_client_current_gold = await _maybe_get_named_window(self.client.root_window, 'Gold')
        messy_client_current_gold = await window_of_client_current_gold.read_wide_string_from_offset(584)
        string_client_current_gold = re.sub('\D', '', messy_client_current_gold)
        client_current_gold = int(string_client_current_gold)


        window_of_client_max_gold = await _maybe_get_named_window(self.client.root_window, 'GoldMax')
        messy_client_max_gold = await window_of_client_max_gold.read_wide_string_from_offset(584)
        string_client_max_gold = re.sub('\D', '', messy_client_max_gold)
        client_max_gold = int(string_client_max_gold)
        client_max_gold_safe_zone = client_max_gold - 20000

        if client_max_gold_safe_zone < client_current_gold:
            logger.debug(f'Client {self.client.title} - is too close to max gold to sell items \nCurrent Gold: {client_current_gold} \nMax Gold: {client_max_gold_safe_zone + 20000} ')
            return True

    async def open_quick_sell_menu(self) -> None:
        # General Logic for detecting if spell book is open, if it's open we need to make sure its on the right tab
        # To Keep it simple, we are starting on Backpack tab, moving to Housing, and Finally Jewels (for now at least)

        spell_book_is_open = await self._check_if_window_is_visible('DeckConfiguration')

        # If spell book is not open, it returns none. We go into the "none if statement" and open the spellbook
        if not spell_book_is_open:
            # print('Spell book not open, manually opening spellbook')
            spellbook = await _maybe_get_named_window(self.client.root_window, "btnSpellbook")
            async with self.client.mouse_handler:
                await self.client.mouse_handler.click_window(spellbook)
            await asyncio.sleep(.2)

        if await self.check_if_client_is_close_to_max_gold():
            # We are checking if gold is close to max. If it is, we close the spell book to allow sigil to continue
            spellbook = await _maybe_get_named_window(self.client.root_window, "btnSpellbook")
            async with self.client.mouse_handler:
                await self.client.mouse_handler.click_window(spellbook)
            return

        inventory_page = await self._check_if_window_is_visible('InventorySpellbookPage')
        # If current page isn't inventory page it returns none. We go into the none if-statement and open the inventory
        if not inventory_page:
            # print('Current page is not backpack, switch to backpack page')
            select_inventory_tab = await _maybe_get_named_window(self.client.root_window, "Inventory")
            async with self.client.mouse_handler:
                await self.client.mouse_handler.click_window(select_inventory_tab)
            await asyncio.sleep(.5)

        # Sometimes the spellbook opening takes some time, so we try and get it, if it fails we just wait and try again
        try:
            quick_sell_tab = await _maybe_get_named_window(self.client.root_window, "QuickSell_Item")
        except ValueError:
            await asyncio.sleep(2)
            quick_sell_tab = await _maybe_get_named_window(self.client.root_window, "QuickSell_Item")

        # I don't know how to detect if the user is on the All Equipments Tab, so we just click it no matter what
        async with self.client.mouse_handler:
            await self.client.mouse_handler.click_window(quick_sell_tab)
        await asyncio.sleep(1)

        select_all_tab = await _maybe_get_named_window(self.client.root_window, 'ShopCategory_All')

        async with self.client.mouse_handler:
            await self.client.mouse_handler.click_window(select_all_tab)
        await asyncio.sleep(.2)

    async def read_each_item(self):
        for i in range(0, 10):
            # We set the path for 'i' which is the item we want to check if we can sell it
            item = await get_window_from_path(self.client.root_window, ["WorldView", "shopGUI", "buyWindow", "column0", f"shoplist{i}"])
            # We set the mouse position over the item to read the meta data of the item
            messy_item_name = await item.read_wide_string_from_offset(616)
            lower_item_name_illegal_characters = messy_item_name.lower()
            item_name = re.sub('[^A-Za-z0-9 ]+', '', lower_item_name_illegal_characters)

            if item_name in items_to_sell:
                item_to_sell_check_box = await get_window_from_path(self.client.root_window, ["WorldView", "shopGUI", "buyWindow", "column1", f"num{i}"])
                check_box_rectangle = await item_to_sell_check_box.scale_to_client()
                async with self.client.mouse_handler:
                    await self.client.mouse_handler.click(*(check_box_rectangle.center()))
                    logger.debug(f'Client {self.client.title} - Quick Selling {item_name}')

    async def logic_for_finalizing_sale(self) -> None:
        quick_sell_items = await _maybe_get_named_window(self.client.root_window, 'sellAction')
        if not await is_control_grayed(quick_sell_items):
            async with self.client.mouse_handler:
                await self.client.mouse_handler.click_window(quick_sell_items)

            confirm_quick_sell_items = await _maybe_get_named_window(self.client.root_window, 'SellButton')
            async with self.client.mouse_handler:
                await self.client.mouse_handler.click_window(confirm_quick_sell_items)

            please_wait = await get_window_from_path(self.client.root_window, ['WorldView', 'shopGUI', 'QuickSellWaitingWindow'])
            while await please_wait.is_visible():
                try:
                    please_wait = await _maybe_get_named_window(self.client.root_window, 'QuickSellWaitingWindow')
                except ValueError:
                    break
        else:
            close_shop = await _maybe_get_named_window(self.client.root_window, 'exit')
            async with self.client.mouse_handler:
                await self.client.mouse_handler.click_window(close_shop)
            await asyncio.sleep(.2)

        await asyncio.sleep(1)
        close_back_pack = await _maybe_get_named_window(self.client.root_window, 'Close_Button')
        async with self.client.mouse_handler:
            await self.client.mouse_handler.click_window(close_back_pack)
        await asyncio.sleep(.2)

    @logger.catch()
    async def open_and_select_backpack_all_tab(self) -> None:
        # Logic for opening backpack to Quick Sell Menu
        await self.open_quick_sell_menu()

        # Check what page the user is on. If they aren't on the first page, set them to the first page
        left_button = await _maybe_get_named_window(self.client.root_window, 'leftscroll')
        right_button = await _maybe_get_named_window(self.client.root_window, 'rightscroll')
        if await left_button.is_visible():
            while not await is_control_grayed(left_button):
                async with self.client.mouse_handler:
                    await asyncio.sleep(.2)
                    await self.client.mouse_handler.click_window(left_button)
        while not await is_control_grayed(right_button):
            async with self.client.mouse_handler:
                await asyncio.sleep(.2)
                await self.read_each_item()
                await self.client.mouse_handler.click_window(right_button)
        # Below reads final page contents
        await self.read_each_item()
        await asyncio.sleep(.2)

        # Logic for finalizing sale + returning character to neutral state so other tools don't break
        await self.logic_for_finalizing_sale()

    async def goto_bazzar(self) -> None:
        go_to_clients_home = await _maybe_get_named_window(self.client.root_window, 'GoHomeButton')
        async with self.client.mouse_handler:
            await self.client.mouse_handler.click_window(go_to_clients_home)


        