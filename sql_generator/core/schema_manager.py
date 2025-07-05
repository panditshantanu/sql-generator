"""
Schema Manager - Enterprise-grade schema-aware table and column selection.
Handles table relationships, confidence scoring, and filtering.
"""

from typing import Dict, List, Set, Optional, Tuple, Any
from dataclasses import dataclass
import logging
from pathlib import Path
from collections import defaultdict, deque

from .query_analyzer import QueryAnalyzer, QueryContext


@dataclass
class TableSelectionResult:
    """Result of table selection process."""
    selected_tables: List[str]
    confidence_scores: Dict[str, float]
    relationships: List[Tuple[str, str]]
    excluded_tables: List[str]
    selection_reasoning: str
    bridge_tables_added: List[str]  # Tables added to complete relationships


@dataclass
class ColumnSelectionResult:
    """Result of column selection process."""
    selected_columns: List[Dict[str, Any]]
    confidence_scores: Dict[str, float]
    table_distribution: Dict[str, int]
    selection_reasoning: str


@dataclass
class RelationshipGraph:
    """Graph representation of table relationships."""
    adjacency_list: Dict[str, Set[str]]
    relationship_metadata: Dict[Tuple[str, str], Dict[str, Any]]
    
    def add_relationship(self, table1: str, table2: str, metadata: Optional[Dict[str, Any]] = None):
        """Add a bidirectional relationship between two tables."""
        if table1 not in self.adjacency_list:
            self.adjacency_list[table1] = set()
        if table2 not in self.adjacency_list:
            self.adjacency_list[table2] = set()
        
        self.adjacency_list[table1].add(table2)
        self.adjacency_list[table2].add(table1)
        
        if metadata:
            self.relationship_metadata[(table1, table2)] = metadata
            self.relationship_metadata[(table2, table1)] = metadata


