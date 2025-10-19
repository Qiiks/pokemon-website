import requests
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import json
import os
import uvicorn
from difflib import get_close_matches
import sqlite3
import time
from typing import Dict, List, Any, Optional
from functools import lru_cache
import asyncio
import aiohttp

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API URLs
MOVESET_URLS = [
    "https://pokeapi.co/api/v2/pokemon/{pokemon}/"  # PokeAPI endpoint for Pokemon data
]

# Database configuration
DB_PATH = 'pokemon.db'

# Initialize SQLite database with connection pooling
def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# Create database tables if they don't exist
def initialize_database():
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        print("[DEBUG] Initializing database tables...")
        # Table for raw Pokemon data
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pokemon_data (
                name TEXT PRIMARY KEY,
                data TEXT,
                timestamp INTEGER
            )
        """)
        # Table for processed Pokemon data (final response)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS processed_pokemon (
                name TEXT PRIMARY KEY,
                data TEXT,
                timestamp INTEGER
            )
        """)
        # Table for species data
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pokemon_species (
                name TEXT PRIMARY KEY,
                data TEXT,
                timestamp INTEGER
            )
        """)
        # Table for evolution chain data
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS evolution_chains (
                id INTEGER PRIMARY KEY,
                data TEXT,
                timestamp INTEGER
            )
        """)
        # Table for tags/movesets
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tags (
                ID TEXT PRIMARY KEY,
                value TEXT
            )
        """)
        # Table for movesets data
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS movesets (
                pokemon_name TEXT PRIMARY KEY,
                data TEXT,
                timestamp INTEGER
            )
        """)
        conn.commit()
    finally:
        conn.close()
    print("Database initialized successfully")

# Helper functions
def capitalize_first_letter(s):
    return s[0].upper() + s[1:] if s else s

def title_case(s, separator='-'):
    return ' '.join(capitalize_first_letter(part) for part in s.split(separator)) if s else s

# Dictionary for animation name replacements
ANI_NAME_REPLACEMENTS = {
    "charizard-mega-x": "charizard-megax",
    "charizard-mega-y": "charizard-megay",
    "mewtwo-mega-x": "mewtwo-megax",
    "mewtwo-mega-y": "mewtwo-megay",
    "deoxys-normal": "deoxys",
    "pikachu-original-cap": "pikachu-original",
    "pikachu-hoenn-cap": "pikachu-hoenn",
    "pikachu-sinnoh-cap": "pikachu-sinnoh",
    "pikachu-unova-cap": "pikachu-unova",
    "pikachu-kalos-cap": "pikachu-kalos",
    "pikachu-alola-cap": "pikachu-alola",
    "pikachu-partner-cap": "pikachu-partner",
    "pikachu-rock-star": "pikachu-rockstar",
    "pikachu-pop-star": "pikachu-popstar",
    "nidoran-m": "nidoranm",
    "necrozma-dusk": "necrozma-duskmane",
    "necrozma-dawn": "necrozma-dawnwings",
    "toxtricity-low-key": "toxtricity-lowkey",
    "toxtricity-amped": "toxtricity",
    "toxtricity-amped-gmax": "toxtricity-gmax",
    "shaymin-land": "shaymin",
    "wormadam-plant": "wormadam",
    "giratina-altered": "giratina"
}

# Dictionary for display name replacements
DISPLAY_NAME_REPLACEMENTS = {
    "charizard-mega-x": "Mega Charizard X",
    "charizard-mega-y": "Mega Charizard Y",
    "mewtwo-mega-x": "Mega Mewtwo X",
    "mewtwo-mega-y": "Mega Mewtwo Y",
    "deoxys-normal": "Deoxys",
    "deoxys-attack": "Attack-Deoxys",
    "deoxys-defense": "Defense-Deoxys"
}

def aniname(name):
    return ANI_NAME_REPLACEMENTS.get(name, name)

