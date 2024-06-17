import discord
from discord.ext import commands
from cogs.games.snake import snake_handler as snake
from discord.ui import Button


class SnakeView(discord.ui.View):
    def __init__(self, c, user):
        super().__init__(disable_on_timeout=True, timeout=300)
        self.snake_class = c
        self.user = user
        buttons = ["🔼", "🔽", "◀", "▶"]

    class basicButton(Button):
        def __init__(self, emoji):
            super().__init__(emoji=emoji, style=discord.ButtonStyle.blurple)

        def callback(self, interaction):
            if interaction.user == self.view.user:
                await interaction.response.defer()

                embed = self.view.message.embeds[0]
                move = self.view.snake_class.move_up()
                if move:
                    self.view.disable_all_items()
                    embed.title = 'You died!'
                    embed.description = embed.description + f'\n Final Score: {self.view.snake_class.apples * 10}'
                    await interaction.message.edit(view=self.view, embed=embed)
                    return
                if move is not None:
                    self.view.snake_class.tail_handle()

                embed.description = self.view.snake_class.return_grid()
                embed.description = embed.description + f'\n Score: {self.view.snake_class.apples * 10}'
                await interaction.message.edit(embed=self.view.message.embeds[0])
            else:
                await interaction.response.send_message("This isn't your game!", ephemeral=True)

    @discord.ui.button(style=discord.ButtonStyle.blurple, emoji="🔼")
    async def callback_up(self, _, interaction):
        if interaction.user == self.user:
            await interaction.response.defer()
            embed = self.message.embeds[0]
            move = self.snake_class.move_up()
            if move:
                self.disable_all_items()
                embed.title = 'You died!'
                embed.description = embed.description + f'\n Final Score: {self.snake_class.apples * 10}'
                await interaction.message.edit(view=self, embed=embed)
                return
            if move is not None:
                self.snake_class.tail_handle()

            embed.description = self.snake_class.return_grid()
            embed.description = embed.description + f'\n Score: {self.snake_class.apples * 10}'
            await interaction.message.edit(embed=self.message.embeds[0])
        else:
            await interaction.response.send_message("This isn't your game!", ephemeral=True)

    @discord.ui.button(style=discord.ButtonStyle.blurple, emoji="🔽")
    async def callback_down(self, _, interaction):
        if interaction.user == self.user:
            await interaction.response.defer()
            embed = self.message.embeds[0]

            move = self.snake_class.move_down()
            if move:
                self.disable_all_items()
                embed.title = 'You died!'
                embed.description = embed.description + f'\n Final Score: {self.snake_class.apples * 10}'
                await interaction.message.edit(view=self, embed=embed)
                return
            if move is not None:
                self.snake_class.tail_handle()

            embed.description = self.snake_class.return_grid()
            embed.description = embed.description + f'\n Score: {self.snake_class.apples * 10}'
            await interaction.message.edit(embed=self.message.embeds[0])
        else:
            await interaction.response.send_message("This isn't your game!", ephemeral=True)

    @discord.ui.button(style=discord.ButtonStyle.blurple, emoji="◀")
    async def callback_left(self, _, interaction):
        if interaction.user == self.user:
            await interaction.response.defer()
            embed = self.message.embeds[0]

            move = self.snake_class.move_left()
            if move:
                self.disable_all_items()
                embed.title = 'You died!'
                embed.description = embed.description + f'\n Final Score: {self.snake_class.apples * 10}'
                await interaction.message.edit(view=self, embed=embed)
                return
            if move is not None:
                self.snake_class.tail_handle()

            embed.description = self.snake_class.return_grid()
            embed.description = embed.description + f'\n Score: {self.snake_class.apples * 10}'
            await interaction.message.edit(embed=self.message.embeds[0])
        else:
            await interaction.response.send_message("This isn't your game!", ephemeral=True)

    @discord.ui.button(style=discord.ButtonStyle.blurple, emoji="▶")
    async def callback_right(self, _, interaction):
        if interaction.user == self.user:
            await interaction.response.defer()
            embed = self.message.embeds[0]

            move = self.snake_class.move_right()
            if move:
                self.disable_all_items()
                embed.title = 'You died!'
                embed.description = embed.description + f'\n Final Score: {self.snake_class.apples * 10}'
                await interaction.message.edit(view=self, embed=embed)
                return
            if move is not None:
                self.snake_class.tail_handle()

            embed.description = self.snake_class.return_grid()
            embed.description = embed.description + f'\n Score: {self.snake_class.apples * 10}'
            await interaction.message.edit(embed=self.message.embeds[0])
        else:
            await interaction.response.send_message("This isn't your game!", ephemeral=True)


class SnakeGame(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(description="Snake in discord!")
    async def snake(self, ctx, size: discord.Option(int, min_value=1, max_value=14, required=True),
                    empty_char: discord.Option(str, required=False) = '⬛',
                    snake_char: discord.Option(str, required=False) = '<:polymars:1124864385190461450>',
                    tail_char: discord.Option(str, required=False) = '🟧',
                    apple_char: discord.Option(str, required=False) = '🍎',
                    spawn_rate: discord.Option(int, required=False,
                                               description="Larger the spawn rate, the longer it'll take for apples to spawn",
                                               min_value=1, max_value=100) = 4):
        snake_class = snake.Snake(size, empty_char=empty_char, snake_char=snake_char, tail_char=tail_char,
                                  apple_char=apple_char, spawn_rate=spawn_rate)
        snake_class.start()
        embed = discord.Embed(
            title='Snake',
            description=snake_class.return_grid(),
            color=discord.Color.random()
        )
        embed.description = embed.description + f'\n Score: 0'
        snake_class.spawn_apple()
        await ctx.respond(embed=embed, view=SnakeView(snake_class, user=ctx.author))


def setup(bot: discord.Bot):
    bot.add_cog(SnakeGame(bot))  # Add the cog for snake
