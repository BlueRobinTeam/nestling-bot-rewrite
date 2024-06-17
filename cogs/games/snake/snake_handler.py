import random


class Snake:
    def __init__(self, grid_size, empty_char='⬛', snake_char='<:polymars:1124864385190461450> ', tail_char='🟧',
                 apple_char='🍎', spawn_rate=4):
        self.running = None  # for console running
        self.grid = [[empty_char for _ in range(grid_size)] for _ in range(grid_size)]  # snake grid
        self.grid_size = grid_size
        self.snake_char = snake_char
        self.tail_char = tail_char
        self.empty_char = empty_char
        self.apple_char = apple_char
        self.spawn_rate = spawn_rate
        self.turns = 0
        row = int(len(self.grid) / 2)
        self.snake_pos = [row, row]
        self.apples = 0
        self.tail_positions = []
        self.last_move = None

    def return_grid(self) -> str:
        """
        Function to return the grid in a format that's readable
        """
        end_return = []
        for x in self.grid:
            row_list = []
            for y in x:
                row_list.append(y)
            end_return.append(" ".join(row_list))
        return "\n".join(end_return)

    def start(self):
        """
        Start the snake game by creating the snake
        """
        self.grid[self.snake_pos[0]][self.snake_pos[1]] = self.snake_char

    # --- Snake Movements ---
    def check_move(self, x_off, y_off, current_move) -> True | False:
        """
        This function is to calculate actions based on the current move.
        If an index error occurs, the snake DIES.
        also I named things weird for some reason
        don't think about it too much...
        IF IT WORKS, IT WORKS

        also,
        if there's an apple it adds a score

        and,
        if there's a tail it kills the snake.
        """
        x = self.snake_pos[1] + x_off  # I did this weird...
        y = self.snake_pos[0] + y_off
        if x >= self.grid_size or x < 0:
            return True  # snake died GG ez
        if y >= self.grid_size or y < 0:
            return True  # snake died GG ez

        if self.grid[y][x] == self.apple_char:
            self.apples += 1
        if self.grid[y][x] == self.tail_char:

            if (current_move == 'up' and self.last_move == 'down') or (
                    current_move == 'down' and self.last_move == 'up') or (
                    current_move == 'left' and self.last_move == 'right') or (
                    current_move == 'right' and self.last_move == 'left'):
                return None  # Do nothing
            return True

        self.turns += 1

        if self.turns % self.spawn_rate == 0:  # custom code to spawn apple every 4 turns
            self.spawn_apple()

        return False

    def move_right(self):  # move snake right
        check = self.check_move(1, 0, 'right')
        if check is None:
            return
        if check:
            self.running = False
            return True

        self.grid[self.snake_pos[0]][self.snake_pos[1]] = self.empty_char  # remove snake from grid
        self.grid[self.snake_pos[0]][self.snake_pos[1] + 1] = self.snake_char  # re-add snake in new position
        self.snake_pos = [self.snake_pos[0], self.snake_pos[1] + 1]
        self.last_move = 'right'
        return False

    def move_left(self):  # move snake left
        check = self.check_move(-1, 0, 'left')
        if check is None:
            return
        if check:
            self.running = False
            return True
        self.grid[self.snake_pos[0]][self.snake_pos[1]] = self.empty_char  # remove snake from grid
        self.grid[self.snake_pos[0]][self.snake_pos[1] - 1] = self.snake_char  # re-add snake in new position
        self.snake_pos = [self.snake_pos[0], self.snake_pos[1] - 1]
        self.last_move = 'left'
        return False

    def move_down(self):  # move snake down
        check = self.check_move(0, 1, 'down')
        if check is None:
            return
        if check:
            self.running = False
            return True
        self.grid[self.snake_pos[0]][self.snake_pos[1]] = self.empty_char  # remove snake from grid
        self.grid[self.snake_pos[0] + 1][self.snake_pos[1]] = self.snake_char  # re-add snake in new position
        self.snake_pos = [self.snake_pos[0] + 1, self.snake_pos[1]]
        self.last_move = 'down'
        return False

    def move_up(self):  # move snake up
        check = self.check_move(0, -1, 'up')
        if check is None:
            return
        if check:
            self.running = False
            return True
        self.grid[self.snake_pos[0]][self.snake_pos[1]] = self.empty_char  # remove snake from grid
        self.grid[self.snake_pos[0] - 1][self.snake_pos[1]] = self.snake_char  # re-add snake in new position
        self.snake_pos = [self.snake_pos[0] - 1, self.snake_pos[1]]
        self.last_move = 'up'
        return False

    def spawn_apple(self):
        spawn_points = []
        for x in range(self.grid_size):
            for y in range(self.grid_size):
                if self.grid[x][y] != self.snake_char:
                    if self.grid[x][y] != self.tail_char and self.grid[x][y] != self.apple_char:
                        spawn_points.append([x, y])
        random_choice = 0
        try:
            random_choice = random.randint(0, len(spawn_points) - 1)
        except ValueError:
            pass
        try:
            self.grid[spawn_points[random_choice][0]][spawn_points[random_choice][1]] = self.apple_char
        except IndexError:
            pass

    def tail_handle(self):
        if self.apples > 0:
            self.tail_positions.append(self.snake_pos.copy())  # the copy is important
            for pos in self.tail_positions:
                if pos != self.snake_pos:
                    self.grid[pos[0]][pos[1]] = self.tail_char

            if self.apples < len(self.tail_positions) - 1:
                if self.tail_positions[0] != self.snake_pos:
                    self.grid[self.tail_positions[0][0]][
                        self.tail_positions[0][1]] = self.empty_char  # replace end tail with empty char
                    self.tail_positions.pop(0)
