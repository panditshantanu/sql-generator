from typing import List, Dict, Optional
from pydantic import BaseModel, Field, ValidationError
import json
import os


# -----------------------------
# Pydantic Models for Validation
# -----------------------------

class Column(BaseModel):
    name: str
    description: str
    type: str
    length: Optional[int] = None
    precision: Optional[List[int]] = None
    nullable: Optional[bool] = True
    aliases: Optional[List[str]] = Field(default_factory=list)


class Table(BaseModel):
    table_name: str
    aliases: Optional[List[str]] = Field(default_factory=list)
    display_name: str
    description: str
    columns: Dict[str, Column]


class Schema(BaseModel):
    tables: List[Table]


# -----------------------------
# Schema Loader Class
# -----------------------------

class SchemaLoader:
    def __init__(self, path: str):
        if not os.path.exists(path):
            raise FileNotFoundError(f"Schema file not found: {path}")
        with open(path, "r", encoding="utf-8") as f:
            raw = json.load(f)
        try:
            self.schema = Schema(**raw)
        except ValidationError as e:
            raise ValueError(f"❌ Schema validation failed:\n{e}")
        self.table_map = {t.table_name: t for t in self.schema.tables}
        # Create alias map for table lookup
        self.table_alias_map = {}
        for table in self.schema.tables:
            # Add the table name itself
            self.table_alias_map[table.table_name] = table
            # Add all aliases
            if table.aliases:
                for alias in table.aliases:
                    self.table_alias_map[alias] = table

    def list_tables(self) -> List[str]:
        return list(self.table_map.keys())

    def get_table(self, table_name: str) -> Optional[Table]:
        """Get table by name or alias."""
        return self.table_alias_map.get(table_name)

    def get_table_by_name_only(self, table_name: str) -> Optional[Table]:
        """Get table by exact name only (not aliases)."""
        return self.table_map.get(table_name)

    def find_table_by_alias(self, alias: str) -> Optional[Table]:
        """Find table by alias name."""
        for table in self.schema.tables:
            if table.aliases and alias in table.aliases:
                return table
        return None

    def get_columns(self, table_identifier: str) -> Optional[Dict[str, Column]]:
        """Get columns by table name or alias."""
        table = self.get_table(table_identifier)
        return table.columns if table else None
        table = self.get_table(table_identifier)
        return table.columns if table else None

    def find_column(self, column_name: str) -> List[Dict]:
        """Find columns by name or alias across all tables."""
        matches = []
        for table in self.schema.tables:
            for col_key, col in table.columns.items():
                if col_key == column_name or column_name in (col.aliases or []):
                    matches.append({
                        "table": table.table_name,
                        "column": col_key,
                        "meta": col
                    })
        return matches

    def find_table(self, table_identifier: str) -> List[Dict]:
        """Find tables by name or alias."""
        matches = []
        for table in self.schema.tables:
            if (table.table_name == table_identifier or 
                (table.aliases and table_identifier in table.aliases)):
                matches.append({
                    "table": table.table_name,
                    "aliases": table.aliases or [],
                    "display_name": table.display_name,
                    "meta": table
                })
        return matches

    def describe_table(self, table_identifier: str) -> Optional[Dict[str, str]]:
        """Return a dictionary of column names and descriptions for a table."""
        columns = self.get_columns(table_identifier)
        if not columns:
            return None
        return {col_key: col_meta.description for col_key, col_meta in columns.items()}