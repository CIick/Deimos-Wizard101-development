import asyncio
import wizwalker
from wizwalker import Keycode, HotkeyListener, ModifierKeys, utils
# from wizwalker import WizWalker
from wizwalker.client_handler import ClientHandler
from wizwalker.memory import Window
import re
from loguru import logger

async def main(client):

    print("Starting Root Window hook")
    print("Starting Render Context hook")
    print("Hooking done")
    print(await client.zone_name())
    input("Press Enter to continue")
    print(await client.root_window.debug_print_ui_tree())


# Error Handling
async def run():
    walker = ClientHandler()
    client = walker.get_new_clients()[0]

    try:
        await client.activate_hooks()
        await main(client)
    finally:
        print("Closing SlackPack")
        await walker.close()


# Start
if __name__ == "__main__":
    asyncio.run(run())
