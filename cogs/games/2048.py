# --- Imports ---
import discord
from discord.ext import commands  # for cogs
from discord.ui import Button, View  # for discord buttons
import random
import copy


# --- 2048 Class Handler ---
class TwentyFortyEight:
    def __init__(self):  # consoleOn is a bool that allows printing or not printing
        # --- Default Vars ---
        self.emptyChar = "⬜"
        self.boardX = 4
        self.boardY = 4
        self.boardList = []  # Generates in init_

        # --- Starting variables ---
        self.score = 0
        self.dead = False

    async def create_board(self):
        """
        Must be run after created initializing the TwentyFortyEight class.
        Generates the board list asynchronously.

        create_2048 is a helper function that does this automatically
        """
        random.seed(random.random())

        # --- Generate boardList ---
        rows = []
        for y in range(self.boardY):
            rows.append("⬜")
        columns = []
        for x in range(self.boardX):
            columns.append(rows.copy())
        self.boardList = columns
        for i in range(2):  # Create two twos in the board
            randomNumber = random.randint(1, 2)
            if randomNumber == 1:
                randomEmptyTile = (await self.GetEmptyTiles())[random.randrange(0, len(await self.GetEmptyTiles()))]
                self.boardList[randomEmptyTile[0]][randomEmptyTile[1]] = "2"
            elif randomNumber == 2:
                randomEmptyTile = (await self.GetEmptyTiles())[random.randrange(0, len(await self.GetEmptyTiles()))]
                self.boardList[randomEmptyTile[0]][randomEmptyTile[1]] = "4"
        # --- delete what generated the list ---
        del columns
        del rows
        del randomEmptyTile

    async def DecryptBoard(self):
        finalString = ""
        for i in self.boardList:
            finalString += "\n"
            for e in i:
                try:
                    if type(int(e)) is int:
                        finalString += f"‖{e:2}‖"
                except ValueError:
                    finalString += f"{e:2}"
        return finalString

    async def GetEmptyTiles(self):
        returnList = []
        for y in range(self.boardY):
            for x in range(self.boardX):
                if self.boardList[y][x] == self.emptyChar:
                    returnList.append([y, x])
        return returnList

    async def Down(self):
        await self.MoveTile((1, 0),
                            self.boardList, True)
        # Moves tile down (note: tuple order is (y,x)) (Also note: down is 1 and up is -1)

    async def Right(self):
        await self.MoveTile((0, 1), self.boardList, True)
        # Note that right is 1 and left is -1

    async def Left(self):
        await self.MoveTile((0, -1), self.boardList, True)

    async def Up(self):
        await self.MoveTile((-1, 0), self.boardList, True)

    async def MoveTile(self, direction, boardList,
                       mainBoard: bool):  # main board is to check if the board is the main board. This is to check the scoring
        movedItems = 0  # calculated to create new tiles
        if direction[0] > 0 or direction[1] > 0:
            for i in range(4):  # Push tiles down
                for y in range(self.boardY):
                    for x in range(self.boardX):
                        if boardList[y][x] != self.emptyChar:
                            try:
                                if boardList[y + direction[0]][x + direction[1]] == self.emptyChar:
                                    char = boardList[y][x]
                                    boardList[y][x] = self.emptyChar
                                    boardList[y + direction[0]][x + direction[1]] = char
                                    movedItems += 1
                            except IndexError:
                                pass
            for y in reversed(range(
                    self.boardY)):  # add tiles together (Note: The X and Y are reversed to calculate the merging properly based on the direction)
                for x in reversed(range(self.boardX)):
                    if boardList[y][x] != self.emptyChar:
                        try:
                            if boardList[y + direction[0]][x + direction[1]] == str(boardList[y][x]):
                                char = boardList[y][x]
                                boardList[y][x] = self.emptyChar
                                boardList[y + direction[0]][x + direction[1]] = str(
                                    int(char) * 2)  # multiplies the tile by 2 when merging
                                movedItems += 1
                                if mainBoard:
                                    self.score += int(char) * 2

                        except IndexError:
                            pass
            for i in range(4):  # Push tiles down again
                for y in range(self.boardY):
                    for x in range(self.boardX):
                        if boardList[y][x] != self.emptyChar:
                            try:  # try catch function to check if the index goes out of the board
                                if boardList[y + direction[0]][x + direction[1]] == self.emptyChar:
                                    char = boardList[y][x]
                                    boardList[y][x] = self.emptyChar
                                    boardList[y + direction[0]][x + direction[1]] = char
                                    movedItems += 1
                            except IndexError:
                                pass

        # left and up directions
        elif direction[0] < 0 or direction[1] < 0:
            for i in range(self.boardX + self.boardY):  # calculates pushing the tiles multiple times
                for y in range(self.boardY):
                    for x in range(self.boardX):
                        if boardList[y][x] != self.emptyChar:  # checks if the current tile is empty
                            if (y != 0 and direction[0] != 0) or (x != 0 and direction[1] != 0):
                                # special case where tiles could move off of the board because we are using negative list indexes
                                if boardList[y + direction[0]][x + direction[1]] == self.emptyChar:
                                    char = boardList[y][x]
                                    boardList[y][x] = self.emptyChar
                                    boardList[y + direction[0]][x + direction[1]] = char
                                    movedItems += 1
            for y in range(self.boardY):  # adds the tiles together
                for x in range(self.boardX):
                    if boardList[y][x] != self.emptyChar:
                        if boardList[y + direction[0]][x + direction[1]] == boardList[y][x]:
                            if (y != 0 and direction[0] != 0) or (x != 0 and direction[1] != 0):
                                char = boardList[y][x]
                                boardList[y][x] = self.emptyChar
                                boardList[y + direction[0]][x + direction[1]] = str(int(char) * 2)
                                movedItems += 1
                                if mainBoard:
                                    self.score += int(char) * 2
            for i in range(self.boardX + self.boardY):  # calculates pushing the tiles again
                for y in range(self.boardY):
                    for x in range(self.boardX):
                        if boardList[y][x] != self.emptyChar:  # checks if the current tile is empty
                            if (y != 0 and direction[0] != 0) or (x != 0 and direction[1] != 0):
                                # special case where tiles could move off of the board because we are using negative list indexes
                                if boardList[y + direction[0]][x + direction[1]] == self.emptyChar:
                                    char = boardList[y][x]
                                    boardList[y][x] = self.emptyChar
                                    boardList[y + direction[0]][x + direction[1]] = char
                                    movedItems += 1

        # create a new tile
        if movedItems != 0:
            randomEmptyTile = (await self.GetEmptyTiles())[random.randrange(0, len(await self.GetEmptyTiles()))]
            boardList[randomEmptyTile[0]][randomEmptyTile[1]] = "2"

    async def CheckDead(self):
        newBoard = copy.deepcopy(self.boardList)  # copy of board to check if game is dead
        check = 0
        await self.MoveTile((1, 0), newBoard, False)  # check down
        if newBoard == self.boardList:
            check += 1
        newBoard = copy.deepcopy(self.boardList)  # copy of board to check if game is dead
        await self.MoveTile((0, 1), newBoard, False)  # check right
        if newBoard == self.boardList:
            check += 1
        newBoard = copy.deepcopy(self.boardList)  # copy of board to check if game is dead
        await self.MoveTile((-1, 0), newBoard, False)  # check up
        if newBoard == self.boardList:
            check += 1
        newBoard = copy.deepcopy(self.boardList)  # copy of board to check if game is dead
        await self.MoveTile((0, -1), newBoard, False)  # check left
        if newBoard == self.boardList:
            check += 1
        if check == 4:
            self.dead = True

        return check


