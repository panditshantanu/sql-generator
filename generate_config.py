#!/usr/bin/env python3
"""
Configuration Generator for SQL Generator
Creates domain-specific configuration files from templates.
"""

import json
import argparse
from pathlib import Path
from typing import Dict, List, Any


class ConfigurationGenerator:
    """Generates domain-specific configurations for SQL Generator."""
    
    def __init__(self):
        self.current_dir = Path(__file__).parent
        self.config_dir = self.current_dir / "data" / "config"
        self.template_path = self.config_dir / "query_analysis_config_template.json"
    
    def create_domain_config(self, 
                           domain_name: str,
                           tables: List[Dict[str, Any]],
                           query_patterns: List[Dict[str, Any]] = None,
                           domain_settings: Dict[str, Any] = None) -> str:
        """
        Create a domain-specific configuration file.
        
        Args:
            domain_name: Name of the domain (e.g., 'ecommerce', 'healthcare')
            tables: List of table definitions
            query_patterns: List of query pattern definitions
            domain_settings: Domain-specific settings
            
        Returns:
            Path to the created configuration file
        """
        # Load template
        if self.template_path.exists():
            with open(self.template_path, 'r') as f:
                config = json.load(f)
        else:
            config = self._get_default_template()
        
        # Update schema info
        config["schema_info"]["domain"] = domain_name
        config["schema_info"]["description"] = f"Configuration for {domain_name} domain"
        
        # Update table patterns
        config["table_patterns"] = tables
        
        # Update query patterns
        if query_patterns:
            config["query_patterns"] = query_patterns
        
        # Update domain config
        if domain_settings:
            config["domain_config"].update(domain_settings)
        
        # Save configuration
        output_path = self.config_dir / f"query_analysis_config_{domain_name}.json"
        with open(output_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        return str(output_path)
    
    def create_ecommerce_config(self) -> str:
        """Create configuration for e-commerce domain."""
        tables = [
            {
                "table_name": "customers",
                "keywords": ["customer", "client", "buyer", "person", "individual"],
                "aliases": ["cust", "customer", "c"],
                "relationships": ["orders.customer_id"],
                "exclusion_patterns": ["employee", "staff", "worker"]
            },
            {
                "table_name": "products",
                "keywords": ["product", "item", "goods", "merchandise", "inventory", "catalog"],
                "aliases": ["prod", "product", "p"],
                "relationships": ["order_items.product_id"],
                "exclusion_patterns": []
            },
            {
                "table_name": "orders",
                "keywords": ["order", "purchase", "transaction", "sale", "bought"],
                "aliases": ["ord", "order", "o"],
                "relationships": ["customers.customer_id", "order_items.order_id"],
                "exclusion_patterns": []
            },
            {
                "table_name": "order_items",
                "keywords": ["item", "line", "detail", "order_line"],
                "aliases": ["ord_item", "line_item", "oi"],
                "relationships": ["orders.order_id", "products.product_id"],
                "exclusion_patterns": []
            },
            {
                "table_name": "categories",
                "keywords": ["category", "group", "classification"],
                "aliases": ["cat", "category", "c"],
                "relationships": ["products.category_id"],
                "exclusion_patterns": []
            }
        ]
        
        query_patterns = [
            {
                "pattern_id": "customer_orders",
                "keywords": ["customer", "purchased", "bought", "ordered"],
                "required_tables": ["customers", "orders"],
                "optional_tables": ["order_items", "products"],
                "excluded_tables": [],
                "confidence_boost": 0.3
            },
            {
                "pattern_id": "product_analysis",
                "keywords": ["product", "item", "inventory", "stock", "catalog"],
                "required_tables": ["products"],
                "optional_tables": ["categories", "order_items"],
                "excluded_tables": [],
                "confidence_boost": 0.2
            },
            {
                "pattern_id": "sales_analysis",
                "keywords": ["sales", "revenue", "orders", "transactions"],
                "required_tables": ["orders", "order_items"],
                "optional_tables": ["customers", "products"],
                "excluded_tables": [],
                "confidence_boost": 0.2
            }
        ]
        
        return self.create_domain_config("ecommerce", tables, query_patterns)
    
    def create_healthcare_config(self) -> str:
        """Create configuration for healthcare domain."""
        tables = [
            {
                "table_name": "patients",
                "keywords": ["patient", "person", "individual", "client"],
                "aliases": ["pat", "patient", "p"],
                "relationships": ["appointments.patient_id", "medical_records.patient_id"],
                "exclusion_patterns": ["doctor", "physician", "staff"]
            },
            {
                "table_name": "doctors",
                "keywords": ["doctor", "physician", "provider", "practitioner"],
                "aliases": ["doc", "doctor", "d"],
                "relationships": ["appointments.doctor_id"],
                "exclusion_patterns": ["patient"]
            },
            {
                "table_name": "appointments",
                "keywords": ["appointment", "visit", "consultation", "exam"],
                "aliases": ["appt", "appointment", "a"],
                "relationships": ["patients.patient_id", "doctors.doctor_id"],
                "exclusion_patterns": []
            },
            {
                "table_name": "medical_records",
                "keywords": ["record", "history", "chart", "medical"],
                "aliases": ["record", "chart", "mr"],
                "relationships": ["patients.patient_id"],
                "exclusion_patterns": []
            }
        ]
        
        query_patterns = [
            {
                "pattern_id": "patient_care",
                "keywords": ["patient", "care", "treatment", "visit"],
                "required_tables": ["patients"],
                "optional_tables": ["appointments", "medical_records"],
                "excluded_tables": [],
                "confidence_boost": 0.3
            },
            {
                "pattern_id": "doctor_schedule",
                "keywords": ["doctor", "schedule", "appointments"],
                "required_tables": ["doctors", "appointments"],
                "optional_tables": ["patients"],
                "excluded_tables": [],
                "confidence_boost": 0.2
            }
        ]
        
        return self.create_domain_config("healthcare", tables, query_patterns)
    
    def create_financial_config(self) -> str:
        """Create configuration for financial domain."""
        tables = [
            {
                "table_name": "accounts",
                "keywords": ["account", "customer", "client", "holder"],
                "aliases": ["acc", "account", "a"],
                "relationships": ["transactions.account_id"],
                "exclusion_patterns": []
            },
            {
                "table_name": "transactions",
                "keywords": ["transaction", "payment", "transfer", "deposit", "withdrawal"],
                "aliases": ["txn", "transaction", "t"],
                "relationships": ["accounts.account_id"],
                "exclusion_patterns": []
            },
            {
                "table_name": "loans",
                "keywords": ["loan", "credit", "mortgage", "debt"],
                "aliases": ["loan", "l"],
                "relationships": ["accounts.account_id"],
                "exclusion_patterns": []
            }
        ]
        
        query_patterns = [
            {
                "pattern_id": "account_activity",
                "keywords": ["account", "balance", "activity", "transactions"],
                "required_tables": ["accounts", "transactions"],
                "optional_tables": [],
                "excluded_tables": [],
                "confidence_boost": 0.3
            },
            {
                "pattern_id": "loan_analysis",
                "keywords": ["loan", "credit", "debt", "payment"],
                "required_tables": ["loans"],
                "optional_tables": ["accounts"],
                "excluded_tables": [],
                "confidence_boost": 0.2
            }
        ]
        
        return self.create_domain_config("financial", tables, query_patterns)
    
    def _get_default_template(self) -> Dict[str, Any]:
        """Get default template if file doesn't exist."""
        return {
            "schema_info": {
                "domain": "generic",
                "description": "Generic domain configuration",
                "version": "1.0"
            },
            "table_patterns": [],
            "query_patterns": [],
            "domain_config": {
                "min_confidence_threshold": 0.5,
                "max_tables_per_query": 4,
                "max_columns_per_table": 3,
                "enable_relationship_inference": True,
                "strict_mode": False,
                "table_selection_strategy": "confidence_based",
                "enable_context_filtering": True
            }
        }


def main():
    """Command-line interface for configuration generation."""
    parser = argparse.ArgumentParser(description="Generate SQL Generator domain configurations")
    parser.add_argument("--domain", choices=["ecommerce", "healthcare", "financial"], 
                       help="Pre-built domain configuration to generate")
    parser.add_argument("--list-domains", action="store_true",
                       help="List available pre-built domain configurations")
    
    args = parser.parse_args()
    
    generator = ConfigurationGenerator()
    
    if args.list_domains:
        print("Available pre-built domain configurations:")
        print("  - ecommerce: E-commerce/retail domain")
        print("  - healthcare: Healthcare/medical domain")
        print("  - financial: Financial/banking domain")
        return
    
    if args.domain:
        if args.domain == "ecommerce":
            config_path = generator.create_ecommerce_config()
        elif args.domain == "healthcare":
            config_path = generator.create_healthcare_config()
        elif args.domain == "financial":
            config_path = generator.create_financial_config()
        
        print(f"✅ Created {args.domain} configuration: {config_path}")
        print(f"💡 To use this configuration:")
        print(f"   1. Review and customize the generated file")
        print(f"   2. Copy it to: data/config/query_analysis_config.json")
        print(f"   3. Restart your SQL Generator application")
    else:
        print("Please specify a domain with --domain or use --list-domains")
        print("Example: python generate_config.py --domain ecommerce")


if __name__ == "__main__":
    main()
