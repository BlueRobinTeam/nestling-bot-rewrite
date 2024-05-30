# --- Discord Imports ---
import discord
from discord.ext import commands  # for cogs
from discord.ui import Button, View  # for discord buttons
# --- File Imports ---
from cogs.games.twenty_forty_eight import twenty_forty_eight_handler
from cogs.games.twenty_forty_eight import twenty_forty_eight_pillow
import io


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
                embed.set_footer(text=f"Score: {self.game.score}")
                if self.game.check_dead():
                    return await interaction.message.edit(embed=embed)
                await interaction.message.edit(
                    embed=embed)
            else:
                with io.BytesIO() as output:
                    img = await twenty_forty_eight_pillow.convert_board_to_image(self.game.board_list)
                    img.save(output, format="PNG")
                    output.seek(0)
                    await interaction.message.edit(content=f"Score: {self.game.score}", file=discord.File(output, filename="2048.png"), attachments=[])  # Send the final product into discord
                    # Note: Attachments need to be empty for it to work (it deletes the other attachments and replaces them)
        else:
            await interaction.response.send_message("This is not your game!", ephemeral=True)


class twenty_forty_eight_view(View):
    def __init__(self, user, game, m, text_based: bool):
        super().__init__(timeout=500)
        self.message = m
        self.text_based = text_based
        self.add_item(TwentyFortyEightButton(0, "🔼", game, user, False, text_based))
        self.add_item(TwentyFortyEightButton(0, "🔽", game, user, False, text_based))
        self.add_item(TwentyFortyEightButton(0, "◀", game, user, False, text_based))
        self.add_item(TwentyFortyEightButton(0, "▶", game, user, False, text_based))

    async def on_timeout(self):
        self.disable_all_items()
        if self.text_based:
            new_embed = self.message.embeds[0]
            new_embed.color = discord.Color.darker_grey()
            new_embed.description = new_embed.description + "\n **Timed out!**"
            await self.message.edit(embed=new_embed, view=self)
        else:
            await self.message.edit(f"{self.message.content} \n **Timed out**", view=self)


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
                                         text_based: discord.Option(bool, default=False, description="This is a faster version (faster loading not playing) of the game that doesn't use images."),
                                         size: discord.Option(int, default=4, min_value=2, max_value=10,
                                                              description="Horizontal size of the board")):
        game = await twenty_forty_eight_handler.create_2048(empty_char=empty_character, board_size_x=size,
                                                            board_size_y=size)
        if not text_based:  # makes it image based
            with io.BytesIO() as output:
                img = await twenty_forty_eight_pillow.convert_board_to_image(game.board_list)
                img.save(output, format="PNG")
                output.seek(0)
                message = await ctx.respond(
                    file=discord.File(output, filename="2048.png"))  # Send the final product into discord
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


def setup(bot: discord.Bot):
    bot.add_cog(twenty_forty_eight_command(bot))  # Add the cog for 2048