def get_base_form(name):
    """Get the base form name for a Pokemon"""
    # Remove common form suffixes
    name = name.lower()
    suffixes = ['-mega', '-gmax', '-mega-x', '-mega-y', '-alola', '-galar', '-hisui']
    for suffix in suffixes:
        if name.endswith(suffix):
            return name.replace(suffix, '')
    return name

def format_display_name(name):
    # Check for mega forms first
    if "-mega" in name and name not in DISPLAY_NAME_REPLACEMENTS:
        base_name = name.replace("-mega", "")
        return "Mega " + capitalize_first_letter(base_name)
    
    # Otherwise use the replacements dictionary
    return DISPLAY_NAME_REPLACEMENTS.get(name, title_case(name))

# Type effectiveness data
TYPE_WEAKNESSES = {
    'normal': {'fighting': 2},
    'fire': {'water': 2, 'ground': 2, 'rock': 2},
    'water': {'electric': 2, 'grass': 2},
    'electric': {'ground': 2},
    'grass': {'fire': 2, 'ice': 2, 'poison': 2, 'flying': 2, 'bug': 2},
    'ice': {'fire': 2, 'fighting': 2, 'rock': 2, 'steel': 2},
    'fighting': {'flying': 2, 'psychic': 2, 'fairy': 2},
    'poison': {'ground': 2, 'psychic': 2},
    'ground': {'water': 2, 'grass': 2, 'ice': 2},
    'flying': {'electric': 2, 'ice': 2, 'rock': 2},
    'psychic': {'bug': 2, 'ghost': 2, 'dark': 2},
    'bug': {'fire': 2, 'flying': 2, 'rock': 2},
    'rock': {'water': 2, 'grass': 2, 'fighting': 2, 'ground': 2, 'steel': 2},
    'ghost': {'ghost': 2, 'dark': 2},
    'dragon': {'ice': 2, 'dragon': 2, 'fairy': 2},
    'steel': {'fire': 2, 'fighting': 2, 'ground': 2},
    'dark': {'fighting': 2, 'bug': 2, 'fairy': 2},
    'fairy': {'poison': 2, 'steel': 2}
}

TYPE_STRENGTHS = {
    'normal': {},
    'fire': {'grass': 2, 'ice': 2, 'bug': 2, 'steel': 2},
    'water': {'fire': 2, 'ground': 2, 'rock': 2},
    'electric': {'water': 2, 'flying': 2},
    'grass': {'water': 2, 'ground': 2, 'rock': 2},
    'ice': {'grass': 2, 'flying': 2, 'ground': 2, 'dragon': 2},
    'fighting': {'normal': 2, 'ice': 2, 'rock': 2, 'dark': 2, 'steel': 2},
    'poison': {'grass': 2, 'fairy': 2},
    'ground': {'fire': 2, 'electric': 2, 'poison': 2, 'rock': 2, 'steel': 2},
    'flying': {'grass': 2, 'fighting': 2, 'bug': 2},
    'psychic': {'fighting': 2, 'poison': 2},
    'bug': {'grass': 2, 'psychic': 2, 'dark': 2},
    'rock': {'fire': 2, 'ice': 2, 'flying': 2, 'bug': 2},
    'ghost': {'ghost': 2, 'psychic': 2},
    'dragon': {'dragon': 2},
    'steel': {'ice': 2, 'rock': 2, 'fairy': 2},
    'dark': {'ghost': 2, 'psychic': 2},
    'fairy': {'fighting': 2, 'dragon': 2, 'dark': 2}
}

# Remote moveset URLs are defined at the top of the file

# Cache for pokemon names
POKEMON_NAMES = []

# Load pokemon names from json file
def load_pokemon_names():
    global POKEMON_NAMES
    try:
        with open('pokemon.json', 'r') as f:
            pokemon_data = json.load(f)
        POKEMON_NAMES = [p['name'] for p in pokemon_data['pokemon']]
        return POKEMON_NAMES
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading Pokemon names: {e}")
        return []

