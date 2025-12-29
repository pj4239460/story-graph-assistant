"""
Vector Database Infrastructure using FAISS
"""
from __future__ import annotations
from typing import List, Dict
from pathlib import Path
import json
import numpy as np


class VectorDatabase:
    """Vector database for semantic search using FAISS"""
    
    def __init__(self, persist_directory: str = ".vectordb"):
        """Initialize FAISS-based vector database with persistence"""
        self.persist_directory = Path(persist_directory)
        self.persist_directory.mkdir(parents=True, exist_ok=True)
        
        # Lazy import to avoid loading heavy dependencies at startup
        try:
            import faiss
            from sentence_transformers import SentenceTransformer
            
            self._faiss = faiss
            self._available = True
            
            # Initialize embedding model (using a multilingual model for Chinese support)
            print("Loading embedding model...")
            self.embedding_model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
            print("Embedding model loaded.")
            
            # Store for project-specific indices and metadata
            self.indices = {}  # project_id_type -> faiss.Index
            self.metadata = {}  # project_id_type -> {id: {doc, metadata}}
            
            # Load existing indices
            self._load_all_indices()
            
            print("✓ Vector database initialized successfully (FAISS)")
            
        except Exception as e:
            print(f"WARNING: Vector database not available: {e}")
            print("Falling back to keyword search. To enable semantic search, install: pip install faiss-cpu sentence-transformers")
            self._available = False
            self.embedding_model = None
    
    def is_available(self) -> bool:
        """Check if vector database is available"""
        return self._available
    
    def _get_index_path(self, project_id: str, collection_type: str) -> Path:
        """Get file path for index"""
        safe_name = f"{project_id}_{collection_type}".replace("-", "_").replace(".", "_")[:63]
        return self.persist_directory / f"{safe_name}.index"
    
    def _get_metadata_path(self, project_id: str, collection_type: str) -> Path:
        """Get file path for metadata"""
        safe_name = f"{project_id}_{collection_type}".replace("-", "_").replace(".", "_")[:63]
        return self.persist_directory / f"{safe_name}.meta.json"
    
    def _load_all_indices(self):
        """Load all existing indices from disk"""
        for index_file in self.persist_directory.glob("*.index"):
            try:
                index = self._faiss.read_index(str(index_file))
                key = index_file.stem  # filename without .index
                self.indices[key] = index
                
                # Load corresponding metadata
                meta_file = index_file.parent / f"{key}.meta.json"
                if meta_file.exists():
                    with open(meta_file, 'r', encoding='utf-8') as f:
                        self.metadata[key] = json.load(f)
                else:
                    self.metadata[key] = {}
                    
                print(f"  Loaded index: {key} ({index.ntotal} vectors)")
            except Exception as e:
                print(f"  Warning: Failed to load index {index_file}: {e}")
    
    def _get_or_create_index(self, project_id: str, collection_type: str):
        """Get or create a FAISS index for a project collection"""
        key = f"{project_id}_{collection_type}".replace("-", "_").replace(".", "_")[:63]
        
        if key not in self.indices:
            # Create new index (384 dimensions for paraphrase-multilingual-MiniLM-L12-v2)
            dimension = 384
            self.indices[key] = self._faiss.IndexFlatL2(dimension)
            self.metadata[key] = {}
            
        return key
    
    def _save_index(self, key: str):
        """Save index and metadata to disk"""
        if key not in self.indices:
            return
            
        try:
            # Extract project_id and collection_type from key
            parts = key.rsplit('_', 1)
            if len(parts) == 2:
                project_id = parts[0]
                collection_type = parts[1]
            else:
                # Fallback: use key as is
                project_id = key
                collection_type = "default"
            
            # Save FAISS index
            index_path = self._get_index_path(project_id, collection_type)
            self._faiss.write_index(self.indices[key], str(index_path))
            
            # Save metadata
            meta_path = self._get_metadata_path(project_id, collection_type)
            with open(meta_path, 'w', encoding='utf-8') as f:
                json.dump(self.metadata[key], f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            print(f"Warning: Failed to save index {key}: {e}")
    
    def embed_text(self, text: str) -> np.ndarray:
        """Generate embedding for text"""
        if not self._available:
            return np.array([])
        embedding = self.embedding_model.encode(text, convert_to_numpy=True)
        return embedding
    
    def index_character(self, project_id: str, char_id: str, char_data: Dict):
        """Index a character for semantic search"""
        if not self._available:
            return
        
        try:
            key = self._get_or_create_index(project_id, "characters")
            
            # Build searchable text from character data
            text_parts = [
                f"Name: {char_data['name']}",
                f"Description: {char_data.get('description', '')}",
            ]
            
            if char_data.get('alias'):
                text_parts.append(f"Alias: {char_data['alias']}")
            
            if char_data.get('traits'):
                text_parts.append(f"Traits: {', '.join(char_data['traits'])}")
            
            if char_data.get('goals'):
                text_parts.append(f"Goals: {', '.join(char_data['goals'])}")
                
            if char_data.get('fears'):
                text_parts.append(f"Fears: {', '.join(char_data['fears'])}")
            
            searchable_text = "\n".join(text_parts)
            
            # Generate embedding
            embedding = self.embed_text(searchable_text)
            
            # Add to FAISS index
            self.indices[key].add(np.array([embedding], dtype=np.float32))
            
            # Store metadata
            internal_id = self.indices[key].ntotal - 1  # Last added vector
            self.metadata[key][str(internal_id)] = {
                "id": char_id,
                "document": searchable_text,
                "name": char_data['name'],
                "type": "character"
            }
            
            # Save to disk
            self._save_index(key)
            
        except Exception as e:
            print(f"ERROR indexing character {char_id}: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    def index_scene(self, project_id: str, scene_id: str, scene_data: Dict):
        """Index a scene for semantic search"""
        if not self._available:
            return
        
        try:
            key = self._get_or_create_index(project_id, "scenes")
            
            # Build searchable text from scene data
            text_parts = [
                f"Title: {scene_data['title']}",
            ]
            
            if scene_data.get('chapter'):
                text_parts.append(f"Chapter: {scene_data['chapter']}")
            
            if scene_data.get('summary'):
                text_parts.append(f"Summary: {scene_data['summary']}")
            elif scene_data.get('body'):
                # Use first 500 chars of body if no summary
                preview = scene_data['body'][:500]
                text_parts.append(f"Content: {preview}")
            
            if scene_data.get('tags'):
                text_parts.append(f"Tags: {', '.join(scene_data['tags'])}")
            
            searchable_text = "\n".join(text_parts)
            
            # Generate embedding
            embedding = self.embed_text(searchable_text)
            
            # Add to FAISS index
            self.indices[key].add(np.array([embedding], dtype=np.float32))
            
            # Store metadata
            internal_id = self.indices[key].ntotal - 1
            self.metadata[key][str(internal_id)] = {
                "id": scene_id,
                "document": searchable_text,
                "title": scene_data['title'],
                "type": "scene"
            }
            
            # Save to disk
            self._save_index(key)
            
        except Exception as e:
            print(f"ERROR indexing scene {scene_id}: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    def search_characters(self, project_id: str, query: str, top_k: int = 3) -> List[Dict]:
        """Search for relevant characters using semantic similarity"""
        if not self._available:
            return []
            
        try:
            key = f"{project_id}_characters".replace("-", "_").replace(".", "_")[:63]
            
            if key not in self.indices or self.indices[key].ntotal == 0:
                return []
            
            # Generate query embedding
            query_embedding = self.embed_text(query)
            
            # Search in FAISS
            k = min(top_k, self.indices[key].ntotal)
            distances, indices = self.indices[key].search(np.array([query_embedding], dtype=np.float32), k)
            
            # Format results
            characters = []
            for i, idx in enumerate(indices[0]):
                if idx >= 0 and str(idx) in self.metadata[key]:
                    meta = self.metadata[key][str(idx)]
                    characters.append({
                        "id": meta['id'],
                        "name": meta['name'],
                        "distance": float(distances[0][i]),
                        "document": meta['document']
                    })
            
            return characters
        except Exception as e:
            print(f"Error searching characters: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def search_scenes(self, project_id: str, query: str, top_k: int = 3) -> List[Dict]:
        """Search for relevant scenes using semantic similarity"""
        if not self._available:
            return []
            
        try:
            key = f"{project_id}_scenes".replace("-", "_").replace(".", "_")[:63]
            
            if key not in self.indices or self.indices[key].ntotal == 0:
                return []
            
            # Generate query embedding
            query_embedding = self.embed_text(query)
            
            # Search in FAISS
            k = min(top_k, self.indices[key].ntotal)
            distances, indices = self.indices[key].search(np.array([query_embedding], dtype=np.float32), k)
            
            # Format results
            scenes = []
            for i, idx in enumerate(indices[0]):
                if idx >= 0 and str(idx) in self.metadata[key]:
                    meta = self.metadata[key][str(idx)]
                    scenes.append({
                        "id": meta['id'],
                        "title": meta['title'],
                        "distance": float(distances[0][i]),
                        "document": meta['document']
                    })
            
            return scenes
        except Exception as e:
            print(f"Error searching scenes: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def delete_character(self, project_id: str, char_id: str):
        """Remove a character from the index
        Note: FAISS doesn't support direct deletion, would need to rebuild index"""
        print(f"Warning: FAISS doesn't support direct deletion. Character {char_id} remains in index.")
    
    def delete_scene(self, project_id: str, scene_id: str):
        """Remove a scene from the index
        Note: FAISS doesn't support direct deletion, would need to rebuild index"""
        print(f"Warning: FAISS doesn't support direct deletion. Scene {scene_id} remains in index.")
    
    def clear_project(self, project_id: str):
        """Clear all indexed data for a project"""
        try:
            # Delete character index
            char_key = f"{project_id}_characters".replace("-", "_").replace(".", "_")[:63]
            if char_key in self.indices:
                del self.indices[char_key]
                del self.metadata[char_key]
                
                index_path = self._get_index_path(project_id, "characters")
                meta_path = self._get_metadata_path(project_id, "characters")
                
                if index_path.exists():
                    index_path.unlink()
                if meta_path.exists():
                    meta_path.unlink()
            
            # Delete scene index
            scene_key = f"{project_id}_scenes".replace("-", "_").replace(".", "_")[:63]
            if scene_key in self.indices:
                del self.indices[scene_key]
                del self.metadata[scene_key]
                
                index_path = self._get_index_path(project_id, "scenes")
                meta_path = self._get_metadata_path(project_id, "scenes")
                
                if index_path.exists():
                    index_path.unlink()
                if meta_path.exists():
                    meta_path.unlink()
                    
        except Exception as e:
            print(f"Error clearing project: {e}")
