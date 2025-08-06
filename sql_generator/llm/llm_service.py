"""
LLM Service for SQL Generator - supports multiple LLM providers.
Handles API communication, response parsing, and error handling.
"""

import os
import json
import time
import logging
from typing import Dict, List, Optional, Any, Union
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path

# Import providers with fallbacks
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False


@dataclass
class LLMResponse:
    """Standardized LLM response structure."""
    sql_query: str
    raw_response: str
    provider: str
    model: str
    tokens_used: Optional[int] = None
    response_time: Optional[float] = None
    success: bool = True
    error: Optional[str] = None


@dataclass
class LLMConfig:
    """LLM configuration settings."""
    provider: str
    model: str
    api_key: str
    max_tokens: int = 1000
    temperature: float = 0.1
    timeout: int = 30
    max_retries: int = 3
    retry_delay: float = 1.0


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""
    
    def __init__(self, config: LLMConfig):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    @abstractmethod
    def generate_sql(self, prompt: str) -> LLMResponse:
        """Generate SQL from prompt."""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if provider is available and configured."""
        pass


class LocalLLMProvider(LLMProvider):
    """Local LLM provider (for Ollama, LM Studio, etc.)."""
    
    def __init__(self, config: LLMConfig):
        super().__init__(config)
        if not REQUESTS_AVAILABLE:
            raise ImportError("Requests package not installed. Run: pip install requests")
        
        # Use api_key as the base URL for local models
        self.base_url = config.api_key or "http://localhost:11434"  # Default Ollama URL
    
    def generate_sql(self, prompt: str) -> LLMResponse:
        """Generate SQL using local LLM."""
        start_time = time.time()
        
        try:
            # Ollama API format
            payload = {
                "model": self.config.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": self.config.temperature,
                    "num_predict": self.config.max_tokens
                }
            }
            
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=self.config.timeout
            )
            response.raise_for_status()
            
            response_time = time.time() - start_time
            result = response.json()
            raw_content = result.get("response", "").strip()
            
            # Extract SQL from response
            sql_query = self._extract_sql(raw_content)
            
            return LLMResponse(
                sql_query=sql_query,
                raw_response=raw_content,
                provider="local",
                model=self.config.model,
                response_time=response_time,
                success=True
            )
            
        except Exception as e:
            self.logger.error(f"Local LLM error: {e}")
            return LLMResponse(
                sql_query="",
                raw_response="",
                provider="local",
                model=self.config.model,
                response_time=time.time() - start_time,
                success=False,
                error=str(e)
            )
    
    def is_available(self) -> bool:
        """Check if local LLM is available."""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def _extract_sql(self, content: str) -> str:
        """Extract SQL query from response content."""
        content = content.strip()
        
        if content.startswith("```sql"):
            content = content[6:]
        elif content.startswith("```"):
            content = content[3:]
        
        if content.endswith("```"):
            content = content[:-3]
        
        prefixes_to_remove = [
            "SQL Query:",
            "Query:",
            "SQL:",
            "Here's the SQL query:",
            "The SQL query is:",
        ]
        
        for prefix in prefixes_to_remove:
            if content.startswith(prefix):
                content = content[len(prefix):].strip()
                break
        
        return content.strip()


class LLMService:
    """
    Main LLM service that manages multiple providers and handles fallbacks.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize LLM service with configuration.
        
        Args:
            config_path: Path to LLM configuration file
        """
        self.logger = logging.getLogger(__name__)
        self.providers: Dict[str, LLMProvider] = {}
        self.cache: Dict[str, LLMResponse] = {}
        
        # Load configuration
        self.config = self._load_config(config_path)
        self._initialize_providers()
    
    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Load LLM configuration from file or environment."""
        config = {
            "default_provider": "local",
            "providers": {
                "local": {
                    "model": "codellama:7b",
                    "api_key": "http://localhost:11434",  # Base URL for local
                    "max_tokens": 1000,
                    "temperature": 0.1,
                    "timeout": 60,
                    "max_retries": 3,
                    "retry_delay": 2.0
                }
            },
            "enable_caching": True,
            "fallback_providers": ["local"]
        }
        
        # Override with file config if provided
        if config_path and Path(config_path).exists():
            try:
                with open(config_path, 'r') as f:
                    file_config = json.load(f)
                    config.update(file_config)
            except Exception as e:
                self.logger.warning(f"Failed to load config from {config_path}: {e}")
        
        return config
    
    def _initialize_providers(self):
        """Initialize available LLM providers."""
        provider_classes = {
            "local": LocalLLMProvider
        }
        
        for provider_name, provider_config in self.config["providers"].items():
            if provider_name in provider_classes:
                try:
                    llm_config = LLMConfig(
                        provider=provider_name,
                        **provider_config
                    )
                    
                    provider = provider_classes[provider_name](llm_config)
                    if provider.is_available():
                        self.providers[provider_name] = provider
                        self.logger.info(f"Initialized {provider_name} provider")
                    else:
                        self.logger.warning(f"{provider_name} provider not available")
                
                except Exception as e:
                    self.logger.error(f"Failed to initialize {provider_name}: {e}")
    
    def generate_sql(
        self, 
        prompt: str, 
        preferred_provider: Optional[str] = None,
        use_cache: bool = True
    ) -> LLMResponse:
        """
        Generate SQL query from prompt using the best available provider.
        
        Args:
            prompt: SQL generation prompt
            preferred_provider: Preferred LLM provider name
            use_cache: Whether to use cached responses
            
        Returns:
            LLMResponse with generated SQL
        """
        # Check cache first
        if use_cache and self.config.get("enable_caching", True):
            cache_key = self._get_cache_key(prompt, preferred_provider)
            if cache_key in self.cache:
                self.logger.info("Using cached response")
                return self.cache[cache_key]
        
        # Determine provider order
        provider_order = self._get_provider_order(preferred_provider)
        
        for provider_name in provider_order:
            if provider_name not in self.providers:
                continue
            
            self.logger.info(f"Attempting SQL generation with {provider_name}")
            
            try:
                provider = self.providers[provider_name]
                response = self._generate_with_retry(provider, prompt)
                
                if response.success and response.sql_query:
                    # Cache successful response
                    if use_cache and self.config.get("enable_caching", True):
                        cache_key = self._get_cache_key(prompt, preferred_provider)
                        self.cache[cache_key] = response
                    
                    self.logger.info(f"Successfully generated SQL with {provider_name}")
                    return response
                else:
                    self.logger.warning(f"{provider_name} failed: {response.error}")
                    
            except Exception as e:
                self.logger.error(f"Error with {provider_name}: {e}")
                continue
        
        # All providers failed
        return LLMResponse(
            sql_query="",
            raw_response="",
            provider="none",
            model="none",
            success=False,
            error="All LLM providers failed"
        )
    
    def _generate_with_retry(self, provider: LLMProvider, prompt: str) -> LLMResponse:
        """Generate SQL with retry logic."""
        max_retries = provider.config.max_retries
        retry_delay = provider.config.retry_delay
        
        for attempt in range(max_retries + 1):
            try:
                response = provider.generate_sql(prompt)
                if response.success:
                    return response
                
                if attempt < max_retries:
                    self.logger.warning(f"Attempt {attempt + 1} failed, retrying in {retry_delay}s")
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                
            except Exception as e:
                if attempt < max_retries:
                    self.logger.warning(f"Attempt {attempt + 1} error: {e}, retrying")
                    time.sleep(retry_delay)
                    retry_delay *= 2
                else:
                    return LLMResponse(
                        sql_query="",
                        raw_response="",
                        provider=provider.config.provider,
                        model=provider.config.model,
                        success=False,
                        error=str(e)
                    )
        
        return LLMResponse(
            sql_query="",
            raw_response="",
            provider=provider.config.provider,
            model=provider.config.model,
            success=False,
            error="Max retries exceeded"
        )
    
    def _get_provider_order(self, preferred_provider: Optional[str]) -> List[str]:
        """Get provider order for fallback strategy."""
        if preferred_provider and preferred_provider in self.providers:
            # Start with preferred, then fallback order
            fallback_providers = self.config.get("fallback_providers", list(self.providers.keys()))
            order = [preferred_provider]
            for provider in fallback_providers:
                if provider != preferred_provider and provider in self.providers:
                    order.append(provider)
            return order
        else:
            # Use default order
            default_provider = self.config.get("default_provider", "openai")
            if default_provider in self.providers:
                fallback_providers = self.config.get("fallback_providers", list(self.providers.keys()))
                order = [default_provider]
                for provider in fallback_providers:
                    if provider != default_provider and provider in self.providers:
                        order.append(provider)
                return order
            else:
                return list(self.providers.keys())
    
    def _get_cache_key(self, prompt: str, provider: Optional[str]) -> str:
        """Generate cache key for prompt and provider."""
        import hashlib
        content = f"{prompt}:{provider or 'default'}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def get_available_providers(self) -> List[str]:
        """Get list of available providers."""
        return list(self.providers.keys())
    
    def health_check(self) -> Dict[str, bool]:
        """Check health of all providers."""
        health = {}
        for provider_name, provider in self.providers.items():
            try:
                health[provider_name] = provider.is_available()
            except Exception:
                health[provider_name] = False
        return health
    
    def clear_cache(self):
        """Clear response cache."""
        self.cache.clear()
        self.logger.info("Cache cleared")


# Convenience functions
def create_llm_service(config_path: Optional[str] = None) -> LLMService:
    """Create and configure LLM service."""
    return LLMService(config_path)


def quick_sql_generation(prompt: str, provider: str = "openai") -> str:
    """Quick SQL generation function for simple use cases."""
    service = create_llm_service()
    response = service.generate_sql(prompt, preferred_provider=provider)
    return response.sql_query if response.success else f"Error: {response.error}"
