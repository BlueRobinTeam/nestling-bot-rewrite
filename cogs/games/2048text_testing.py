"""
This file is used to test the 2048 handler without having to run the bot itself.
If you want to do bot unrelated optimization tests for 2048, this is a good place to do it.
"""

import twenty_forty_eight_handler
import asyncio


async def main():
    game = await twenty_forty_eight_handler.create_2048()
    running = True
    while running:
        print(await game.decrypt_board())
        print(f"Score: {game.score}")
        i = input()

        if i == 'stop':
            running = False
            break

        if i == 'restart':
            game = await twenty_forty_eight_handler.create_2048()
            continue

        if i == "r" or i == "right":
            await game.right()
        elif i == "u" or i == "up":
            await game.up()
        elif i == "d" or i == "down":
            await game.down()
        elif i == "l" or i == "left":
            await game.left()




def start():
    asyncio.run(main=main())


start()
