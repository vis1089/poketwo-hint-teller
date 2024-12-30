import json
import os
from pathlib import Path
import discord
from discord import Client
import pokeformat

__version__ = "v2.0.0"

def read_pokemon(pokemon_list_dir):
    try:
        with open(pokemon_list_dir, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        pokeformat.format_poke()
        return read_pokemon()

def special_pokemon(pokemon):
    special_forms = [
        'Alolan', 'Galarian', 'Shadow', 'Hisuian', 'Therian Enamorus',
        'pom-pom', 'sensu', 'sandy', 'plant', 'trash'
    ]
    return {mon.split(' ')[1]: mon for mon in pokemon if mon.split(' ')[0] in special_forms}

def search_mons(hint, pokemon):
    possible_mons = [p for p in pokemon if len(hint) == len(p)]
    for i, char in enumerate(hint):
        if char != '_':
            possible_mons = [p for p in possible_mons if p[i] == char]
    return possible_mons

def main():
    pokemon_list_dir = Path('Bidoof/pokemon.json')
    client = Client()
    pokemon = read_pokemon(pokemon_list_dir)
    special_mons = special_pokemon(pokemon)

    @client.event
    async def on_ready():
        print(f'Initialized PokeHelper {__version__}')

    @client.event
    async def on_message(msg):
        if msg.author.id == 716390085896962058 and 'The pokémon is' in msg.content:
            content = msg.content.strip().strip('.')
            pokemon_hint = ''.join('_' if c == '\\' else c for c in content)
            final_mons = search_mons(pokemon_hint, pokemon)
            final_mons.extend(special_mons.get(mon, []) for mon in final_mons if mon in special_mons)
            await msg.channel.send(' '.join(final_mons).replace('_', ''))

    client.run(os.getenv('DISCORD_TOKEN'))

if __name__ == "__main__":
    main()
