from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List, Dict, Any, Optional, Union
import joblib
import os
import sys
from pathlib import Path

# Add parent directory to path for imports
current_dir = Path(__file__).parent
parent_dir = current_dir.parent
project_root = parent_dir.parent

# Add all necessary paths
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(parent_dir))
sys.path.insert(0, str(current_dir))

# Import with robust fallback handling
try:
    # Try package imports first
    from .semantic_schema import SemanticSchema, prepare_semantic_schema
    from ..utils.config_manager import get_config
except ImportError:
    try:
        # Try direct imports from current directory
        from semantic_schema import SemanticSchema, prepare_semantic_schema
        from sql_generator.utils.config_manager import get_config
    except ImportError:
        try:
            # Try absolute imports
            from sql_generator.schema.semantic_schema import SemanticSchema, prepare_semantic_schema
            from sql_generator.utils.config_manager import get_config
        except ImportError:
            # Last resort fallback - create basic functions
            import sys
            from pathlib import Path
            
            # Try to import semantic_schema from local directory
            try:
                from semantic_schema import SemanticSchema, prepare_semantic_schema
            except ImportError:
                # If that fails, provide minimal implementation
                class SemanticSchema:
                    def __init__(self, schema_path):
                        self.schema_path = schema_path
                    
                    def build_column_corpus(self):
                        return []
                    
                    def build_table_corpus(self):
                        return []
                
                def prepare_semantic_schema(schema_path):
                    return SemanticSchema(schema_path)
            
            # Try to import config_manager
            try:
                config_file = Path(__file__).parent.parent.parent / "data" / "config" / "config.json"
                if config_file.exists():
                    import json
                    with open(config_file) as f:
                        _config = json.load(f)
                    def get_config():
                        return _config
                else:
                    def get_config():
                        return {
                            "embeddings": {"model_name": "all-MiniLM-L6-v2", "enable_caching": False},
                            "vector_store": {"persist_dir": "./data/chroma_db", "verbose": True}
                        }
            except Exception:
                def get_config():
                    return {
                        "embeddings": {"model_name": "all-MiniLM-L6-v2", "enable_caching": False},
                        "vector_store": {"persist_dir": "./data/chroma_db", "verbose": True}
                    }


