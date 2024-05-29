"""
This file is part of 2048 and is used for creating an image from
the board list.
"""

from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
import math


def convert_board_to_image(board_list, size_x, size_y, font_size, empty_char, color_background: (int, int, int), color_font: (int, int, int)):
    """
    :param board_list: List from twenty_forty_eight_handler.py object
    :param size_x: horizontal size of the image
    :param size_y: vertical size of the image
    :param font_size:
    :param empty_char:
    :param color_background:
    :param color_font:
    :return:
    """
    font_path = "./fonts/Pixelify_Sans/static/PixelifySans-Regular.ttf"
    img = Image.new(mode="RGB", size=(size_x, size_y), color=color_background)
    draw = ImageDraw.Draw(img)

    board_length = len(board_list)
    tile_x_size = (size_x/board_length)
    tile_y_size = (size_y/board_length)
    for x in range(board_length):
        for y in range(len(board_list[x])):
            tile = board_list[x][y]
            if empty_char != tile:
                if len(tile) > 1:
                    font = ImageFont.truetype(font_path, font_size * (.85 ** len(tile*2)))
                else:
                    font = ImageFont.truetype(font_path, font_size)
                # https://stackoverflow.com/questions/16373425/add-text-on-image-using-pil
                draw.text((x*tile_x_size + (size_x/board_length**2), y*tile_y_size + (size_y/board_length**2) - (math.log(font_size))**2), tile, color_font, font=font)
                rectangle = [(x*tile_x_size, y*tile_x_size), (x*tile_x_size + tile_x_size, y*tile_x_size + tile_x_size)]
                draw.rectangle(rectangle, outline="green")  # https://www.geeksforgeeks.org/python-pil-imagedraw-draw-rectangle/

    img.save('sample-out.jpg')


#  --- Testing Below ---
test_list = [['*', '2', '*', '*'], ['2', '20', '2048', '*'], ['4', '*', '2', '*'], ['*', '*', '2', '*']]
convert_board_to_image(test_list, 300, 300, 60, "*", (0, 0, 0), (255, 255, 255))
