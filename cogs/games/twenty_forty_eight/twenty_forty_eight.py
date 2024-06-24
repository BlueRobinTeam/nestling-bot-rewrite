"""
This is the main handler for the 2048 discord handler
"""

# --- Discord Imports ---
import discord
from discord.ext import commands  # for cogs
from discord.ui import Button, View  # for discord buttons
# --- File Imports ---
from cogs.games.twenty_forty_eight import twenty_forty_eight_handler
from cogs.games.twenty_forty_eight import twenty_forty_eight_pillow
import io
import sqlite3

con = sqlite3.connect("2048_scores.db")
cur = con.cursor()
cur.execute("""CREATE TABLE IF NOT EXISTS scores (userID INTEGER, score INTEGER)""")


class TwentyFortyEightButton(Button):
    def __init__(self, row, emoji, game, user, color, text_based):
        super().__init__(style=discord.ButtonStyle.blurple, emoji=emoji, row=row)
        self.game = game
        self.user = user
        self.color = color
        self.text_based = text_based

    async def callback(self, interaction):
        if self.user == interaction.user:
            await interaction.response.defer()
            if self.emoji.name == "▶":
                await self.game.right()
            elif self.emoji.name == "◀":
                await self.game.left()
            elif self.emoji.name == "🔼":
                await self.game.up()
            elif self.emoji.name == "🔽":
                await self.game.down()
            if self.text_based:
                embed = discord.Embed(
                    title="2048",
                    description=f"```\n{await self.game.decrypt_board()}```",
                    colour=discord.Colour.random()
                )
                embed.set_author(name=self.user, icon_url=self.user.avatar.url)

                if await self.game.check_dead():
                    embed.set_footer(text=f"**You died!**\nFinal Score: {self.game.score}")
                    embed.colour = discord.Color.from_rgb(0, 0, 0)
                    return await interaction.message.edit(embed=embed)
                embed.set_footer(text=f"Score: {self.game.score}")
                await interaction.message.edit(
                    embed=embed)
            else:
                if await self.game.check_dead():
                    self.view.disable_all_items()
                    with io.BytesIO() as output:
                        img = await twenty_forty_eight_pillow.convert_board_to_image(self.game.board_list)
                        img.save(output, format="PNG")
                        output.seek(0)
                        return await interaction.message.edit(
                            content=f"Player: {interaction.user}\nFinal Score: {self.game.score}",
                            file=discord.File(output, filename="2048.png"),
                            attachments=[], view=self.view)  # Send the final product into discord
                        # Note: Attachments need to be empty for it to work (it deletes the other attachments and replaces them)
                with io.BytesIO() as output:
                    img = await twenty_forty_eight_pillow.convert_board_to_image(self.game.board_list)
                    img.save(output, format="PNG")
                    output.seek(0)
                    await interaction.message.edit(content=f"Player: {interaction.user}\nScore: {self.game.score}",
                                                   file=discord.File(output, filename="2048.png"),
                                                   attachments=[])  # Send the final product into discord
                    # Note: Attachments need to be empty for it to work (it deletes the other attachments and replaces them)
        else:
            await interaction.response.send_message("This is not your game!", ephemeral=True)


class twenty_forty_eight_view(View):
    def __init__(self, user, game, m, text_based: bool):
        """
        :param user: The user who started the game.
        :param game: The game object to interact with.
        :param m: The message object containing the view.
        :param text_based: If the game should be displayed via text or not.
        """
        super().__init__(timeout=500)
        self.message = m
        self.text_based = text_based
        self.user = user
        self.game = game
        self.add_item(TwentyFortyEightButton(0, "🔼", self.game, user, False, text_based))
        self.add_item(TwentyFortyEightButton(0, "🔽", self.game, user, False, text_based))
        self.add_item(TwentyFortyEightButton(0, "◀", self.game, user, False, text_based))
        self.add_item(TwentyFortyEightButton(0, "▶", self.game, user, False, text_based))

    @discord.ui.button(
        label="Submit",
        style=discord.ButtonStyle.blurple,
        emoji="📤",
        row=2
    )  # Button for the user to submit their score instantly
    async def submit_button_score(self, _, interaction):
        await self.submit_score()
        await interaction.response.send_message(
            "Score submitted! \n *Note: You don't need to press this button to submit the score, "
            "timeouts also submit score automatically*", ephemeral=True)

    async def submit_score(self):
        res = cur.execute("""SELECT * FROM scores WHERE userID IS ?""", (self.user.id,))  # Search for user in the database
        fetch = res.fetchone()
        if fetch:  # If user found
            score = fetch[1]  # User's score
            if self.game.score > score:  # If the score is greater than the current user's score
                cur.execute("""UPDATE scores SET score = ? WHERE userID IS ?""", (self.game.score, self.user.id))
        else:  # If not found, create a new score for that user
            cur.execute("""INSERT INTO scores VALUES(?, ?)""", (self.user.id, self.game.score))
        con.commit()

    async def on_timeout(self):
        await self.submit_score()
        self.disable_all_items()
        if self.text_based:
            new_embed = self.message.embeds[0]
            new_embed.color = discord.Color.darker_grey()
            new_embed.description = new_embed.description + "\n **Timed out!**"
            await self.message.edit(embed=new_embed, view=self)
        else:
            try:
                await self.message.edit(f"{self.message.content} \n **Timed out**", view=self)
            except discord.errors.NotFound:
                pass  # ignore, user deleted their game


class twenty_forty_eight_command(commands.Cog):
    """
    This is the cog for 2048 related commands.
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="2048", description="Play 2048 on Discord!")
    async def twenty_forty_eight_command(self, ctx,
                                         empty_character: discord.Option(str, default="*", min_length=1, max_length=1,
                                                                         description="The empty characters of the board"),
                                         text_based: discord.Option(bool, default=False,
                                                                    description="This is a faster version (faster loading not playing) of the game that doesn't use images."),
                                         size: discord.Option(int, default=4, min_value=2, max_value=10,
                                                              description="Horizontal size of the board")):
        game = await twenty_forty_eight_handler.create_2048(empty_char=empty_character, board_size_x=size,
                                                            board_size_y=size)
        if not text_based:  # makes it image based
            with io.BytesIO() as output:
                img = await twenty_forty_eight_pillow.convert_board_to_image(game.board_list)
                img.save(output, format="PNG")
                output.seek(0)
                message = await ctx.respond(f"Player: {ctx.author}\nScore: 0",
                                            file=discord.File(output,
                                                              filename="2048.png"))  # Send the final product into discord
        else:
            embed = discord.Embed(
                title="2048",
                description=f"```\n{await game.decrypt_board()}```",
                colour=discord.Colour.random()
            )
            embed.set_author(name=ctx.user, icon_url=ctx.user.avatar.url)
            embed.set_footer(text=f"Score: {game.score}")

            message = await ctx.respond(embed=embed)
        view = twenty_forty_eight_view(ctx.user, game, message, text_based)

        await message.edit_original_response(view=view)

    @commands.slash_command(name="2048scoreboard")
    async def scoreboard(self, ctx):
        score_embed = discord.Embed(
            title="2048 Scoreboard",
            color=discord.Colour.random()
        )

        await ctx.respond(embed=score_embed)


def setup(bot: discord.Bot):
    bot.add_cog(twenty_forty_eight_command(bot))  # Add the cog for 2048
