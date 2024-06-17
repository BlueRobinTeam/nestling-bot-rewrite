# About Cogs
## What is cogs.json?
Cogs.json is the JSON used to implement the cogs into the bot.
Any cog path in cogs.json will be loaded.

## How to load a path
Path folders are loaded with `.`s because that's how the Pycord library currently works. Use `.` for sub folders.

## What py files are which?
The py files that are the same name as the parent folder are the main files and are the 
discord handler. `_handler` files relate to components that the discord handlers use.

# Imports
*Note: Imports are all from the root directory that main.py is running in*