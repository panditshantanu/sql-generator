"""
Query Analyzer - Enterprise-grade query analysis and context detection.
Configurable patterns and rules for different domains and schemas.
"""

import re
from typing import Dict, List, Set, Optional, Any
from dataclasses import dataclass
import json
from pathlib import Path


@dataclass
class QueryContext:
    """Represents the analyzed context of a query."""
    query_type: str  # e.g., 'purchase', 'customer', 'product', 'employee'
    keywords: List[str]
    confidence: float
    suggested_tables: Set[str]
    excluded_tables: Set[str]
    required_relationships: List[str]


@dataclass
class TablePattern:
    """Pattern for identifying table relevance."""
    table_name: str
    keywords: List[str]
    aliases: List[str]
    relationships: List[str]
    exclusion_patterns: List[str]


@dataclass
class QueryPattern:
    """Pattern for query type detection."""
    pattern_id: str
    keywords: List[str]
    required_tables: List[str]
    optional_tables: List[str]
    excluded_tables: List[str]
    confidence_boost: float


class QueryAnalyzer:
    """
    Enterprise-grade query analyzer that uses configurable patterns
    instead of hard-coded business logic.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize with configuration file or defaults.
        
        Args:
            config_path: Path to query analysis configuration file
        """
        self.table_patterns: Dict[str, TablePattern] = {}
        self.query_patterns: Dict[str, QueryPattern] = {}
        self.domain_config: Dict[str, Any] = {}
        
        if config_path and Path(config_path).exists():
            self.load_config(config_path)
        else:
            self._load_default_config()
    
    def load_config(self, config_path: str):
        """Load configuration from JSON file."""
        try:
            with open(config_path, 'r') as f:
                self.config = json.load(f)
            
            # Load table patterns
            for table_config in self.config.get('table_patterns', []):
                pattern = TablePattern(**table_config)
                self.table_patterns[pattern.table_name] = pattern
            
            # Load query patterns
            for query_config in self.config.get('query_patterns', []):
                pattern = QueryPattern(**query_config)
                self.query_patterns[pattern.pattern_id] = pattern
            
            # Load domain configuration
            self.domain_config = self.config.get('domain_config', {})
            
        except Exception as e:
            print(f"Warning: Failed to load config from {config_path}: {e}")
            self._load_default_config()
    
    def _load_default_config(self):
        """Load minimal default configuration (domain-agnostic)."""
        # Default patterns - these should be overridden by config file
        self.query_patterns = {
            'generic_search': QueryPattern(
                pattern_id='generic_search',
                keywords=[],
                required_tables=[],
                optional_tables=[],
                excluded_tables=[],
                confidence_boost=0.0
            )
        }
        
        self.domain_config = {
            'min_confidence_threshold': 0.5,
            'max_tables_per_query': 5,
            'enable_relationship_inference': True,
            'strict_mode': False
        }
    
    def analyze_query(self, query: str) -> QueryContext:
        """
        Analyze a query and return context with suggested tables.
        
        Args:
            query: Natural language query
            
        Returns:
            QueryContext with analysis results
        """
        query_lower = query.lower()
        
        # Find matching query patterns
        best_pattern = None
        best_confidence = 0.0
        
        for pattern in self.query_patterns.values():
            confidence = self._calculate_pattern_confidence(query_lower, pattern)
            if confidence > best_confidence:
                best_confidence = confidence
                best_pattern = pattern
        
        # Determine suggested and excluded tables
        suggested_tables = set()
        excluded_tables = set()
        
        if best_pattern:
            suggested_tables.update(best_pattern.required_tables)
            suggested_tables.update(best_pattern.optional_tables)
            excluded_tables.update(best_pattern.excluded_tables)
        
        # Apply table-specific patterns
        for table_pattern in self.table_patterns.values():
            if self._matches_table_pattern(query_lower, table_pattern):
                suggested_tables.add(table_pattern.table_name)
            elif self._excluded_by_pattern(query_lower, table_pattern):
                excluded_tables.add(table_pattern.table_name)
        
        return QueryContext(
            query_type=best_pattern.pattern_id if best_pattern else 'generic',
            keywords=self._extract_keywords(query_lower),
            confidence=best_confidence,
            suggested_tables=suggested_tables,
            excluded_tables=excluded_tables,
            required_relationships=self._infer_relationships(suggested_tables)
        )
    
    def _calculate_pattern_confidence(self, query: str, pattern: QueryPattern) -> float:
        """Calculate confidence score for a query pattern."""
        if not pattern.keywords:
            return 0.0
        
        matches = sum(1 for keyword in pattern.keywords if keyword in query)
        confidence = matches / len(pattern.keywords)
        
        return min(confidence + pattern.confidence_boost, 1.0)
    
    def _matches_table_pattern(self, query: str, pattern: TablePattern) -> bool:
        """Check if query matches a table pattern."""
        if not pattern.keywords:
            return False
        
        return any(keyword in query for keyword in pattern.keywords)
    
    def _excluded_by_pattern(self, query: str, pattern: TablePattern) -> bool:
        """Check if table should be excluded based on patterns."""
        if not pattern.exclusion_patterns:
            return False
        
        return all(exclusion not in query for exclusion in pattern.exclusion_patterns)
    
    def _extract_keywords(self, query: str) -> List[str]:
        """Extract relevant keywords from query."""
        # Simple keyword extraction - can be enhanced
        words = re.findall(r'\w+', query)
        return [word for word in words if len(word) > 2]
    
    def _infer_relationships(self, tables: Set[str]) -> List[str]:
        """Infer required relationships between tables."""
        relationships = []
        
        if not self.domain_config.get('enable_relationship_inference', True):
            return relationships
        
        # This would be configurable based on schema metadata
        # For now, return empty list to avoid hard-coding
        return relationships
    
    def get_confidence_threshold(self) -> float:
        """Get minimum confidence threshold from configuration."""
        return self.domain_config.get('min_confidence_threshold', 0.5)
    
    def get_max_tables(self) -> int:
        """Get maximum tables per query from configuration."""
        return self.domain_config.get('max_tables_per_query', 5)
    
    def is_strict_mode(self) -> bool:
        """Check if strict mode is enabled."""
        return self.domain_config.get('strict_mode', False)
