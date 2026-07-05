import chromadb
from chromadb.utils import embedding_functions
import os
from typing import List

class RAGSystem:
    def __init__(self):
        self.client = chromadb.PersistentClient(path="./chroma_db")
        
        self.embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )
        
        self.style_collection = self.client.get_or_create_collection(
            name="style_guides",
            embedding_function=self.embedding_fn
        )
        self.api_collection = self.client.get_or_create_collection(
            name="remotion_api",
            embedding_function=self.embedding_fn
        )
        
        self._seed_documents()
    
    def _seed_documents(self):
        try:
            self.style_collection.delete(ids=[str(i) for i in range(10)])
            self.api_collection.delete(ids=[str(i) for i in range(10)])
        except:
            pass
        
        style_docs = [
            {
                "id": "cinematic",
                "content": "CINEMATIC STYLE: Slow pacing with 3-4 seconds per scene. Use warm golden tones. Smooth cross-fade transitions. Emotional captions with poetic language.",
                "metadata": {"style": "cinematic"}
            },
            {
                "id": "upbeat",
                "content": "UPBEAT STYLE: Fast pacing with 1-2 seconds per scene. Bright vibrant colors. Dynamic cut transitions. Energetic captions with emojis.",
                "metadata": {"style": "upbeat"}
            },
            {
                "id": "corporate",
                "content": "CORPORATE STYLE: Moderate pacing with 2-3 seconds per scene. Clean professional look. Subtle fade transitions. Concise professional captions.",
                "metadata": {"style": "corporate"}
            }
        ]
        
        for doc in style_docs:
            self.style_collection.add(
                documents=[doc["content"]],
                ids=[doc["id"]],
                metadatas=[doc["metadata"]]
            )
        
        api_docs = [
            {
                "id": "sequence",
                "content": "import { Sequence, useCurrentFrame } from 'remotion';"
            },
            {
                "id": "interpolation",
                "content": "import { interpolate } from 'remotion';"
            },
            {
                "id": "spring",
                "content": "import { spring } from 'remotion';"
            }
        ]
        
        for doc in api_docs:
            self.api_collection.add(
                documents=[doc["content"]],
                ids=[doc["id"]]
            )
    
    def retrieve_style(self, intent_str: str, k: int = 1) -> str:
        results = self.style_collection.query(
            query_texts=[intent_str],
            n_results=k
        )
        if results['documents'] and len(results['documents'][0]) > 0:
            return results['documents'][0][0]
        return ""
    
    def retrieve_api(self, query: str, k: int = 2) -> List[str]:
        results = self.api_collection.query(
            query_texts=[query],
            n_results=k
        )
        if results['documents'] and len(results['documents'][0]) > 0:
            return results['documents'][0]
        return []