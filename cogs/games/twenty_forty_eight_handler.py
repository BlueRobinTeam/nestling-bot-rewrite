import random
import copy


# --- 2048 Class Handler ---
class TwentyFortyEight:
    def __init__(self, board_size_x=4, board_size_y=4, empty_char="⬜"):
        # --- Default Vars ---
        self.empty_char = empty_char
        self.board_size_x = board_size_x
        self.board_size_y = board_size_y
        self.board_list = []  # Generates in init_

        # --- Starting variables ---
        self.score = 0
        self.dead = False
        self.tile_positions = []

    async def create_board(self):
        """
        Must be run after created initializing the TwentyFortyEight class.
        Generates the board list asynchronously.

        create_2048 is a helper function that does this automatically
        """
        random.seed(random.random())

        # --- Generate boardList ---
        rows = []
        for _ in range(self.board_size_x):
            rows.append(self.empty_char)
        columns = []
        for _ in range(self.board_size_y):
            columns.append(rows.copy())

        self.board_list = columns.copy()  # Save the generated board list

        # -- Generate the starting numbers on the board --
        for i in range(2):
            random_number = random.randint(1, 2)
            if random_number == 1:
                await self.add_tile(2)
            elif random_number == 2:  # Generate a four by random chance
                await self.add_tile(4)

    async def add_tile(self, tile: int):
        random_empty_tile = await self.random_empty_tile()
        self.board_list[random_empty_tile[0]][random_empty_tile[1]] = str(tile)
        self.tile_positions.append([random_empty_tile[0], random_empty_tile[1], tile])

    async def decrypt_board(self):
        final_string = ""
        for y in range(self.board_size_y):
            final_string += '\n'
            for x in range(self.board_size_x):
                final_string += str(self.board_list[x][y]) + '\t'

        return final_string

    async def get_empty_tiles(self):
        returnList = []
        for x in range(self.board_size_x):
            for y in range(self.board_size_y):
                if self.board_list[x][y] == self.empty_char:
                    returnList.append([x, y])
        return returnList

    async def random_empty_tile(self):
        """Gets a random empty tile from get_empty_tiles"""
        empty_tiles = await self.get_empty_tiles()
        return empty_tiles[random.randrange(0, len(empty_tiles))]

    async def down(self):
        await self.move_tile('down', True)

    async def right(self):
        await self.move_tile('right', True)

    async def left(self):
        await self.move_tile('left', True)

    async def up(self):
        await self.move_tile('up', True)
        print('up')

    async def check_tile(self, position):
        """
        Checks if the tile is empty or not.
        :param position:
        :return: Int or None if empty
        """

    async def collides_with(self, check_tile: (int, int)) -> bool:
        """
        This is to check if a tile is colliding with another tile
        :param check_tile: (x, y) where the tile could move
        :return: Bool
        """

        for tile in self.tile_positions:
            if tile[0] == check_tile[0] and tile[1] == check_tile[1]:
                return True  # Collided
        return False  # Did not collide

    async def move_tile(self, direction,
                        mainBoard: bool):
        copy_board = copy.deepcopy(self.board_list)
        moved = False
        if direction == 'down' or direction == 'right':
            start = self.board_size_y - 1
            end = -1
            step = -1
        else:
            if direction == 'up':
                end = self.board_size_y
            else:
                end = self.board_size_x
            step = 1
            start = 0
        if direction == 'up' or direction == 'down':

            for x in range(self.board_size_x):
                for y in range(start, end, step):
                    tile = copy_board[x][y]
                    if copy_board[x][y] == self.empty_char:
                        continue

                    if direction == 'up':
                        possible_directions = range(y - 1, -1, -1)
                    else:  # down
                        possible_directions = range(y + 1, self.board_size_y, 1)
                        print(list(possible_directions))

                    for possible_y in possible_directions:
                        if copy_board[x][possible_y] == self.empty_char:

                            copy_board[x][y] = self.empty_char
                            copy_board[x][possible_y] = str(tile)
                            y = possible_y
                            moved = True

                        elif int(copy_board[x][possible_y]) == int(copy_board[x][y]):
                            copy_board[x][y] = self.empty_char
                            copy_board[x][possible_y] = str(int(tile) * 2)
                            moved = True
                            break

                        else:
                            break  # tile collided

        self.board_list = copy_board
        if moved:
            await self.add_tile(2)


# -- Helper functions --
async def create_2048(**kwargs) -> TwentyFortyEight:
    """
    :param kwargs: Same parameters as the main TwentyFortyEight handler

    Helper func
    :return: TwentyFortyEight
    """
    base_class = TwentyFortyEight(**kwargs)
    await base_class.create_board()
    return base_class
