import json
import os
from pathlib import Path
from discord.ext import commands
import discord
from discord_slash import SlashCommand  # Make sure you have this package installed if using slash commands
import pokeformat

__version__ = "v2.0.0"

def read_pokemon(pokemon_list_dir):
    """Reads and loads Pokémon data from a JSON file."""
    try:
        with open(pokemon_list_dir, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        pokeformat.format_poke()  # Attempt to regenerate the Pokémon list if not found.
        return read_pokemon(pokemon_list_dir)  # Recursive call with correct parameter

def special_pokemon(pokemon):
    """Creates a dictionary of special Pokémon forms for quick lookup."""
    special_forms = [
        'Alolan', 'Galarian', 'Shadow', 'Hisuian', 'Therian Enamorus',
        'pom-pom', 'sensu', 'sandy', 'plant', 'trash'
    ]
    return {mon.split(' ')[1]: mon for mon in pokemon if mon.split(' ')[0] in special_forms}

def search_mons(hint, pokemon):
    """Searches for Pokémon based on a hint that may contain underscores as placeholders."""
    possible_mons = [p for p in pokemon if len(hint) == len(p)]
    for i, char in enumerate(hint):
        if char != '_':
            possible_mons = [p for p in possible_mons if p[i] == char]
    return possible_mons

def setup_bot():
    intents = discord.Intents.default()
    intents.messages = True
    intents.guilds = True
    intents.message_content = True  # Enable if your bot reads message content

    bot = commands.Bot(command_prefix='!', intents=intents)
    slash = SlashCommand(bot, sync_commands=True)  # Only necessary if using slash commands

    @bot.event
    async def on_ready():
        print(f'Initialized PokeHelper {__version__}')
        pokemon_list_dir = Path('Bidoof/pokemon.json')
        bot.pokemon = read_pokemon(pokemon_list_dir)
        bot.special_mons = special_pokemon(bot.pokemon)
        print("Pokémon data loaded and ready to go!")

    @bot.command(name='identify')
    async def identify_pokemon(ctx, *, message: str):
        if 'The pokémon is' in message:
            content = message.strip().strip('.')
            pokemon_hint = ''.join('_' if c == '\\' else c for c in content)
            final_mons = search_mons(pokemon_hint, bot.pokemon)
            final_mons.extend(bot.special_mons.get(mon, []) for mon in final_mons if mon in bot.special_mons)
            response = ' '.join(final_mons).replace('_', '')
            await ctx.send(response if response else "No matches found.")

    return bot


if __name__ == "__main__":
    bot = setup_bot()
    bot.run(os.environ['DISCORD_TOKEN'])
