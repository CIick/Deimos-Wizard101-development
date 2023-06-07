import asyncio

from wizwalker import ClientHandler
from wizwalker.extensions.scripting.deck_builder import DeckBuilder
from wizwalker.extensions.scripting.utils import _maybe_get_named_window


async def main():
    handler = ClientHandler()
    client = handler.get_new_clients()[0]

    try:
        print("Preparing")
        await client.activate_hooks()
        async with DeckBuilder(client) as deck_builder:
            # await deck_builder.log_user_in_and_out()
            for i in range(1):
                await deck_builder.open_deck_page()
                deck = await deck_builder.get_deck_preset()
                print(deck)
                input()
                await deck_builder.open_deck_page()
                deck = await deck_builder.get_deck_preset()
                print(deck)
                # deck = {'normal': {'Angry Snowpig': 1, 'Handsome Fomori': 1, 'Winter Moon': 1, 'Aegis': 1, 'Colossal': 1, 'Daybreaker - T03 - A': 1, 'Epic': 1, 'Gargantuan': 1, 'Giant': 1, 'Indemnity': 1, 'Monstrous': 1, 'Nightbringer - T03 - A': 1, 'Potent Trap': 1, 'Sharpened Blade': 1, 'Strong': 1, 'Goat Monk': 1, 'Pigsie': 1, 'Pixie': 1, "Ratatoskr's Spin": 1, 'Brimstone Revenant': 1, 'Athena Battle Sight': 1, 'CollectEssenceUndead': 1, "Grendel's Amends": 1, 'Ninja Pig': 1, 'Berserk': 1, 'Brace': 1, 'Fortify': 1, 'Frenzy': 1, 'Banshee': 1, 'Dark Sprite': 1, 'Dream Shield': 1, 'Feint': 1, 'Ghoul': 1, 'Lord of Night': 1, 'Skeletal Pirate': 1, 'Vampire': 1, 'Cleanse Charm': 1, 'Cripple': 1, 'Darkwind': 1, 'Defibrillate': 1, 'Disarm': 1, 'Dissipate': 1, 'Insane Bolt': 1, 'Lightning Bats': 1, 'Lightning Strike': 1, 'Mass Storm Prism': 1, 'Minion Storm': 1, 'Queen Calypso': 1, 'Ramp_Storm_03': 1, 'Sooth': 1, 'Storm Prism': 1, 'Storm Shark': 1, 'Storm Shield': 1, 'Storm Trap': 1, 'Stormblade': 1, 'Stormspear': 1, 'Supercharge': 1, 'Tempest': 1, 'Thermic Shield': 1, 'Thunder Snake': 1, 'Wild Bolt': 1, 'Windstorm': 1}, 'tc': {}, 'item': {}}
                # await deck_builder.set_deck_preset(deck, ignore_failures=True)

            # await deck_builder.get_deck_spell_list()
            # print(await deck_builder.get_deck_spell_list())
            # await deck_builder.set_deck_preset(ignore_failures=False)
            # await deck_builder.calculate_deck_card_position(4)
            # # await deck_builder.remove_by_name('Epic', 3)
            # await deck_builder.calculate_card_position(4)

            # await deck_builder.add_by_name('Thunder Snake', number_of_copies=None)
            # await deck_builder.add_by_name('Leviathan', number_of_copies=None)
            # await deck_builder.add_by_name('Savage Paw', number_of_copies=None)
            # await deck_builder.add_by_name('Stormzilla', number_of_copies=None)
            # await deck_builder.add_by_name('Vampire', number_of_copies=None)
            # await deck_builder.add_by_name('Epic', number_of_copies=None)

            # await deck_builder.set_page(0)
            # await deck_builder.calcuate_window_areas()
            # click = await deck_builder.calculate_card_position(4)
            # deck_builder.calcuate_page_of_card(['22','22','22','22','22','22','22','22','22','22','22','22','22','22','22','22','22','22','22','22','22','22','22','22', 'hello'], 'hello')
            # async with client.mouse_handler:
            #     await client.mouse_handler.click(*click)
            # card = await deck_builder.get_spell_list_rectangle()
            # # new = card.sc
            # # for i in range(100000):
            # #     card.paint_on_screen(client.window_handle)
            # async with client.mouse_handler:
            #     await asyncio.sleep(1)
                # await client.mouse_handler.click(331, 630)
                # pyautogui.click(card_pos)
            # list_of_spells = await deck_builder.get_spell_list()
            # for card in list_of_spells:
            #     graphical = await card.graphical_spell()
            #     template = await graphical.spell_template()
            #     print(await template.name())

            # print(await deck_builder.spell_list_match_template('Unicorn'))
            # print(await deck_builder.deck_list_match_template('Unicorn'))

            # print(await deck_builder.get_graphical_deck_cards())
            # await deck_builder.clear_deck()
            pass
            # # adds two unicorns
            # await deck_builder.add_by_name("Unicorn", 2)


    finally:
        print("Closing")
        await handler.close()


if __name__ == "__main__":
    asyncio.run(main())