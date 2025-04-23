from sentence_transformers import SentenceTransformer
import numpy as np
import json
import os

EMBEDDING_MODEL = 'all-MiniLM-L6-v2'
EMBEDDINGS_PATH = "data/emoji_embeddings_augmented.npy"
EMOJI_DATA_PATH = "data/emoji_data_augmented.json"

ml_assets = {}

def load_models():
    """Loads the Sentence Transformer model, embeddings, and emoji list."""
    print("Loading ML models and data...")
    if not os.path.exists(EMBEDDINGS_PATH) or not os.path.exists(EMOJI_DATA_PATH):
        print("Error: Embeddings or emoji list file not found.")
        print("Please ensure 'scripts/create_index.py' was run successfully.")
        return False
        
    try:
        ml_assets['model'] = SentenceTransformer(EMBEDDING_MODEL)
        ml_assets['embeddings'] = np.load(EMBEDDINGS_PATH)
        
        with open(EMOJI_DATA_PATH, 'r', encoding='utf-8') as f: # use 'utf-8' encoding to handle emojis
            emoji_data = json.load(f)
            ml_assets['emoji_list'] = [item['emoji'] for item in emoji_data]
            
        if len(ml_assets['emoji_list']) != ml_assets['embeddings'].shape[0]:
            print("Error: Mismatch between loaded emoji list length and embeddings dimensions.")
            ml_assets.clear() 
            return False
            
        print(f"Successfully loaded model and data: {len(ml_assets['emoji_list'])} emojis")
        return True
        
    except Exception as e:
        print(f"An error occurred during model/data loading: {e}")
        ml_assets.clear()
        return False

def get_model():
    return ml_assets.get('model')

def get_embeddings():
    return ml_assets.get('embeddings')

def get_emoji_list():
    return ml_assets.get('emoji_list')