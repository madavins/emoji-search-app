import json
import numpy as np
import os
from sentence_transformers import SentenceTransformer

INPUT_DATA_FILE = "data/emoji_data.json"
OUTPUT_DIR = "data"
EMBEDDINGS_OUTPUT_FILE = os.path.join(OUTPUT_DIR, "emoji_embeddings.npy")
EMBEDDING_MODEL = 'all-MiniLM-L6-v2' # lightweight, fast and performant model

def create_embeddings():
    """
    Loads emoji data, generates and saves sentence embeddings for descriptions.
    """
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Load emoji data
    try:
        with open(INPUT_DATA_FILE, 'r', encoding='utf-8') as f: # use utf-8 encoding to handle emojis
            emoji_data = json.load(f)
    except FileNotFoundError:
        print(f"Error: Input file not found at {INPUT_DATA_FILE}")
        print("Please run scripts/prepare_emoji_data.py first.")
        return
    except Exception as e:
        print(f"An unexpected error occurred loading data: {e}")
        return

    if not emoji_data:
        print("Error: No data loaded.")
        return

    descriptions = [item['description'] for item in emoji_data] 
    print(f"Loading Transformer model: {EMBEDDING_MODEL}...")
    
    try:
        model = SentenceTransformer(EMBEDDING_MODEL)
    except Exception as e:
        print(f"Error loading sentence transformer model: {e}")
        return

    # Create and save embeddings
    try:
        embeddings = model.encode(descriptions, show_progress_bar=True, convert_to_numpy=True)
        print(f"Shape of embeddings array: {embeddings.shape}")
        
        np.save(EMBEDDINGS_OUTPUT_FILE, embeddings)
        print(f"Embeddings saved to {EMBEDDINGS_OUTPUT_FILE}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    create_embeddings()
