from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import os
from contextlib import asynccontextmanager 
import numpy as np 
from sklearn.metrics.pairwise import cosine_similarity 

from .models import *
from .ml_utils import * 

STATIC_DIR = "static"
TOP_N_RESULTS = 10

# --- Lifespan context manager ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    
    print("Application startup...")
    if not load_models():
        print("FATAL: ML Models or data failed to load.")
        raise RuntimeError("Application startup aborted: Failed to load ML models.")
    print("ML Models loaded successfully.")

    yield

    print("Application shutdown...")
    ml_assets.clear()


app = FastAPI(
    title="Emoji semantic search API",
    description="Use this API to find relevant emojis based on text descriptions using semantic search.",
    lifespan=lifespan, 
)

# --- Mount static files ---
if os.path.isdir(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
else:
    print(f"Warning: Static directory '{STATIC_DIR}' not found. Frontend will not be served.")


# --- API endpoints ---
@app.get("/", response_class=FileResponse, tags=["Frontend"])
async def read_index():
    """Serves index.html page."""
    html_file_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(html_file_path):
        return FileResponse(html_file_path)
    else:
        print(f"Error: {html_file_path} not found.")
        raise HTTPException(status_code=404, detail="Index file not found.")


@app.get("/search", response_model=SearchResponse, tags=["Search"]) 
async def search_emoji(q: str | None = None): 
    """
    Searches for emojis based on the provided query string 'q'.
    """
    model = get_model()
    all_embeddings = get_embeddings()
    emoji_list = get_emoji_list()

    if not q:
        return SearchResponse(results=[]) # if no query, return empty results
    
    try:
        query_embedding = model.encode([q], convert_to_numpy=True) # extract embedding from query
        similarities = cosine_similarity(query_embedding, all_embeddings)[0] 

        # Using argpartition instead of full sort for efficiency
        top_n_indices = np.argpartition(similarities, -TOP_N_RESULTS)[-TOP_N_RESULTS:] # indices of top N results (not sorted)
        sorted_top_n_indices = sorted(top_n_indices, key=lambda i: similarities[i], reverse=True) # don't sort indices, but sort the values

        results = []
        for index in sorted_top_n_indices:
            score = float(np.clip(similarities[index], 0.0, 1.0)) # clip to handle precision error
            results.append(SearchResultItem(emoji=emoji_list[index], score=score))

        return SearchResponse(results=results)

    except Exception as e:
        print(f"Error during search for query '{q}': {e}")
        raise HTTPException(status_code=500, detail="An error occurred during the search process.")