# Data retrieval functions
async def fetch_pokemon_data(session, name):
    """Fetch Pokemon data from the API or database"""
    # Check database first
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT data, timestamp FROM pokemon_data WHERE name=?", (name,))
        row = cur.fetchone()
        
        # If data exists and is less than 7 days old, use it
        if row and (time.time() - row['timestamp'] < 7 * 24 * 60 * 60):
            print(f"Using cached data for {name}")
            return json.loads(row['data'])
    finally:
        conn.close()
    
    # If not in database or too old, fetch from API
    try:
        async with session.get(f"https://pokeapi.co/api/v2/pokemon/{name}") as response:
            if response.status != 200:
                raise HTTPException(status_code=404, detail=f"Pokemon {name} not found")
            
            data = await response.json()
            
            # Save to database
            conn = get_db_connection()
            try:
                cur = conn.cursor()
                cur.execute(
                    "INSERT OR REPLACE INTO pokemon_data (name, data, timestamp) VALUES (?, ?, ?)",
                    (name, json.dumps(data), int(time.time()))
                )
                conn.commit()
            finally:
                conn.close()
                
            return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch pokemon data: {str(e)}")

async def fetch_species_data(session, name):
    """Fetch Pokemon species data from the API or database"""
    # Check database first
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT data, timestamp FROM pokemon_species WHERE name=?", (name,))
        row = cur.fetchone()
        
        # If data exists and is less than 30 days old, use it
        if row and (time.time() - row['timestamp'] < 30 * 24 * 60 * 60):
            return json.loads(row['data'])
    finally:
        conn.close()
    
    # If not in database or too old, fetch from API
    try:
        async with session.get(f"https://pokeapi.co/api/v2/pokemon-species/{name}/") as response:
            if response.status != 200:
                raise HTTPException(status_code=404, detail=f"Pokemon species {name} not found")
            
            data = await response.json()
            
            # Save to database
            conn = get_db_connection()
            try:
                cur = conn.cursor()
                cur.execute(
                    "INSERT OR REPLACE INTO pokemon_species (name, data, timestamp) VALUES (?, ?, ?)",
                    (name, json.dumps(data), int(time.time()))
                )
                conn.commit()
            finally:
                conn.close()
                
            return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch species data: {str(e)}")

async def fetch_evolution_chain(session, chain_url):
    """Fetch evolution chain data from the API or database"""
    # Extract chain ID from URL
    chain_id = int(chain_url.split('/')[-2])
    
    # Check database first
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT data, timestamp FROM evolution_chains WHERE id=?", (chain_id,))
        row = cur.fetchone()
        
        # If data exists and is less than 30 days old, use it
        if row and (time.time() - row['timestamp'] < 30 * 24 * 60 * 60):
            return json.loads(row['data'])
    finally:
        conn.close()
    
    # If not in database or too old, fetch from API
    try:
        async with session.get(chain_url) as response:
            if response.status != 200:
                raise HTTPException(status_code=404, detail=f"Evolution chain {chain_id} not found")
            
            data = await response.json()
            
            # Save to database
            conn = get_db_connection()
            try:
                cur = conn.cursor()
                cur.execute(
                    "INSERT OR REPLACE INTO evolution_chains (id, data, timestamp) VALUES (?, ?, ?)",
                    (chain_id, json.dumps(data), int(time.time()))
                )
                conn.commit()
            finally:
                conn.close()
                
            return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch evolution chain: {str(e)}")