class SchemaManager:
    """
    Enterprise-grade schema manager that handles table and column selection
    using configurable rules and semantic search results.
    """
    
    def __init__(self, 
                 query_analyzer: Optional[QueryAnalyzer] = None,
                 config: Optional[Dict[str, Any]] = None):
        """
        Initialize schema manager.
        
        Args:
            query_analyzer: Query analyzer instance
            config: Configuration dictionary
        """
        self.query_analyzer = query_analyzer or QueryAnalyzer()
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Configuration defaults
        self.min_confidence = self.config.get('min_confidence_threshold', 0.5)
        self.max_tables = self.config.get('max_tables_per_query', 4)
        self.max_columns_per_table = self.config.get('max_columns_per_table', 3)
        self.enable_context_filtering = self.config.get('enable_context_filtering', True)
        self.enable_relationship_completion = self.config.get('enable_relationship_completion', True)
        
        # Build relationship graph from config
        self.relationship_graph = self._build_relationship_graph()
    
    def _build_relationship_graph(self) -> RelationshipGraph:
        """
        Build a complete relationship graph from configuration.
        Works with any schema by parsing table_patterns relationships.
        """
        graph = RelationshipGraph(
            adjacency_list=defaultdict(set),
            relationship_metadata={}
        )
        
        # Get table patterns from config
        table_patterns = self.config.get('table_patterns', [])
        
        for table_config in table_patterns:
            table_name = table_config.get('table_name')
            relationships = table_config.get('relationships', [])
            
            for relationship in relationships:
                # Parse relationship format: "target_table.column" or "target_table"
                if '.' in relationship:
                    target_table = relationship.split('.')[0]
                else:
                    target_table = relationship
                
                # Add bidirectional relationship
                graph.add_relationship(
                    table_name,
                    target_table,
                    {
                        'source_table': table_name,
                        'target_table': target_table,
                        'relationship_string': relationship,
                        'type': 'foreign_key' if '.' in relationship else 'direct'
                    }
                )
        
        self.logger.info(f"Built relationship graph with {len(graph.adjacency_list)} tables")
        return graph
    
    def _find_relationship_paths(self, table1: str, table2: str, max_depth: int = 3) -> List[List[str]]:
        """
        Find all paths between two tables using BFS.
        Returns list of paths (each path is a list of table names).
        """
        if table1 not in self.relationship_graph.adjacency_list or table2 not in self.relationship_graph.adjacency_list:
            return []
        
        if table1 == table2:
            return [[table1]]
        
        paths = []
        queue = deque([(table1, [table1])])
        visited_paths = set()
        
        while queue:
            current_table, path = queue.popleft()
            
            if len(path) > max_depth:
                continue
            
            # Create a path signature for deduplication
            path_signature = tuple(sorted(path))
            if path_signature in visited_paths:
                continue
            visited_paths.add(path_signature)
            
            for neighbor in self.relationship_graph.adjacency_list[current_table]:
                if neighbor == table2:
                    # Found target - complete path
                    complete_path = path + [neighbor]
                    paths.append(complete_path)
                elif neighbor not in path:  # Avoid cycles
                    new_path = path + [neighbor]
                    queue.append((neighbor, new_path))
        
        # Sort paths by length (prefer shorter paths)
        return sorted(paths, key=len)
    
    def _complete_table_relationships(self, selected_tables: List[str]) -> Tuple[List[str], List[str]]:
        """
        Complete table relationships by adding necessary bridge tables.
        Returns (completed_table_list, bridge_tables_added).
        
        This is fully generic and works with any schema configuration.
        """
        if not self.enable_relationship_completion or len(selected_tables) <= 1:
            return selected_tables, []
        
        bridge_tables = set()
        completed_tables = set(selected_tables)
        
        # Find shortest paths between all pairs of selected tables
        for i, table1 in enumerate(selected_tables):
            for table2 in selected_tables[i+1:]:
                paths = self._find_relationship_paths(table1, table2, max_depth=3)
                
                if paths:
                    # Use the shortest path
                    shortest_path = paths[0]
                    
                    # Add all intermediate tables (bridge tables)
                    for table in shortest_path[1:-1]:  # Exclude start and end tables
                        if table not in completed_tables:
                            bridge_tables.add(table)
                            completed_tables.add(table)
                            self.logger.info(f"Adding bridge table '{table}' to connect {table1} → {table2}")
        
        # Sort to ensure deterministic order
        completed_list = sorted(completed_tables)
        bridge_list = sorted(bridge_tables)
        
        return completed_list, bridge_list
    
    def select_tables(self, 
                     query: str,
                     semantic_results: Dict[str, List[Dict[str, Any]]],
                     available_tables: Optional[Set[str]] = None) -> TableSelectionResult:
        """
        Select relevant tables based on query analysis and semantic search.
        
        Args:
            query: Natural language query
            semantic_results: Results from semantic search
            available_tables: Set of available tables in schema
            
        Returns:
            TableSelectionResult with selected tables and reasoning
        """
        # Analyze query context
        context = self.query_analyzer.analyze_query(query)
        
        # Get tables from semantic search results
        semantic_tables = self._extract_tables_from_semantic_results(semantic_results)
        
        # Apply confidence filtering
        high_confidence_tables = self._filter_by_confidence(
            semantic_tables, 
            self.min_confidence
        )
        
        # Apply context-aware filtering
        if self.enable_context_filtering:
            filtered_tables = self._apply_context_filtering(
                high_confidence_tables, 
                context, 
                available_tables
            )
        else:
            filtered_tables = high_confidence_tables
        
        # Limit number of tables (before relationship completion)
        initial_tables = list(filtered_tables.keys())[:self.max_tables]
        
        # Complete relationships by adding bridge tables
        completed_tables, bridge_tables_added = self._complete_table_relationships(initial_tables)
        
        # Update confidence scores for bridge tables
        final_confidence_scores = dict(filtered_tables)
        for bridge_table in bridge_tables_added:
            # Assign minimum confidence to bridge tables
            final_confidence_scores[bridge_table] = self.min_confidence
        
        # Infer relationships using the completed table set
        relationships = self._infer_table_relationships(completed_tables, context)
        
        # Generate reasoning
        reasoning = self._generate_table_selection_reasoning(
            query, context, semantic_tables, filtered_tables, 
            initial_tables, completed_tables, bridge_tables_added
        )
        
        return TableSelectionResult(
            selected_tables=completed_tables,
            confidence_scores=final_confidence_scores,
            relationships=relationships,
            excluded_tables=list(context.excluded_tables),
            selection_reasoning=reasoning,
            bridge_tables_added=bridge_tables_added
        )
    
    def select_columns(self,
                      query: str,
                      semantic_results: Dict[str, List[Dict[str, Any]]],
                      selected_tables: List[str]) -> ColumnSelectionResult:
        """
        Select relevant columns based on query analysis and semantic search.
        
        Args:
            query: Natural language query
            semantic_results: Results from semantic search
            selected_tables: List of selected tables
            
        Returns:
            ColumnSelectionResult with selected columns and reasoning
        """
        # Get columns from semantic search results
        all_columns = semantic_results.get('columns', [])
        
        # Filter columns by confidence
        high_confidence_columns = [
            col for col in all_columns 
            if self._calculate_column_confidence(col) >= self.min_confidence
        ]
        
        # Filter columns to only include those from selected tables
        relevant_columns = [
            col for col in high_confidence_columns
            if col.get('table') in selected_tables
        ]
        
        # Distribute columns across tables
        distributed_columns = self._distribute_columns_across_tables(
            relevant_columns, 
            selected_tables
        )
        
        # Calculate confidence scores
        confidence_scores = {
            f"{col.get('table')}.{col.get('column')}": self._calculate_column_confidence(col)
            for col in distributed_columns
        }
        
        # Calculate table distribution
        table_distribution = {}
        for col in distributed_columns:
            table = col.get('table')
            table_distribution[table] = table_distribution.get(table, 0) + 1
        
        # Generate reasoning
        reasoning = self._generate_column_selection_reasoning(
            query, all_columns, distributed_columns, selected_tables
        )
        
        return ColumnSelectionResult(
            selected_columns=distributed_columns,
            confidence_scores=confidence_scores,
            table_distribution=table_distribution,
            selection_reasoning=reasoning
        )
    
    def _extract_tables_from_semantic_results(self, 
                                            semantic_results: Dict[str, List[Dict[str, Any]]]) -> Dict[str, float]:
        """Extract tables and their confidence scores from semantic results."""
        tables_scores = {}
        
        # Get tables from column results
        for col_result in semantic_results.get('columns', []):
            table = col_result.get('table')
            if table:
                score = self._calculate_column_confidence(col_result)
                if table not in tables_scores:
                    tables_scores[table] = score
                else:
                    # Use highest score for each table
                    tables_scores[table] = max(tables_scores[table], score)
        
        # Get tables from table results
        for table_result in semantic_results.get('tables', []):
            table = table_result.get('table')
            if table:
                score = self._calculate_table_confidence(table_result)
                if table not in tables_scores:
                    tables_scores[table] = score
                else:
                    # Combine scores (weighted average)
                    tables_scores[table] = (tables_scores[table] + score) / 2
        
        return tables_scores
    
    def _filter_by_confidence(self, 
                            tables_scores: Dict[str, float], 
                            min_confidence: float) -> Dict[str, float]:
        """Filter tables by minimum confidence threshold."""
        return {
            table: score 
            for table, score in tables_scores.items() 
            if score >= min_confidence
        }
    
    def _apply_context_filtering(self, 
                               tables_scores: Dict[str, float],
                               context: QueryContext,
                               available_tables: Optional[Set[str]]) -> Dict[str, float]:
        """Apply context-aware filtering to table selection."""
        filtered_tables = {}
        
        for table, score in tables_scores.items():
            # Skip if table is explicitly excluded by context
            if table in context.excluded_tables:
                self.logger.debug(f"Excluding table {table} based on query context")
                continue
            
            # Skip if table is not available in schema
            if available_tables and table not in available_tables:
                self.logger.debug(f"Excluding table {table} - not available in schema")
                continue
            
            # Boost score if table is suggested by context
            if table in context.suggested_tables:
                score = min(score + 0.1, 1.0)  # Boost but cap at 1.0
                self.logger.debug(f"Boosting score for suggested table {table}")
            
            filtered_tables[table] = score
        
        # Add required tables from context even if not in semantic results
        for required_table in context.suggested_tables:
            if (required_table not in filtered_tables and 
                (not available_tables or required_table in available_tables)):
                filtered_tables[required_table] = self.min_confidence
                self.logger.debug(f"Adding required table {required_table} from context")
        
        return filtered_tables
    
    def _calculate_column_confidence(self, column_result: Dict[str, Any]) -> float:
        """Calculate confidence score for a column result."""
        # This would use the same normalization logic as before
        # but extracted into a configurable method
        raw_score = column_result.get('score', 0)
        
        # Use absolute thresholds for semantic similarity scores
        if raw_score >= 0.8:
            return 0.9 + ((raw_score - 0.8) / 0.2) * 0.1
        elif raw_score >= 0.6:
            return 0.7 + ((raw_score - 0.6) / 0.2) * 0.2
        elif raw_score >= 0.4:
            return 0.4 + ((raw_score - 0.4) / 0.2) * 0.3
        elif raw_score >= 0.2:
            return 0.1 + ((raw_score - 0.2) / 0.2) * 0.3
        else:
            return (raw_score / 0.2) * 0.1
    
    def _calculate_table_confidence(self, table_result: Dict[str, Any]) -> float:
        """Calculate confidence score for a table result."""
        return self._calculate_column_confidence(table_result)  # Same logic for now
    
    def _distribute_columns_across_tables(self, 
                                        columns: List[Dict[str, Any]], 
                                        selected_tables: List[str]) -> List[Dict[str, Any]]:
        """Distribute column selection across tables."""
        distributed = []
        table_column_count = {table: 0 for table in selected_tables}
        
        # Sort columns by confidence score (descending)
        sorted_columns = sorted(
            columns, 
            key=lambda col: self._calculate_column_confidence(col), 
            reverse=True
        )
        
        for column in sorted_columns:
            table = column.get('table')
            if (table in selected_tables and 
                table_column_count[table] < self.max_columns_per_table):
                distributed.append(column)
                table_column_count[table] += 1
        
        return distributed
    
    def _infer_table_relationships(self, 
                                 selected_tables: List[str], 
                                 context: QueryContext) -> List[Tuple[str, str]]:
        """
        Infer actual relationships between selected tables using the relationship graph.
        This is fully generic and works with any schema configuration.
        """
        relationships = []
        
        # Get direct relationships from the graph
        for i, table1 in enumerate(selected_tables):
            for table2 in selected_tables[i+1:]:
                if (table1 in self.relationship_graph.adjacency_list and 
                    table2 in self.relationship_graph.adjacency_list[table1]):
                    # Direct relationship exists
                    relationships.append((table1, table2))
                    self.logger.debug(f"Found direct relationship: {table1} ↔ {table2}")
        
        # Also include relationships from context if they exist
        for rel in context.required_relationships:
            if '→' in rel:
                from_table, to_table = rel.split('→')
                from_table, to_table = from_table.strip(), to_table.strip()
                if from_table in selected_tables and to_table in selected_tables:
                    # Check if we haven't already added this relationship
                    if ((from_table, to_table) not in relationships and 
                        (to_table, from_table) not in relationships):
                        relationships.append((from_table, to_table))
        
        return relationships
    
    def _generate_table_selection_reasoning(self, 
                                          query: str,
                                          context: QueryContext,
                                          semantic_tables: Dict[str, float],
                                          filtered_tables: Dict[str, float],
                                          selected_tables: List[str],
                                          initial_tables: List[str],
                                          completed_tables: List[str],
                                          bridge_tables_added: List[str]) -> str:
        """Generate human-readable reasoning for table selection."""
        reasoning_parts = []
        
        reasoning_parts.append(f"Query Type: {context.query_type}")
        reasoning_parts.append(f"Semantic Search Found: {len(semantic_tables)} tables")
        reasoning_parts.append(f"After Confidence Filtering: {len(filtered_tables)} tables")
        reasoning_parts.append(f"Context Suggested: {len(context.suggested_tables)} tables")
        reasoning_parts.append(f"Context Excluded: {len(context.excluded_tables)} tables")
        reasoning_parts.append(f"Initial Selection: {initial_tables}")
        reasoning_parts.append(f"Completed Selection: {completed_tables}")
        
        if context.excluded_tables:
            reasoning_parts.append(f"Excluded Tables: {list(context.excluded_tables)}")
        
        if bridge_tables_added:
            reasoning_parts.append(f"Bridge Tables Added: {bridge_tables_added}")
        
        return " | ".join(reasoning_parts)
    
    def _generate_column_selection_reasoning(self,
                                           query: str,
                                           all_columns: List[Dict[str, Any]],
                                           selected_columns: List[Dict[str, Any]],
                                           selected_tables: List[str]) -> str:
        """Generate human-readable reasoning for column selection."""
        reasoning_parts = []
        
        reasoning_parts.append(f"Total Columns Found: {len(all_columns)}")
        reasoning_parts.append(f"High Confidence Columns: {len(selected_columns)}")
        reasoning_parts.append(f"Selected Tables: {selected_tables}")
        reasoning_parts.append(f"Max Columns Per Table: {self.max_columns_per_table}")
        
        return " | ".join(reasoning_parts)
