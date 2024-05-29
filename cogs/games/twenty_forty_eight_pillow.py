"""
This file is part of 2048 and is used for creating an image from
the board list.
"""

from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw


def convert_board_to_image(board_list, size, empty_char, color_background: (int, int, int),
                           color_font: (int, int, int)):
    font_path = "./fonts/Pixelify_Sans/static/PixelifySans-Regular.ttf"
    img = Image.new(mode="RGB", size=(size, size), color=color_background)
    draw = ImageDraw.Draw(img)
    draw.fontmode = '1'
    box_size = 5
    font_size = size / 5

    board_length = len(board_list)
    tile_x_size = (size / board_length)
    tile_y_size = (size / board_length)
    for x in range(board_length):
        for y in range(len(board_list[x])):
            tile = board_list[x][y]
            if empty_char != tile:
                offset = 0
                if len(tile) > 1:
                    font = ImageFont.truetype(font_path, font_size * (.85 ** len(tile * 2)))

                else:
                    font = ImageFont.truetype(font_path, font_size)
                    offset = font_size / 4
                #  https://stackoverflow.com/questions/16373425/add-text-on-image-using-pil
                draw.text((x * tile_x_size + (size / board_length ** 2),
                           y * tile_y_size + (size / board_length ** 2) - offset), tile, color_font, font=font)
                #  https://stackoverflow.com/questions/51533996/pil-draw-text-without-gray-outline
                rectangle = [(x * tile_x_size, y * tile_y_size),
                             (x * tile_x_size + tile_x_size, y * tile_y_size + tile_y_size)]
                draw.rectangle(rectangle, outline="white", width=box_size,
                               fill=None)  # https://www.geeksforgeeks.org/python-pil-imagedraw-draw-rectangle/
    return img

#  --- Testing Below ---
# test_list = [['*', '2', '*', '*'], ['2', '20', '2048', '*'], ['4', '*', '2', '*'], ['*', '9', '2', '*']]
# convert_board_to_image(test_list, 200, "*", (0, 0, 0), (255, 255, 255))