async def fetch_movesets(session, pokemon_name):
    """Fetch movesets for a Pokemon"""
    print(f"[DEBUG] Starting fetch_movesets for {pokemon_name}")
    conn = get_db_connection()
    movesets = []
    
    try:
        # Helper function to check database
        def check_db(name):
            cur = conn.cursor()
            cur.execute("SELECT data, timestamp FROM movesets WHERE pokemon_name=?", (name,))
            row = cur.fetchone()
            if row and (time.time() - row['timestamp'] < 30 * 24 * 60 * 60):
                print(f"[DEBUG] Found cached movesets for {name}")
                return json.loads(row['data'])
            print(f"[DEBUG] No cached movesets for {name}")
            return None
        
        # Try exact form first
        db_movesets = check_db(pokemon_name)
        if db_movesets:
            print(f"[DEBUG] Returning cached movesets for {pokemon_name}")
            return db_movesets
        
        # If no movesets found and this is a special form, try the base form
        base_form = get_base_form(pokemon_name)
        if base_form != pokemon_name:
            print(f"[DEBUG] Checking base form {base_form} for {pokemon_name}")
            db_movesets = check_db(base_form)
            if db_movesets:
                print(f"[DEBUG] Found movesets from base form {base_form}")
                # Save these movesets for the special form too
                cur = conn.cursor()
                cur.execute(
                    "INSERT OR REPLACE INTO movesets (pokemon_name, data, timestamp) VALUES (?, ?, ?)",
                    (pokemon_name, json.dumps(db_movesets), int(time.time()))
                )
                conn.commit()
                return db_movesets
        
        print(f"[DEBUG] Attempting to fetch movesets from PokeAPI for {pokemon_name}")
        # Try to get movesets from PokeAPI
        url = MOVESET_URLS[0]  # We only have one URL now
        movesets = await fetch_moveset_url(session, url, pokemon_name)
        
        if movesets:  # Valid movesets found
            print(f"[DEBUG] Got valid movesets from PokeAPI: {len(movesets)} sets")
            # Save movesets to database
            cur = conn.cursor()
            cur.execute(
                "INSERT OR REPLACE INTO movesets (pokemon_name, data, timestamp) VALUES (?, ?, ?)",
                (pokemon_name, json.dumps(movesets), int(time.time()))
            )
            conn.commit()
            return movesets
        else:
            print(f"[DEBUG] No valid movesets from PokeAPI")
    
    except Exception as e:
        print(f"[DEBUG] Error in fetch_movesets: {e}")
    finally:
        conn.close()
    
    print(f"[DEBUG] No movesets found for {pokemon_name}, returning empty list")
    return movesets or []

