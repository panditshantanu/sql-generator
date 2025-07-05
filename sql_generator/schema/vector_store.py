import chromadb
from typing import List, Dict, Any, Optional, Union
import numpy as np
import sys
from pathlib import Path
import logging

# Add parent directory to path for imports
current_dir = Path(__file__).parent
parent_dir = current_dir.parent
sys.path.insert(0, str(current_dir))
sys.path.insert(0, str(parent_dir))

try:
    from ..utils.config_manager import get_config
except ImportError:
    # Handle direct execution or path issues
    try:
        from sql_generator.utils.config_manager import get_config
    except ImportError:
        # Fallback
        sys.path.insert(0, str(parent_dir))
        try:
            from sql_generator.utils.config_manager import get_config
        except ImportError:
            def get_config():
                return {
                    "vector_store": {"persist_dir": "./data/chroma_db", "verbose": True},
                    "embeddings": {"model_name": "all-MiniLM-L6-v2"}
                }


class VectorStore:
    """Manages vector storage operations using ChromaDB for schema embeddings."""
    
    def __init__(self, persist_dir: Optional[str] = None, verbose: Optional[bool] = None):
        """
        Initialize the vector store.
        
        Args:
            persist_dir: Directory path for persistent storage (overrides config)
            verbose: Whether to print status messages (overrides config)
        """
        self.config = get_config()
        
        # Use provided values or fall back to config
        if persist_dir is not None:
            self.persist_dir = Path(persist_dir)
        else:
            self.persist_dir = Path(self.config.get_chroma_path())
            
        if verbose is not None:
            self.verbose = verbose
        else:
            self.verbose = self.config.get("vector_store.verbose", True)
            
        self._client = None
        
        # Create directory if it doesn't exist
        self.persist_dir.mkdir(parents=True, exist_ok=True)
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        
        if self.verbose:
            print(f"📂 VectorStore initialized with persist_dir: {self.persist_dir}")
    
    @property
    def client(self) -> chromadb.PersistentClient:
        """Lazy load the ChromaDB client."""
        if self._client is None:
            self._client = chromadb.PersistentClient(path=str(self.persist_dir))
        return self._client
    
    @staticmethod
    def safe_str(val: Any) -> str:
        """Convert any value to a safe string, handling None values."""
        return "" if val is None else str(val)
    
    def _validate_records(self, records: List[Dict[str, Any]]) -> None:
        """Validate that records have required fields."""
        if not records:
            raise ValueError("Records list cannot be empty")
        
        for i, record in enumerate(records):
            if "embedding" not in record:
                raise ValueError(f"Record {i} missing 'embedding' field")
            if "text" not in record:
                raise ValueError(f"Record {i} missing 'text' field")
            
            # Validate embedding is array-like
            embedding = record["embedding"]
            if not hasattr(embedding, '__iter__') or isinstance(embedding, str):
                raise ValueError(f"Record {i} embedding must be array-like")
    
    def _prepare_data(self, records: List[Dict[str, Any]]) -> Dict[str, List]:
        """Prepare data for ChromaDB insertion."""
        ids = []
        embeddings = []
        documents = []
        metadatas = []
        
        for rec in records:
            # Generate unique ID
            table = self.safe_str(rec.get('table'))
            column = self.safe_str(rec.get('column', 'table'))
            col_id = f"{table}.{column}"
            
            # Handle duplicate IDs
            base_id = col_id
            counter = 1
            while col_id in ids:
                col_id = f"{base_id}_{counter}"
                counter += 1
            
            ids.append(col_id)
            
            # Prepare embedding
            embedding = rec["embedding"]
            if isinstance(embedding, np.ndarray):
                embeddings.append(embedding.tolist())
            else:
                embeddings.append(list(embedding))
            
            documents.append(str(rec["text"]))
            
            # Prepare metadata (ensure all values are ChromaDB compatible)
            metadata = {
                "table": self.safe_str(rec.get("table")),
                "column": self.safe_str(rec.get("column")),
                "level": "column" if rec.get("column") is not None else "table"
            }
            
            # Add any additional metadata fields
            for key, value in rec.items():
                if key not in ["embedding", "text", "table", "column"]:
                    # Convert to ChromaDB compatible types
                    if isinstance(value, (str, int, float, bool)):
                        metadata[key] = value
                    elif value is not None:
                        metadata[key] = str(value)
            
            metadatas.append(metadata)
        
        return {
            "ids": ids,
            "embeddings": embeddings,
            "documents": documents,
            "metadatas": metadatas
        }
    
    def store_records(
        self, 
        collection_name: str, 
        records: List[Dict[str, Any]],
        clear_existing: bool = False
    ) -> int:
        """
        Store records in a ChromaDB collection.
        
        Args:
            collection_name: Name of the collection
            records: List of records with embeddings
            clear_existing: Whether to clear existing collection first
            
        Returns:
            Number of records stored
        """
        try:
            self._validate_records(records)
            
            # Get or create collection
            if clear_existing:
                try:
                    self.client.delete_collection(collection_name)
                    if self.verbose:
                        print(f"🗑️ Cleared existing collection '{collection_name}'")
                except Exception:
                    pass  # Collection might not exist
            
            collection = self.client.get_or_create_collection(
                name=collection_name,
                metadata={"hnsw:space": "cosine"}  # Ensure cosine distance is used
            )
            
            # Prepare data
            data = self._prepare_data(records)
            
            # Store in ChromaDB
            collection.add(**data)
            
            if self.verbose:
                print(f"✅ Stored {len(data['ids'])} records in collection '{collection_name}'")
            
            return len(data['ids'])
            
        except Exception as e:
            self.logger.error(f"Failed to store records in collection '{collection_name}': {e}")
            raise
    
    def load_collection(self, collection_name: str) -> chromadb.Collection:
        """
        Load a ChromaDB collection.
        
        Args:
            collection_name: Name of the collection to load
            
        Returns:
            ChromaDB collection object
        """
        try:
            return self.client.get_collection(name=collection_name)
        except Exception as e:
            self.logger.error(f"Failed to load collection '{collection_name}': {e}")
            raise
    
    def collection_exists(self, collection_name: str) -> bool:
        """Check if a collection exists."""
        try:
            self.client.get_collection(name=collection_name)
            return True
        except Exception:
            return False
    
    def list_collections(self) -> List[str]:
        """List all available collections."""
        try:
            collections = self.client.list_collections()
            return [col.name for col in collections]
        except Exception as e:
            self.logger.error(f"Failed to list collections: {e}")
            return []
    
    def delete_collection(self, collection_name: str) -> bool:
        """
        Delete a collection.
        
        Args:
            collection_name: Name of collection to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.client.delete_collection(collection_name)
            if self.verbose:
                print(f"🗑️ Deleted collection '{collection_name}'")
            return True
        except Exception as e:
            self.logger.error(f"Failed to delete collection '{collection_name}': {e}")
            return False
    
    def get_collection_info(self, collection_name: str) -> Dict[str, Any]:
        """Get information about a collection."""
        try:
            collection = self.load_collection(collection_name)
            count = collection.count()
            
            info = {
                "name": collection_name,
                "count": count,
                "embedding_dim": None,
                "sample_metadata": None
            }
            
            # Only get sample data if collection has records
            if count > 0:
                # Get sample metadata to understand structure
                sample_data = collection.peek(limit=1)
                
                # Check embeddings safely
                embeddings = sample_data.get("embeddings")
                if embeddings is not None and len(embeddings) > 0:
                    info["embedding_dim"] = len(embeddings[0])
                
                # Check metadatas safely
                metadatas = sample_data.get("metadatas")
                if metadatas is not None and len(metadatas) > 0:
                    info["sample_metadata"] = metadatas[0]
            
            return info
            
        except Exception as e:
            self.logger.error(f"Failed to get info for collection '{collection_name}': {e}")
            return {"error": str(e)}
    
    def store_embedded_schema(
        self, 
        embedded_data: Dict[str, List[Dict[str, Any]]],
        collection_prefix: str = "schema",
        clear_existing: bool = False
    ) -> Dict[str, int]:
        """
        Store embedded schema data (columns and tables) in separate collections.
        
        Args:
            embedded_data: Dictionary with 'columns' and 'tables' keys
            collection_prefix: Prefix for collection names
            clear_existing: Whether to clear existing collections
            
        Returns:
            Dictionary with counts for each collection
        """
        results = {}
        
        if "columns" in embedded_data:
            columns_collection = f"{collection_prefix}_columns"
            results["columns"] = self.store_records(
                columns_collection, 
                embedded_data["columns"],
                clear_existing
            )
        
        if "tables" in embedded_data:
            tables_collection = f"{collection_prefix}_tables"
            results["tables"] = self.store_records(
                tables_collection,
                embedded_data["tables"],
                clear_existing
            )
        
        return results


# Backwards compatibility functions
def safe_str(val: Any) -> str:
    """Legacy function for backwards compatibility."""
    return VectorStore.safe_str(val)


def store_in_chroma(
    name: str,
    records: List[Dict[str, Any]],
    persist_dir: Optional[str] = None
) -> None:
    """Legacy function for backwards compatibility."""
    vector_store = VectorStore(persist_dir)
    vector_store.store_records(name, records)


def load_chroma_collection(collection_name: str = None, name: str = None, persist_dir: Optional[str] = None):
    """Legacy function for backwards compatibility."""
    # Handle both old and new parameter names
    collection_name = collection_name or name
    if not collection_name:
        raise ValueError("Must provide either 'collection_name' or 'name' parameter")
    
    vector_store = VectorStore(persist_dir, verbose=False)
    return vector_store.load_collection(collection_name)

if __name__ == "__main__":
    import numpy as np
    from pprint import pprint
    
    try:
        from schema_embedder import SchemaEmbedder
    except ImportError:
        print("SchemaEmbedder not available for demo")
        SchemaEmbedder = None
    
    # Initialize vector store (will use config)
    vector_store = VectorStore()
    
    print("📊 Vector Store Demo")
    print("===================")
    print(f"Using ChromaDB path from config: {vector_store.persist_dir}")
    
    # Demo with sample data
    sample_records = [
        {
            "table": "customers",
            "column": "customer_id",
            "text": "customer identification number primary key",
            "embedding": np.random.rand(384).tolist()  # Simulated embedding
        },
        {
            "table": "customers", 
            "column": "email",
            "text": "customer email address contact information",
            "embedding": np.random.rand(384).tolist()
        },
        {
            "table": "orders",
            "text": "orders table containing customer purchase information",
            "embedding": np.random.rand(384).tolist()  # Table-level embedding
        }
    ]
    
    # Store sample data
    print("\n1. Storing sample records...")
    count = vector_store.store_records("demo_schema", sample_records, clear_existing=True)
    print(f"Stored {count} records")
    
    # List collections
    print("\n2. Available collections:")
    collections = vector_store.list_collections()
    for col in collections:
        print(f"  - {col}")
    
    # Get collection info
    print("\n3. Collection information:")
    info = vector_store.get_collection_info("demo_schema")
    pprint(info)
    
    # Load and query collection
    print("\n4. Loading collection for queries...")
    collection = vector_store.load_collection("demo_schema")
    print(f"Collection loaded: {collection.name}")
    
    # Demonstrate with real schema embedder if available
    if SchemaEmbedder:
        print("\n5. Real schema embedding demo...")
        try:
            # Create embedder with config
            config = vector_store.config
            embedder = SchemaEmbedder(
                model_name=config.get("embeddings.model_name"),
                enable_caching=config.get("embeddings.enable_caching"),
                cache_dir=config.get("embeddings.cache_dir") if config.get("embeddings.enable_caching") else None
            )
            
            embedded_data = embedder.embed_schema(
                config.get("schema.schema_path"),
                cache_prefix="demo_retail"
            )
            
            # Store embedded schema
            results = vector_store.store_embedded_schema(
                embedded_data,
                collection_prefix="retail_demo",
                clear_existing=True
            )
            
            print("Embedded schema storage results:")
            pprint(results)
            
            # Show collection info for real data
            if results.get("columns", 0) > 0:
                col_info = vector_store.get_collection_info("retail_demo_columns")
                print("\nColumns collection info:")
                pprint(col_info)
                
        except Exception as e:
            print(f"Schema embedding demo failed: {e}")
    
    print("\n✅ Demo completed!")