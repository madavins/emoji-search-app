from pydantic import BaseModel, Field
from typing import List

class SearchResultItem(BaseModel):
    emoji: str = Field(..., description="Emoji.")
    score: float = Field(..., description="Similarity score (higher is better).", ge=0.0, le=1.0) 

class SearchResponse(BaseModel):
    results: List[SearchResultItem] = Field(..., description="A list of ranked emoji search results.")