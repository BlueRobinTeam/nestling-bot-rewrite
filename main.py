import discord
import os
import json
from web import main_flask

# --- Discord Intents ---
intents = discord.Intents.default()
# noinspection PyDunderSlots,PyUnresolvedReferences
intents.messages = True
# noinspection PyDunderSlots,PyUnresolvedReferences
intents.message_content = True
# noinspection PyDunderSlots,PyUnresolvedReferences
intents.members = True

# --- Bot ---
bot = discord.Bot(intents=intents)


# --- Basic Listeners ---
@bot.event
async def on_connect():
    # -- Setup Cogs --
    with open(os.path.abspath("./setup.json"), "r") as setup_json:  # Use the setup folder to get the cogs folder
        cogs_folder = json.load(setup_json)["cogs_folder"]  # Load cogs folder from setup JSON

    with open(os.path.abspath(cogs_folder + "/cogs.json"), "r") as cogs_setup_json:
        cogs_json = json.load(cogs_setup_json)  # Json for the list of cogs

    for sub_folder in cogs_json["sub_folders"]:
        for file in cogs_json["sub_folders"][sub_folder]["files"]:
            print(file)
            file_path = f"{cogs_folder.replace('/', '').replace('.', '')}.{sub_folder}.{file}"
            print(f"Loaded {file_path}")
            bot.load_extension(file_path)

    await bot.sync_commands()
    print("Synced commands!")

    await main_flask.start_app(bot)
    print("Website started!")


@bot.event
async def on_ready():
    print("Nestling Bot is ready!")


@bot.slash_command(name="ping")
async def ping(ctx):
    await ctx.respond(f"Hello! My ping is: {bot.latency * 1000}")


bot.run(os.getenv("BOT_TOKEN"))
