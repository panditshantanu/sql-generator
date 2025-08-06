from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any, Optional, Union
import numpy as np
import logging
import sys
from pathlib import Path

# Add parent directory to path for imports
current_dir = Path(__file__).parent
parent_dir = current_dir.parent
sys.path.insert(0, str(current_dir))
sys.path.insert(0, str(parent_dir))

try:
    from .vector_store import VectorStore, load_chroma_collection
    from ..utils.config_manager import get_config
except ImportError:
    # Handle direct execution or path issues
    try:
        from vector_store import VectorStore, load_chroma_collection
        from sql_generator.utils.config_manager import get_config
    except ImportError:
        # Fallback - ensure all paths are available
        sys.path.insert(0, str(parent_dir / 'schema'))
        sys.path.insert(0, str(parent_dir))
        try:
            from vector_store import VectorStore, load_chroma_collection
            from sql_generator.utils.config_manager import get_config
        except ImportError:
            from vector_store import VectorStore, load_chroma_collection
            def get_config():
                return {"embeddings": {"model_name": "all-MiniLM-L6-v2"}}


class SchemaSearcher:
    """Handles semantic search operations on schema embeddings stored in ChromaDB."""
    
    def __init__(
        self, 
        vector_store: Optional[VectorStore] = None,
        model_name: Optional[str] = None,
        verbose: bool = False
    ):
        """
        Initialize the SchemaSearcher.
        
        Args:
            vector_store: Optional VectorStore instance. If None, creates new one
            model_name: Name of the sentence transformer model
            verbose: Whether to enable verbose logging
        """
        self.logger = logging.getLogger(__name__)
        self.config = get_config()
        
        # Initialize model
        self.model_name = model_name or self.config.get("embeddings.model_name", "all-MiniLM-L6-v2")
        self.model = SentenceTransformer(self.model_name)
        
        # Initialize vector store
        self.vector_store = vector_store or VectorStore(verbose=verbose)
        
        # Cache for embeddings
        self._embedding_cache = {}
        
        self.logger.info(f"SchemaSearcher initialized with model: {self.model_name}")
    
    def search(
        self,
        query: str,
        n_results: int = 10,
        collection_types: Optional[List[str]] = None,
        include_scores: bool = True,
        score_threshold: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for relevant schema elements based on query.
        
        Args:
            query: Search query string
            n_results: Maximum number of results to return
            collection_types: Types of collections to search (e.g., ['tables', 'columns'])
            include_scores: Whether to include similarity scores
            score_threshold: Minimum similarity score threshold
            
        Returns:
            List of dictionaries containing search results
        """
        try:
            self.logger.debug(f"Searching for: '{query}' (n_results={n_results})")
            
            # Generate query embedding
            query_embedding = self._get_query_embedding(query)
            
            # Determine collections to search
            if collection_types is None:
                collection_types = ['schema_tables', 'schema_columns']
            
            all_results = []
            
            # Search each collection
            for collection_type in collection_types:
                try:
                    collection = load_chroma_collection(
                        collection_name=collection_type,
                        persist_dir=self.vector_store.persist_dir
                    )
                    
                    if collection is None:
                        self.logger.warning(f"Collection '{collection_type}' not found")
                        continue
                    
                    # Perform search
                    results = collection.query(
                        query_embeddings=[query_embedding.tolist()],
                        n_results=n_results,
                        include=['metadatas', 'documents', 'distances']
                    )
                    
                    # Process results
                    collection_results = self._process_collection_results(
                        results, collection_type, include_scores, score_threshold
                    )
                    
                    all_results.extend(collection_results)
                    
                except Exception as e:
                    self.logger.error(f"Error searching collection '{collection_type}': {e}")
                    continue
            
            # Sort by score and limit results
            if include_scores:
                all_results.sort(key=lambda x: x.get('score', 0), reverse=True)
            
            final_results = all_results[:n_results]
            
            self.logger.debug(f"Found {len(final_results)} results")
            return final_results
            
        except Exception as e:
            self.logger.error(f"Search failed: {e}")
            return []
    
    def _get_query_embedding(self, query: str) -> np.ndarray:
        """Generate embedding for search query with caching."""
        if query in self._embedding_cache:
            return self._embedding_cache[query]
        
        embedding = self.model.encode(query, convert_to_numpy=True)
        self._embedding_cache[query] = embedding
        
        return embedding
    
    def _process_collection_results(
        self,
        results: Dict,
        collection_type: str,
        include_scores: bool,
        score_threshold: Optional[float]
    ) -> List[Dict[str, Any]]:
        """Process raw collection results into structured format."""
        processed_results = []
        
        if not results.get('documents') or not results['documents'][0]:
            return processed_results
        
        documents = results['documents'][0]
        metadatas = results.get('metadatas', [[{}] * len(documents)])[0]
        distances = results.get('distances', [[0] * len(documents)])[0]
        
        for i, (doc, metadata, distance) in enumerate(zip(documents, metadatas, distances)):
            # Convert distance to similarity score
            if distance is not None:
                # For cosine distance, convert to similarity score
                # Only clamp negative scores to 0, but allow scores > 1 to remain
                score = 1 - distance
                if score < 0:
                    score = 0.0
            else:
                score = 0.0
            
            # Apply score threshold
            if score_threshold is not None and score < score_threshold:
                continue
            
            result = {
                'content': doc,
                'metadata': metadata or {},
                'collection_type': collection_type,
                'rank': i + 1
            }
            
            if include_scores:
                result['score'] = score
                result['distance'] = distance
            
            processed_results.append(result)
        
        return processed_results
    
    def search_tables(
        self,
        query: str,
        n_results: int = 5,
        include_scores: bool = True
    ) -> List[Dict[str, Any]]:
        """Search specifically for table-related results."""
        return self.search(
            query=query,
            n_results=n_results,
            collection_types=['schema_tables'],
            include_scores=include_scores
        )
    
    def search_columns(
        self,
        query: str,
        n_results: int = 10,
        include_scores: bool = True
    ) -> List[Dict[str, Any]]:
        """Search specifically for column-related results."""
        return self.search(
            query=query,
            n_results=n_results,
            collection_types=['schema_columns'],
            include_scores=include_scores
        )
    
    def search_schema(
        self,
        query: str,
        k_tables: int = 5,
        k_columns: int = 10,
        include_scores: bool = True
    ) -> Dict[str, Any]:
        """
        Search for relevant schema elements (tables and columns) based on query.
        This method maintains compatibility with existing code.
        
        Args:
            query: Search query string
            k_tables: Maximum number of table results to return
            k_columns: Maximum number of column results to return
            include_scores: Whether to include similarity scores
            
        Returns:
            Dictionary containing 'tables' and 'columns' results
        """
        try:
            # Search for tables
            table_results = self.search_tables(
                query=query,
                n_results=k_tables,
                include_scores=include_scores
            )
            
            # Search for columns
            column_results = self.search_columns(
                query=query,
                n_results=k_columns,
                include_scores=include_scores
            )
            
            return {
                'tables': table_results,
                'columns': column_results,
                'query': query
            }
            
        except Exception as e:
            self.logger.error(f"Error in search_schema: {e}")
            return {
                'tables': [],
                'columns': [],
                'query': query,
                'error': str(e)
            }
    
    def get_related_schema(
        self,
        table_name: str,
        include_columns: bool = True,
        n_columns: int = 20
    ) -> Dict[str, Any]:
        """
        Get schema information related to a specific table.
        
        Args:
            table_name: Name of the table
            include_columns: Whether to include column information
            n_columns: Maximum number of columns to return
            
        Returns:
            Dictionary containing table and column information
        """
        result = {
            'table': table_name,
            'table_info': {},
            'columns': []
        }
        
        try:
            # Search for table information
            table_results = self.search_tables(table_name, n_results=1)
            if table_results:
                result['table_info'] = table_results[0]
            
            # Search for columns if requested
            if include_columns:
                column_query = f"table {table_name} columns"
                column_results = self.search_columns(column_query, n_results=n_columns)
                
                # Filter columns that belong to this table
                relevant_columns = []
                for col in column_results:
                    col_metadata = col.get('metadata', {})
                    if col_metadata.get('table_name', '').lower() == table_name.lower():
                        relevant_columns.append(col)
                
                result['columns'] = relevant_columns
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error getting related schema for '{table_name}': {e}")
            return result
    
    def clear_cache(self):
        """Clear the embedding cache."""
        self._embedding_cache.clear()
        self.logger.debug("Embedding cache cleared")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the search index."""
        try:
            stats = {
                'model_name': self.model_name,
                'cache_size': len(self._embedding_cache),
                'collections': {}
            }
            
            # Get collection statistics
            collection_types = ['schema_tables', 'schema_columns']
            for collection_type in collection_types:
                try:
                    collection = load_chroma_collection(
                        collection_name=collection_type,
                        persist_dir=self.vector_store.persist_dir
                    )
                    
                    if collection:
                        count = collection.count()
                        stats['collections'][collection_type] = {
                            'count': count,
                            'exists': True
                        }
                    else:
                        stats['collections'][collection_type] = {
                            'count': 0,
                            'exists': False
                        }
                        
                except Exception as e:
                    self.logger.error(f"Error getting stats for '{collection_type}': {e}")
                    stats['collections'][collection_type] = {
                        'error': str(e),
                        'exists': False
                    }
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Error getting stats: {e}")
            return {'error': str(e)}


def search_schema(
    query: str,
    n_results: int = 10,
    collection_types: Optional[List[str]] = None,
    **kwargs
) -> List[Dict[str, Any]]:
    """
    Convenience function for quick schema searches.
    
    Args:
        query: Search query
        n_results: Number of results to return
        collection_types: Types of collections to search
        **kwargs: Additional arguments passed to SchemaSearcher
        
    Returns:
        List of search results
    """
    searcher = SchemaSearcher(**kwargs)
    return searcher.search(
        query=query,
        n_results=n_results,
        collection_types=collection_types
    )


# Example usage and testing
if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    try:
        # Create searcher
        searcher = SchemaSearcher(verbose=True)
        
        # Test search
        print("Testing schema search...")
        results = searcher.search("customer information", n_results=5)
        
        print(f"Found {len(results)} results:")
        for i, result in enumerate(results[:3], 1):
            print(f"{i}. {result.get('content', 'No content')[:100]}...")
            print(f"   Score: {result.get('score', 'N/A')}")
            print(f"   Type: {result.get('collection_type', 'Unknown')}")
            print()
        
        # Get stats
        stats = searcher.get_stats()
        print("Index statistics:")
        for collection, info in stats.get('collections', {}).items():
            print(f"  {collection}: {info.get('count', 0)} items")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
