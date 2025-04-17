# Emoji Semantic Search App

Search for emojis using natural language. Built with FastAPI & SentenceTransformers.

<img width="600" alt="App screenshot" src="https://github.com/user-attachments/assets/b8a23585-839c-4140-af11-74f330538ea9" />

## Setup

1.  **Clone:** `git clone github.com/madavins/emoji-search-app`
2.  **Install:** `cd emoji-search-app && pip install -r requirements.txt`
3.  **Process data & generate embeddings:**
    ```bash
    # 1. Extract descriptions -> data/emoji_data.json
    python scripts/prepare_emoji_data.py

    # 2. Create embeddings -> data/emoji_embeddings.npy
    python scripts/generate_embeddings.py
    ```

## Run

1.  **Start Server:** `uvicorn app.main:app --reload`
2.  **Open:** `http://127.0.0.1:8000` in your browser.
3.  **Search:** Type a description (e.g., "happy face", "sad cat") and press Enter. Click emojis to copy.