async def fetch_moveset_url(session, url, pokemon_name):
    """Fetch and parse a single moveset URL"""
    try:
        # Format the URL with the pokemon name
        formatted_url = url.format(pokemon=pokemon_name.lower())
        print(f"[DEBUG] Fetching moves from {formatted_url}")
        
        async with session.get(formatted_url) as response:
            if response.status != 200:
                print(f"[DEBUG] Error: HTTP {response.status} for {formatted_url}")
                return []
            
            print(f"[DEBUG] Got 200 response from {formatted_url}")
            data = await response.json()
            
            # Extract moves from the Pokemon's moveset
            if 'moves' in data:
                print(f"[DEBUG] Found 'moves' field in response with {len(data['moves'])} moves")
                # Print first move entry for debugging
                if data['moves']:
                    print(f"[DEBUG] Sample move entry: {json.dumps(data['moves'][0], indent=2)}")
                
                all_moves = []
                for move_entry in data['moves']:
                    try:
                        if isinstance(move_entry, dict) and 'move' in move_entry:
                            move_data = move_entry['move']
                            if isinstance(move_data, dict) and 'name' in move_data:
                                version_details = move_entry.get('version_group_details', [])
                                
                                # Skip if no version details
                                if not version_details:
                                    continue
                                    
                                # Get the latest version group detail
                                latest_version = version_details[-1]
                                
                                # Prioritize level-up moves from recent games
                                learn_method = latest_version.get('move_learn_method', {}).get('name', '')
                                version_name = latest_version.get('version_group', {}).get('name', '')
                                
                                # Only include moves from recent games (gen 6 onwards)
                                recent_versions = [
                                    'sword-shield', 'sun-moon', 'ultra-sun-ultra-moon',
                                    'x-y', 'omega-ruby-alpha-sapphire', 'scarlet-violet'
                                ]
                                if not any(v in version_name for v in recent_versions):
                                    continue
                                    
                                # Convert move name to title case and replace hyphens with spaces
                                move_name = move_data['name'].replace('-', ' ').title()
                                
                                # Add method info to help with sorting
                                move_info = {
                                    'name': move_name,
                                    'method': learn_method,
                                    'level': latest_version.get('level_learned_at', 0)
                                }
                                
                                print(f"[DEBUG] Processing move: {move_name} (Method: {learn_method}, Level: {move_info['level']})")
                                all_moves.append(move_info)
                            else:
                                print(f"[DEBUG] Invalid move data structure: {move_data}")
                        else:
                            print(f"[DEBUG] Invalid move entry structure: {move_entry}")
                    except Exception as e:
                        print(f"[DEBUG] Error processing move entry: {e}")
                        continue
                        
                # Group moves into themed sets
                movesets = []
                
                # Common move patterns
                physical_patterns = ['punch', 'claw', 'tackle', 'slam', 'cut', 'chop', 'bite', 'wing', 'scratch', 'pound', 'kick', 'dive', 'body slam']
                special_patterns = ['beam', 'pulse', 'blast', 'flare', 'flame', 'ember', 'wave', 'shock', 'thunder', 'ice', 'fire', 'water', 'surf', 'hydro', 'rain', 'origin']
                status_patterns = ['dance', 'growl', 'screech', 'roar', 'smoke', 'rage', 'leer', 'howl', 'sharpen', 'defense', 'calm', 'rest', 'protect']
                
                # Sort moves by level and method
                level_up_moves = [m for m in all_moves if m['method'] == 'level-up']
                level_up_moves.sort(key=lambda x: x['level'])
                
                other_moves = [m for m in all_moves if m['method'] != 'level-up']
                
                # Combine and take only names
                all_move_names = [m['name'] for m in level_up_moves + other_moves]
                
                # Group moves
                physical_moves = [m for m in all_move_names if any(t in m.lower() for t in physical_patterns)]
                special_moves = [m for m in all_move_names if any(t in m.lower() for t in special_patterns)]
                status_moves = [m for m in all_move_names if any(t in m.lower() for t in status_patterns)]
                
                print(f"[DEBUG] Grouped moves - Physical: {len(physical_moves)}, Special: {len(special_moves)}, Status: {len(status_moves)}")
                
                # Create themed movesets (prioritizing level-up moves)
                if physical_moves:
                    movesets.append({
                        "name": "Physical Attacks",
                        "moves": physical_moves[:4]
                    })
                if special_moves:
                    movesets.append({
                        "name": "Special Attacks",
                        "moves": special_moves[:4]
                    })
                if status_moves:
                    movesets.append({
                        "name": "Status Moves",
                        "moves": status_moves[:4]
                    })
                
                # Add remaining moves as a generic set
                remaining_moves = [m for m in all_move_names if m not in (physical_moves + special_moves + status_moves)]
                if remaining_moves:
                    movesets.append({
                        "name": "Other Moves",
                        "moves": remaining_moves[:4]
                    })
                
                print(f"[DEBUG] Created {len(movesets)} movesets")
                return movesets
            else:
                print(f"[DEBUG] No 'moves' field found in response for {pokemon_name}")
                print(f"[DEBUG] Response data keys: {list(data.keys())}")
                return []
    except Exception as e:
        print(f"[DEBUG] Error fetching {formatted_url}: {str(e)}")
        import traceback
        print(f"[DEBUG] Traceback: {traceback.format_exc()}")
        return []

def extract_evolution_names(evolution):
    """Extract all evolution names from the chain recursively"""
    names = [evolution['species']['name']]
    for evolve_to in evolution['evolves_to']:
        names.extend(extract_evolution_names(evolve_to))
    return names

def check_processed_cache(name):
    """Check if we have a processed response cached for this pokemon"""
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT data, timestamp FROM processed_pokemon WHERE name=?", (name,))
        row = cur.fetchone()
        
        # If data exists and is less than 1 day old, use it
        if row and (time.time() - row['timestamp'] < 24 * 60 * 60):
            print(f"Using processed cache for {name}")
            return json.loads(row['data'])
        return None
    finally:
        conn.close()

def save_processed_data(name, data):
    """Save processed pokemon data to cache"""
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT OR REPLACE INTO processed_pokemon (name, data, timestamp) VALUES (?, ?, ?)",
            (name, json.dumps(data), int(time.time()))
        )
        conn.commit()
    finally:
        conn.close()

