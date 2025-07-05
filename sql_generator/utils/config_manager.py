import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
import logging


class Config:
    """Configuration manager for the SQL Generator project."""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize configuration.
        
        Args:
            config_path: Path to config file. If None, looks for config.json in current directory
        """
        self.config_path = self._find_config_file(config_path)
        self._config_data = self._load_config()
        self._setup_logging()
    
    def _find_config_file(self, config_path: Optional[str]) -> Path:
        """Find the configuration file."""
        if config_path:
            return Path(config_path)
        
        # Look for config.json in specific locations
        current_dir = Path(__file__).parent
        project_root = current_dir.parent.parent  # Go up to project root
        
        # Priority order for config file locations
        config_locations = [
            project_root / "data" / "config" / "config.json",  # New structure
            project_root / "config.json",                      # Project root
            current_dir / "config.json",                       # Current directory
            Path("config.json")                                # Working directory
        ]
        
        for config_file in config_locations:
            if config_file.exists():
                return config_file
        
        # Default to the preferred location
        return project_root / "data" / "config" / "config.json"
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file."""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            print(f"✅ Loaded configuration from: {self.config_path}")
            return config_data
        except FileNotFoundError:
            print(f"⚠️  Configuration file not found: {self.config_path}")
            return self._get_default_config()
        except json.JSONDecodeError as e:
            print(f"❌ Error parsing configuration file: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration."""
        return {
            "vector_store": {
                "persist_dir": "./chroma_db",
                "verbose": True
            },
            "embeddings": {
                "model_name": "all-MiniLM-L6-v2",
                "enable_caching": False,
                "cache_dir": "./embeddings_cache"
            },
            "schema": {
                "schema_path": "../../tables_schema.json"
            },
            "logging": {
                "level": "INFO",
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            }
        }
    
    def _setup_logging(self):
        """Setup logging based on configuration."""
        log_config = self.get("logging", {})
        level = getattr(logging, log_config.get("level", "INFO").upper())
        format_str = log_config.get("format", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        
        logging.basicConfig(level=level, format=format_str)
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """
        Get configuration value using dot notation.
        
        Args:
            key_path: Path to the configuration value (e.g., 'vector_store.persist_dir')
            default: Default value if key is not found
            
        Returns:
            Configuration value or default
        """
        keys = key_path.split('.')
        value = self._config_data
        
        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key_path: str, value: Any):
        """
        Set configuration value using dot notation.
        
        Args:
            key_path: Path to the configuration value (e.g., 'vector_store.persist_dir')
            value: Value to set
        """
        keys = key_path.split('.')
        config = self._config_data
        
        # Navigate to parent of target key
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]
        
        # Set the value
        config[keys[-1]] = value
    
    def save(self):
        """Save current configuration to file."""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self._config_data, f, indent=2, ensure_ascii=False)
            print(f"✅ Configuration saved to: {self.config_path}")
        except Exception as e:
            print(f"❌ Error saving configuration: {e}")
    
    def reload(self):
        """Reload configuration from file."""
        self._config_data = self._load_config()
        self._setup_logging()
    
    def get_vector_store_config(self) -> Dict[str, Any]:
        """Get vector store specific configuration."""
        return self.get("vector_store", {})
    
    def get_embeddings_config(self) -> Dict[str, Any]:
        """Get embeddings specific configuration."""
        return self.get("embeddings", {})
    
    def get_schema_config(self) -> Dict[str, Any]:
        """Get schema specific configuration."""
        return self.get("schema", {})
    
    def get_chroma_path(self) -> str:
        """Get ChromaDB persistence directory path."""
        persist_dir = self.get("vector_store.persist_dir", "./chroma_db")
        
        # Convert relative paths to absolute paths based on config file location
        if not os.path.isabs(persist_dir):
            config_dir = self.config_path.parent
            persist_dir = str(config_dir / persist_dir)
        
        return persist_dir
    
    def __repr__(self) -> str:
        """String representation of configuration."""
        return f"Config(config_path='{self.config_path}', data={self._config_data})"


# Global configuration instance
_config_instance = None


def get_config(config_path: Optional[str] = None) -> Config:
    """
    Get the global configuration instance.
    
    Args:
        config_path: Path to config file (only used for first call)
        
    Returns:
        Configuration instance
    """
    global _config_instance
    if _config_instance is None:
        _config_instance = Config(config_path)
    return _config_instance


def reload_config():
    """Reload the global configuration."""
    global _config_instance
    if _config_instance:
        _config_instance.reload()


if __name__ == "__main__":
    # Demo usage
    config = get_config()
    
    print("Configuration Demo")
    print("==================")
    print(f"ChromaDB path: {config.get_chroma_path()}")
    print(f"Model name: {config.get('embeddings.model_name')}")
    print(f"Enable caching: {config.get('embeddings.enable_caching')}")
    print(f"Schema path: {config.get('schema.schema_path')}")
    
    print("\nVector Store Config:")
    print(config.get_vector_store_config())
    
    print("\nEmbeddings Config:")
    print(config.get_embeddings_config())