class TwentyFortyEightButton(Button):
    def __init__(self, row, emoji, game, user, color):
        super().__init__(style=discord.ButtonStyle.blurple, emoji=emoji, row=row)
        self.game = game
        self.user = user
        self.color = color

    async def callback(self, interaction):
        if self.user == interaction.user:
            await interaction.response.defer()
            if self.emoji.name == "▶":
                await self.game.Right()
            elif self.emoji.name == "◀":
                await self.game.Left()
            elif self.emoji.name == "🔼":
                await self.game.Up()
            elif self.emoji.name == "🔽":
                await self.game.Down()
            embed = discord.Embed(
                title="2048",
                description=await self.game.DecryptBoard(),
                colour=discord.Colour.random()
            )
            embed.set_author(name=self.user, icon_url=self.user.avatar.url)
            embed.set_footer(text=f"Score: {self.game.score}")
            await interaction.message.edit(
                embed=embed)

        else:
            await interaction.response.send_message("This is not your game!", ephemeral=True)


class twenty_forty_eight_view(View):
    def __init__(self, user, game, m):
        super().__init__(timeout=500)
        self.message = m
        self.add_item(TwentyFortyEightButton(0, "🔼", game, user, False))
        self.add_item(TwentyFortyEightButton(0, "🔽", game, user, False))
        self.add_item(TwentyFortyEightButton(0, "◀", game, user, False))
        self.add_item(TwentyFortyEightButton(0, "▶", game, user, False))

    async def on_timeout(self):
        self.disable_all_items()
        await self.message.edit_original_response(view=self)
        await self.message.channel.send("Game timed out!")


class twenty_forty_eight_command(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="2048", description="Play 2048 on Discord!")
    async def twenty_forty_eight_command(self, ctx):
        game = await create_2048()
        string = await game.DecryptBoard()
        embed = discord.Embed(
            title="2048",
            description=string,
            colour=discord.Colour.random()
        )
        embed.set_author(name=ctx.user, icon_url=ctx.user.avatar.url)
        embed.set_footer(text=f"Score: {game.score}")

        message = await ctx.respond(embed=embed)
        view = twenty_forty_eight_view(ctx.user, game, message)

        await message.edit_original_response(view=view)


# -- Helper functions --
async def create_2048() -> TwentyFortyEight:
    """
    Helper func
    :return: TwentyFortyEight
    """
    base_class = TwentyFortyEight()
    await base_class.create_board()
    return base_class


def setup(bot: discord.Bot):
    bot.add_cog(twenty_forty_eight_command(bot))  # Add the cog for 2048
