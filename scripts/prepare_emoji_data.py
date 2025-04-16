import emoji
import json
import os
import re

OUTPUT_DIR = "data"
DATA_OUTPUT_FILE = os.path.join(OUTPUT_DIR, "emoji_data.json")

def create_emoji_data():
    """
    Extracts emojis and their English descriptions using the emoji library,
    processes the descriptions, and saves them into a JSON.
    """
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    emoji_data = [] 
    
    for char, data in emoji.EMOJI_DATA.items():
        if 'en' in data:
            # Emoji names originally formated as: :woman_elf_dark_skin_tone:
            # so we need to remove colons and replace underscores with spaces
            name_no_colons = data['en'].strip(':') 
            processed_name = re.sub(r'_+', ' ', name_no_colons).strip()
            emoji_instance = {
                "emoji": char,
                "description": processed_name 
            }
            emoji_data.append(emoji_instance)
    
    try:
        with open(DATA_OUTPUT_FILE, 'w', encoding='utf-8') as f_data: # use utf-8 encoding to handle emojis
            json.dump(emoji_data, f_data, ensure_ascii=False, indent=4) # ensure_ascii=False to keep emojis
            
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    create_emoji_data()