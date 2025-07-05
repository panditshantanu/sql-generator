import re
from typing import List, Dict, Any

try:
    from .schema_loader import SchemaLoader
except ImportError:
    # Handle direct execution
    from schema_loader import SchemaLoader


class SemanticSchema:
    """Handles semantic processing of database schemas for embedding and search."""
    
    def __init__(self, schema_path: str):
        """Initialize with a schema file path."""
        self.schema_loader = SchemaLoader(schema_path)
        self._column_corpus = None
        self._table_corpus = None
    
    @staticmethod
    def normalize(text: str) -> str:
        """Lowercase and remove extra whitespace from text."""
        return re.sub(r"\s+", " ", text.strip().lower())
    
    def build_column_corpus(self) -> List[Dict[str, Any]]:
        """Flatten all columns into a semantic corpus for embedding."""
        if self._column_corpus is not None:
            return self._column_corpus
            
        corpus = []
        for table in self.schema_loader.schema.tables:
            for col_key, col_meta in table.columns.items():
                phrases = [
                    col_meta.name,
                    col_meta.description,
                    col_key,
                    table.table_name,
                    table.display_name
                ]
                if col_meta.aliases:
                    phrases.extend(col_meta.aliases)
                text = self.normalize(" ".join(phrases))
                corpus.append({
                    "table": table.table_name,
                    "column": col_key,
                    "text": text,
                    "meta": col_meta
                })
        
        self._column_corpus = corpus
        return corpus
    
    def build_table_corpus(self) -> List[Dict[str, Any]]:
        """Build a semantic corpus for tables including aliases."""
        if self._table_corpus is not None:
            return self._table_corpus
            
        corpus = []
        for table in self.schema_loader.schema.tables:
            phrases = [
                table.display_name,
                table.description,
                table.table_name,
                " ".join([col.name for col in table.columns.values()]),
                " ".join([col.description for col in table.columns.values() if col.description])
            ]
            
            # Add table aliases to the semantic text
            if table.aliases:
                phrases.extend(table.aliases)
                phrases.append(" ".join(table.aliases))  # Also add as combined text
            
            text = self.normalize(" ".join([p for p in phrases if p]))
            corpus.append({
                "table": table.table_name,
                "meta": table,
                "text": text,
                "aliases": table.aliases or []
            })
        
        self._table_corpus = corpus
        return corpus
    
    def prepare_semantic_data(self) -> Dict[str, List[Dict[str, Any]]]:
        """Load, normalize, and flatten schema into semantic corpora."""
        return {
            "columns": self.build_column_corpus(),
            "tables": self.build_table_corpus()
        }
    
    @property
    def column_corpus(self) -> List[Dict[str, Any]]:
        """Get the column corpus, building it if necessary."""
        return self.build_column_corpus()
    
    @property
    def table_corpus(self) -> List[Dict[str, Any]]:
        """Get the table corpus, building it if necessary."""
        return self.build_table_corpus()


# Backwards compatibility functions
def normalize(text: str) -> str:
    """Lowercase and remove extra whitespace from text."""
    return SemanticSchema.normalize(text)


def build_column_corpus(schema_loader: SchemaLoader) -> List[Dict[str, Any]]:
    """Flatten all columns into a semantic corpus for embedding."""
    semantic_schema = SemanticSchema.__new__(SemanticSchema)
    semantic_schema.schema_loader = schema_loader
    semantic_schema._column_corpus = None
    semantic_schema._table_corpus = None
    return semantic_schema.build_column_corpus()


def build_table_corpus(schema_loader: SchemaLoader) -> List[Dict[str, Any]]:
    """Build a semantic corpus for tables."""
    semantic_schema = SemanticSchema.__new__(SemanticSchema)
    semantic_schema.schema_loader = schema_loader
    semantic_schema._column_corpus = None
    semantic_schema._table_corpus = None
    return semantic_schema.build_table_corpus()


def prepare_semantic_schema(schema_path: str) -> Dict[str, List[Dict[str, Any]]]:
    """Load, normalize, and flatten schema into semantic corpora."""
    semantic_schema = SemanticSchema(schema_path)
    return semantic_schema.prepare_semantic_data()

if __name__ == "__main__":
    from pprint import pprint

    # Use relative path from the schema directory
    semantic_data = prepare_semantic_schema(r"..\..\tables_schema.json")

    print("🔍 Sample Column Corpus Entry:")
    pprint(semantic_data["columns"][0])

    print("\n📘 Sample Table Corpus Entry:")
    pprint(semantic_data["tables"][0])