class SchemaEmbedder:
    """Handles embedding of database schema semantic data using sentence transformers."""
    
    def __init__(
        self, 
        model_name: Optional[str] = None,
        cache_dir: Optional[str] = None,
        verbose: Optional[bool] = None,
        enable_caching: Optional[bool] = None
    ):
        """
        Initialize the schema embedder.
        
        Args:
            model_name: Name of the sentence transformer model to use (overrides config)
            cache_dir: Directory to store embedding caches (overrides config)
            verbose: Whether to print progress messages (overrides config)
            enable_caching: Whether to enable embedding caching (overrides config)
        """
        self.config = get_config()
        
        # Use provided values or fall back to config
        self.model_name = model_name or self.config.get("embeddings.model_name", "all-MiniLM-L6-v2")
        self.enable_caching = enable_caching if enable_caching is not None else self.config.get("embeddings.enable_caching", False)
        self.verbose = verbose if verbose is not None else self.config.get("vector_store.verbose", True)
        
        # Handle cache directory
        if cache_dir is not None:
            self.cache_dir = Path(cache_dir)
        elif self.enable_caching:
            config_cache_dir = self.config.get("embeddings.cache_dir")
            if config_cache_dir:
                # Convert relative paths to absolute paths based on config file location
                if not os.path.isabs(config_cache_dir):
                    config_dir = self.config.config_path.parent
                    self.cache_dir = config_dir / config_cache_dir
                else:
                    self.cache_dir = Path(config_cache_dir)
            else:
                self.cache_dir = None
        else:
            self.cache_dir = None
            
        self._model = None
        self._embedded_data = None
        
        # Create cache directory if specified and caching is enabled
        if self.cache_dir and self.enable_caching:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            
        if self.verbose:
            print(f"🤖 SchemaEmbedder initialized:")
            print(f"   Model: {self.model_name}")
            print(f"   Caching: {self.enable_caching}")
            if self.cache_dir:
                print(f"   Cache dir: {self.cache_dir}")
    
    @property
    def model(self) -> SentenceTransformer:
        """Lazy load the sentence transformer model."""
        if self._model is None:
            if self.verbose:
                print(f"📦 Loading SBERT model: {self.model_name}")
            self._model = SentenceTransformer(self.model_name)
        return self._model
    
    def _get_cache_path(self, cache_name: str) -> Optional[str]:
        """Get the full cache file path if caching is enabled."""
        if self.enable_caching and self.cache_dir and cache_name:
            return str(self.cache_dir / f"{cache_name}.pkl")
        return None
    
    def embed_corpus(
        self, 
        corpus: List[Dict[str, Any]], 
        cache_name: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Embed a corpus of text entries.
        
        Args:
            corpus: List of dictionaries containing 'text' field
            cache_name: Name for caching (without .pkl extension)
            
        Returns:
            List of dictionaries with added 'embedding' field
        """
        if not corpus:
            return []
        
        texts = [entry["text"] for entry in corpus]
        cache_path = self._get_cache_path(cache_name)
        
        # Try to load from cache only if caching is enabled
        if cache_path and self.enable_caching and os.path.exists(cache_path):
            if self.verbose:
                print(f"🔁 Loading cached embeddings from {cache_path}")
            embeddings = joblib.load(cache_path)
        else:
            # Generate new embeddings
            if self.verbose:
                print(f"⚙️ Generating embeddings for {len(texts)} entries...")
            embeddings = self.model.encode(texts, show_progress_bar=self.verbose)
            
            # Cache the embeddings only if caching is enabled
            if cache_path and self.enable_caching:
                joblib.dump(embeddings, cache_path)
                if self.verbose:
                    print(f"💾 Cached embeddings to {cache_path}")
        
        # Enrich corpus with embeddings
        enriched = []
        for entry, embedding in zip(corpus, embeddings):
            enriched.append({
                **entry,
                "embedding": np.array(embedding)
            })
        
        return enriched
    
    def embed_semantic_data(
        self, 
        semantic_data: Dict[str, List[Dict[str, Any]]],
        cache_prefix: Optional[str] = None
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Embed both column and table semantic corpora.
        
        Args:
            semantic_data: Dictionary with 'columns' and 'tables' keys
            cache_prefix: Prefix for cache file names
            
        Returns:
            Dictionary with embedded columns and tables
        """
        embedded_columns = self.embed_corpus(
            semantic_data["columns"],
            cache_name=f"{cache_prefix}_columns" if cache_prefix else None
        )
        
        embedded_tables = self.embed_corpus(
            semantic_data["tables"],
            cache_name=f"{cache_prefix}_tables" if cache_prefix else None
        )
        
        self._embedded_data = {
            "columns": embedded_columns,
            "tables": embedded_tables
        }
        
        return self._embedded_data
    
    def embed_schema(
        self, 
        schema_source: Union[str, SemanticSchema],
        cache_prefix: Optional[str] = None
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Embed a schema from file path or SemanticSchema object.
        
        Args:
            schema_source: Path to schema file or SemanticSchema instance
            cache_prefix: Prefix for cache file names
            
        Returns:
            Dictionary with embedded columns and tables
        """
        if isinstance(schema_source, str):
            # Load from file path
            semantic_schema = SemanticSchema(schema_source)
            semantic_data = semantic_schema.prepare_semantic_data()
        elif isinstance(schema_source, SemanticSchema):
            # Use existing SemanticSchema object
            semantic_data = schema_source.prepare_semantic_data()
        else:
            raise ValueError("schema_source must be a file path or SemanticSchema instance")
        
        return self.embed_semantic_data(semantic_data, cache_prefix)
    
    def get_embedding_stats(self) -> Dict[str, Any]:
        """Get statistics about the current embedded data."""
        if not self._embedded_data:
            return {"error": "No embedded data available"}
        
        columns = self._embedded_data["columns"]
        tables = self._embedded_data["tables"]
        
        stats = {
            "model_name": self.model_name,
            "columns": {
                "count": len(columns),
                "embedding_dim": columns[0]["embedding"].shape[0] if columns else 0,
                "sample_tables": list(set(col["table"] for col in columns[:10]))
            },
            "tables": {
                "count": len(tables),
                "embedding_dim": tables[0]["embedding"].shape[0] if tables else 0,
                "table_names": [table["table"] for table in tables[:10]]
            }
        }
        
        return stats
    
    def clear_cache(self, cache_prefix: Optional[str] = None):
        """Clear cached embeddings."""
        if not self.enable_caching:
            if self.verbose:
                print("Caching is disabled - no cache to clear")
            return
            
        if not self.cache_dir:
            if self.verbose:
                print("No cache directory configured")
            return
        
        if cache_prefix:
            # Clear specific cache files
            patterns = [f"{cache_prefix}_columns.pkl", f"{cache_prefix}_tables.pkl"]
            for pattern in patterns:
                cache_file = self.cache_dir / pattern
                if cache_file.exists():
                    cache_file.unlink()
                    if self.verbose:
                        print(f"🗑️ Deleted cache file: {cache_file}")
        else:
            # Clear all cache files
            for cache_file in self.cache_dir.glob("*.pkl"):
                cache_file.unlink()
                if self.verbose:
                    print(f"🗑️ Deleted cache file: {cache_file}")


# Backwards compatibility functions
def embed_corpus(
    corpus: List[Dict[str, Any]],
    model: SentenceTransformer,
    cache_path: str = None
) -> List[Dict[str, Any]]:
    """Legacy function for embedding corpus."""
    embedder = SchemaEmbedder.__new__(SchemaEmbedder)
    embedder._model = model
    embedder.cache_dir = None
    embedder.verbose = True
    
    # Convert cache_path to cache_name
    cache_name = None
    if cache_path:
        cache_name = Path(cache_path).stem
        embedder.cache_dir = Path(cache_path).parent
    
    return embedder.embed_corpus(corpus, cache_name)


def embed_schema_corpora(
    semantic_data: Dict[str, List[Dict[str, Any]]],
    model_name: str = "all-MiniLM-L6-v2",
    cache_prefix: str = None
) -> Dict[str, List[Dict[str, Any]]]:
    """Legacy function for embedding schema corpora."""
    embedder = SchemaEmbedder(model_name=model_name, cache_dir="." if cache_prefix else None)
    return embedder.embed_semantic_data(semantic_data, cache_prefix)


if __name__ == "__main__":
    from pprint import pprint

    # Example usage with class-based approach (uses config)
    embedder = SchemaEmbedder()
    
    # Get schema path from config
    config = get_config()
    schema_path = config.get("schema.schema_path", r"..\..\tables_schema.json")
    
    embedded_data = embedder.embed_schema(
        schema_path,
        cache_prefix="retail_schema"
    )
    
    print("🔍 Sample embedded column:")
    sample_col = embedded_data["columns"][0]
    print("Table:", sample_col["table"])
    print("Column:", sample_col["column"])
    print("Text:", sample_col["text"][:100] + "...")
    print("Embedding shape:", sample_col["embedding"].shape)
    print("Embedding preview:", sample_col["embedding"][:5])  # First 5 dimensions
    
    print("\n📊 Embedding Statistics:")
    pprint(embedder.get_embedding_stats())
    
    print("\n📘 Sample embedded table:")
    sample_table = embedded_data["tables"][0]
    print("Table:", sample_table["table"])
    print("Text:", sample_table["text"][:100] + "...")
    print("Embedding shape:", sample_table["embedding"].shape)