"""
This file is part of 2048 and is used for creating an image from
the board list.
"""

from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw


def convert_board_to_image(board_list, size_x, size_y, font_size, empty_char):
    img = Image.new(mode="RGB", size=(200, 200), color=(0, 0, 0))
    draw = ImageDraw.Draw(img)
    board_length = len(board_list)
    for x in range(board_length):
        for y in range(len(board_list[x])):
            tile = board_list[x][y]
            if empty_char != tile:
                if len(tile) > 1:
                    font = ImageFont.truetype("./fonts/Poetsen_One/PoetsenOne-Regular.ttf", font_size * (.85 ** len(tile)))
                else:
                    font = ImageFont.truetype("./fonts/Poetsen_One/PoetsenOne-Regular.ttf", font_size)
                # https://stackoverflow.com/questions/16373425/add-text-on-image-using-pil
                draw.text((x*(size_x/board_length) + (size_x/board_length**2) - (font_size/board_length), y*(size_y/board_length) + (size_y/board_length**2) - (font_size/board_length)), tile, (255, 255, 255), font=font)

    img.save('sample-out.jpg')


#  --- Testing Below ---
test_list = [['*', '2', '*', '*'], ['2', '44', '*', '*'], ['4', '*', '*', '*'], ['*', '*', '*', '*']]
convert_board_to_image(test_list, 300, 300, 60, "*")
