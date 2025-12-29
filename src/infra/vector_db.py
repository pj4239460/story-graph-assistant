"""
Vector Database Infrastructure using ChromaDB
"""
from __future__ import annotations
from typing import List, Dict, Optional
from pathlib import Path


class VectorDatabase:
    """Vector database for semantic search using ChromaDB"""
    
    def __init__(self, persist_directory: str = ".chromadb"):
        """Initialize ChromaDB with persistence"""
        self.persist_directory = persist_directory
        Path(persist_directory).mkdir(parents=True, exist_ok=True)
        
        # Lazy import to avoid loading heavy dependencies at startup
        try:
            import chromadb
            from sentence_transformers import SentenceTransformer
            
            self._chromadb = chromadb
            self._available = True
            
            # Initialize ChromaDB client with persistence (simplified for v1.4+)
            self.client = chromadb.PersistentClient(path=persist_directory)
            
            # Initialize embedding model (using a multilingual model for Chinese support)
            print("Loading embedding model...")
            self.embedding_model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
            print("Embedding model loaded.")
            print("✓ Vector database initialized successfully")
            
        except Exception as e:
            print(f"WARNING: Vector database not available: {e}")
            print("Falling back to keyword search. To enable semantic search, install: pip install chromadb sentence-transformers torch")
            self._available = False
            self.client = None
            self.embedding_model = None
    
    def is_available(self) -> bool:
        """Check if vector database is available"""
        return self._available
        
    def get_or_create_collection(self, project_id: str, collection_type: str):
        """Get or create a collection for a project
        
        Args:
            project_id: Unique project identifier
            collection_type: 'characters' or 'scenes'
        """
        if not self._available:
            return None
            
        collection_name = f"{project_id}_{collection_type}"
        # Sanitize collection name (ChromaDB requirements)
        collection_name = collection_name.replace("-", "_").replace(".", "_")[:63]
        
        try:
            collection = self.client.get_collection(name=collection_name)
        except:
            collection = self.client.create_collection(
                name=collection_name,
                metadata={"project_id": project_id, "type": collection_type}
            )
        
        return collection
    
    def embed_text(self, text: str) -> List[float]:
        """Generate embedding for text"""
        if not self._available:
            return []
        embedding = self.embedding_model.encode(text, convert_to_numpy=True)
        return embedding.tolist()
    
    def index_character(self, project_id: str, char_id: str, char_data: Dict):
        """Index a character for semantic search"""
        if not self._available:
            return
        
        try:
            print(f"    Getting collection for project {project_id}...")
            collection = self.get_or_create_collection(project_id, "characters")
            
            print(f"    Building searchable text...")
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
            print(f"    Text length: {len(searchable_text)} chars")
            
            # Generate embedding
            print(f"    Generating embedding...")
            embedding = self.embed_text(searchable_text)
            print(f"    Embedding dimension: {len(embedding)}")
            
            # Upsert to collection
            print(f"    Upserting to ChromaDB...")
            collection.upsert(
                ids=[char_id],
                embeddings=[embedding],
                documents=[searchable_text],
                metadatas=[{
                    "name": char_data['name'],
                    "type": "character"
                }]
            )
            print(f"    Successfully indexed character")
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
            collection = self.get_or_create_collection(project_id, "scenes")
            
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
            
            # Upsert to collection
            collection.upsert(
                ids=[scene_id],
                embeddings=[embedding],
                documents=[searchable_text],
                metadatas=[{
                    "title": scene_data['title'],
                    "type": "scene"
                }]
            )
        except Exception as e:
            print(f"Error indexing scene {scene_id}: {e}")
            raise
    
    def search_characters(self, project_id: str, query: str, top_k: int = 3) -> List[Dict]:
        """Search for relevant characters using semantic similarity"""
        if not self._available:
            return []
            
        try:
            collection = self.get_or_create_collection(project_id, "characters")
            
            # Check if collection is empty
            if collection.count() == 0:
                return []
            
            # Generate query embedding
            query_embedding = self.embed_text(query)
            
            # Search
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=min(top_k, collection.count())
            )
            
            # Format results
            characters = []
            if results['ids'] and len(results['ids'][0]) > 0:
                for i, char_id in enumerate(results['ids'][0]):
                    characters.append({
                        "id": char_id,
                        "name": results['metadatas'][0][i]['name'],
                        "distance": results['distances'][0][i] if 'distances' in results else 0,
                        "document": results['documents'][0][i]
                    })
            
            return characters
        except Exception as e:
            print(f"Error searching characters: {e}")
            return []
    
    def search_scenes(self, project_id: str, query: str, top_k: int = 3) -> List[Dict]:
        """Search for relevant scenes using semantic similarity"""
        if not self._available:
            return []
            
        try:
            collection = self.get_or_create_collection(project_id, "scenes")
            
            # Check if collection is empty
            if collection.count() == 0:
                return []
            
            # Generate query embedding
            query_embedding = self.embed_text(query)
            
            # Search
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=min(top_k, collection.count())
            )
            
            # Format results
            scenes = []
            if results['ids'] and len(results['ids'][0]) > 0:
                for i, scene_id in enumerate(results['ids'][0]):
                    scenes.append({
                        "id": scene_id,
                        "title": results['metadatas'][0][i]['title'],
                        "distance": results['distances'][0][i] if 'distances' in results else 0,
                        "document": results['documents'][0][i]
                    })
            
            return scenes
        except Exception as e:
            print(f"Error searching scenes: {e}")
            return []
    
    def delete_character(self, project_id: str, char_id: str):
        """Remove a character from the index"""
        try:
            collection = self.get_or_create_collection(project_id, "characters")
            collection.delete(ids=[char_id])
        except Exception as e:
            print(f"Error deleting character: {e}")
    
    def delete_scene(self, project_id: str, scene_id: str):
        """Remove a scene from the index"""
        try:
            collection = self.get_or_create_collection(project_id, "scenes")
            collection.delete(ids=[scene_id])
        except Exception as e:
            print(f"Error deleting scene: {e}")
    
    def clear_project(self, project_id: str):
        """Clear all indexed data for a project"""
        try:
            # Delete character collection
            char_collection_name = f"{project_id}_characters".replace("-", "_").replace(".", "_")[:63]
            try:
                self.client.delete_collection(name=char_collection_name)
            except:
                pass
            
            # Delete scene collection
            scene_collection_name = f"{project_id}_scenes".replace("-", "_").replace(".", "_")[:63]
            try:
                self.client.delete_collection(name=scene_collection_name)
            except:
                pass
        except Exception as e:
            print(f"Error clearing project: {e}")