# API endpoints
@app.get("/alive/")
async def alive():
    print("I have been checked")
    return "I'm alive"

@app.get("/info/{name}")
async def info(name: str):
    print(f"Request received for: {name}")
    
    # Make sure Pokemon names are loaded
    if not POKEMON_NAMES:
        load_pokemon_names()
    
    if not POKEMON_NAMES:
        raise HTTPException(status_code=500, detail="Failed to load Pokemon names")
    
    # Find best match
    best_match = get_close_matches(name, POKEMON_NAMES, n=1, cutoff=0.6)
    if not best_match:
        raise HTTPException(status_code=404, detail="No close match found for the given name.")
    
    best_match = best_match[0]
    print(f"Best match found: {best_match}")
    
    # Check if we already have processed data cached
    cached_data = check_processed_cache(best_match)
    if cached_data:
        return cached_data
    
    # If not cached, fetch and process the data
    async with aiohttp.ClientSession() as session:
        # Fetch the main pokemon data
        pokemon_data = await fetch_pokemon_data(session, best_match)
        
        # Start async tasks for additional data
        species_task = fetch_species_data(session, pokemon_data['species']['name'])
        movesets_task = fetch_movesets(session, best_match)
        
        # Process pokemon data while waiting for other requests
        weight = pokemon_data['weight'] / 10
        height = pokemon_data['height'] / 10
        type_str = '\n'.join(capitalize_first_letter(t['type']['name']) for t in pokemon_data['types'])
        
        # Stats
        stat_data = {stat['stat']['name']: stat['base_stat'] for stat in pokemon_data['stats']}
        
        # Abilities
        abilities = [capitalize_first_letter(ability['ability']['name']) for ability in pokemon_data['abilities']]
        
        # Type effectiveness
        type_names = [t['type']['name'] for t in pokemon_data['types']]
        weaknesses = {}
        strengths = {}
        
        for type_name in type_names:
            try:
                weaknesses.update(TYPE_WEAKNESSES.get(type_name, {}))
                strengths.update(TYPE_STRENGTHS.get(type_name, {}))
            except Exception as e:
                print(f"Error processing type effectiveness: {e}")
        
        strong = list(strengths.keys())
        weakness = list(weaknesses.keys())
        
        # Get species data and evolution chain
        species_data = await species_task
        evolution_chain_url = species_data['evolution_chain']['url']
        evolution_chain_data = await fetch_evolution_chain(session, evolution_chain_url)
        
        # Process evolution chain
        chain = evolution_chain_data['chain']
        evolution_names = extract_evolution_names(chain)
        evo_chain = [title_case(name) for name in evolution_names]
        
        # Process forms
        varieties = species_data['varieties']
        forms = [title_case(v['pokemon']['name']) for v in varieties]
        
        # Get movesets
        print(f"[DEBUG] Waiting for movesets task to complete for {best_match}...")
        movesets = await movesets_task
        print(f"[DEBUG] Got movesets for {best_match}: {len(movesets)} sets")
        
        # Construct the final response
        response_data = {
            "name": title_case(format_display_name(pokemon_data['name'])),
            "id": pokemon_data['id'],
            "details": {
                "type": type_str,
                "weight": weight,
                "height": height,
                "preview": pokemon_data['sprites']['other']['official-artwork']['front_default'],
                "animated": f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/versions/generation-v/black-white/animated/{pokemon_data['id']}.gif"
            },
            "evolution": {
                "chain": evo_chain,
                "forms": forms
            },
            "stats": stat_data,
            "abilities": abilities,
            "movesets": movesets,
            "effectiveness": {
                "strong_against": strong,
                "weak_against": weakness
            }
        }
        
        # Save processed data to cache
        save_processed_data(best_match, response_data)
        
        return response_data

@app.on_event("startup")
async def startup_event():
    # Initialize database
    initialize_database()
    # Load Pokemon names
    load_pokemon_names()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
