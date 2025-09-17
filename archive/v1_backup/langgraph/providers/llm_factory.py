"""
LLM Provider Factory
Centralizes LLM provider creation and management with fallback support
"""

import os
import logging
from typing import Optional, Dict, Any, Union
from enum import Enum

from .gemini_provider import GeminiProvider
from .openai_provider import OpenAIProvider
from .anthropic_provider import AnthropicProvider
from .ollama_provider import OllamaProvider

logger = logging.getLogger(__name__)

class LLMProviderType(Enum):
    """Supported LLM providers"""
    GEMINI = "gemini"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    OLLAMA = "ollama"

class LLMFactory:
    """Factory class for creating and managing LLM providers"""
    
    _providers = {}
    _fallback_order = [
        LLMProviderType.GEMINI,
        LLMProviderType.OPENAI,
        LLMProviderType.ANTHROPIC,
        LLMProviderType.OLLAMA
    ]
    
    @classmethod
    def create_provider(
        cls, 
        provider_type: Union[str, LLMProviderType],
        **kwargs
    ) -> Optional[Any]:
        """Create an LLM provider instance"""
        
        if isinstance(provider_type, str):
            try:
                provider_type = LLMProviderType(provider_type.lower())
            except ValueError:
                logger.error(f"Unknown provider type: {provider_type}")
                return None
        
        try:
            if provider_type == LLMProviderType.GEMINI:
                return GeminiProvider(**kwargs)
            elif provider_type == LLMProviderType.OPENAI:
                return OpenAIProvider(**kwargs)
            elif provider_type == LLMProviderType.ANTHROPIC:
                return AnthropicProvider(**kwargs)
            elif provider_type == LLMProviderType.OLLAMA:
                return OllamaProvider(**kwargs)
            else:
                logger.error(f"Unsupported provider type: {provider_type}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to create {provider_type.value} provider: {str(e)}")
            return None
    
    @classmethod
    def get_provider(
        cls, 
        provider_type: Optional[Union[str, LLMProviderType]] = None,
        enable_fallback: bool = True,
        **kwargs
    ) -> Optional[Any]:
        """
        Get an LLM provider with optional fallback support
        
        Args:
            provider_type: Specific provider to use (defaults to env DEFAULT_LLM_PROVIDER)
            enable_fallback: Whether to try fallback providers if primary fails
            **kwargs: Additional arguments passed to provider
        """
        
        # Determine primary provider
        if provider_type is None:
            provider_type = os.getenv("DEFAULT_LLM_PROVIDER", "gemini")
        
        if isinstance(provider_type, str):
            try:
                provider_type = LLMProviderType(provider_type.lower())
            except ValueError:
                logger.warning(f"Invalid provider type {provider_type}, using Gemini as default")
                provider_type = LLMProviderType.GEMINI
        
        # Check if already cached
        cache_key = f"{provider_type.value}_{hash(str(sorted(kwargs.items())))}"
        if cache_key in cls._providers:
            return cls._providers[cache_key]
        
        # Try primary provider
        provider = cls.create_provider(provider_type, **kwargs)
        if provider and cls._test_provider(provider):
            cls._providers[cache_key] = provider
            logger.info(f"Successfully initialized {provider_type.value} provider")
            return provider
        
        # Try fallback providers if enabled
        if enable_fallback:
            logger.warning(f"Primary provider {provider_type.value} failed, trying fallbacks...")
            
            for fallback_type in cls._fallback_order:
                if fallback_type == provider_type:
                    continue  # Skip the failed primary provider
                
                try:
                    fallback_provider = cls.create_provider(fallback_type, **kwargs)
                    if fallback_provider and cls._test_provider(fallback_provider):
                        cls._providers[cache_key] = fallback_provider
                        logger.info(f"Using fallback provider: {fallback_type.value}")
                        return fallback_provider
                except Exception as e:
                    logger.warning(f"Fallback provider {fallback_type.value} failed: {str(e)}")
                    continue
        
        logger.error("All LLM providers failed to initialize")
        return None
    
    @classmethod
    def _test_provider(cls, provider) -> bool:
        """Test if provider is working with a simple query"""
        try:
            # Simple test query
            test_response = provider.generate(
                "Respond with 'OK' if you can receive this message.",
                max_tokens=10,
                temperature=0
            )
            return test_response and len(test_response.strip()) > 0
        except Exception as e:
            logger.warning(f"Provider test failed: {str(e)}")
            return False
    
    @classmethod
    def list_available_providers(cls) -> Dict[str, bool]:
        """List all providers and their availability status"""
        status = {}
        
        for provider_type in LLMProviderType:
            try:
                provider = cls.create_provider(provider_type)
                status[provider_type.value] = provider is not None and cls._test_provider(provider)
            except Exception:
                status[provider_type.value] = False
        
        return status
    
    @classmethod
    def clear_cache(cls):
        """Clear provider cache"""
        cls._providers.clear()
        logger.info("Provider cache cleared")

# Convenience function for quick access
def get_llm_provider(
    provider_type: Optional[str] = None,
    enable_fallback: bool = True,
    **kwargs
) -> Optional[Any]:
    """
    Quick access function to get an LLM provider
    
    Args:
        provider_type: Provider name (gemini, openai, anthropic, ollama)
        enable_fallback: Enable fallback to other providers
        **kwargs: Additional provider arguments
    
    Returns:
        LLM provider instance or None if all providers fail
    """
    return LLMFactory.get_provider(
        provider_type=provider_type,
        enable_fallback=enable_fallback,
        **kwargs
    )

# Configuration helper
def get_provider_config(provider_type: str) -> Dict[str, Any]:
    """Get configuration for a specific provider from environment variables"""
    
    configs = {
        "gemini": {
            "api_key": os.getenv("GOOGLE_API_KEY"),
            "model": os.getenv("GEMINI_MODEL", "gemini-pro"),
            "temperature": float(os.getenv("GEMINI_TEMPERATURE", "0.1")),
            "max_tokens": int(os.getenv("GEMINI_MAX_TOKENS", "4000")),
            "top_p": float(os.getenv("GEMINI_TOP_P", "0.8")),
            "top_k": int(os.getenv("GEMINI_TOP_K", "10")),
        },
        "openai": {
            "api_key": os.getenv("OPENAI_API_KEY"),
            "model": os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview"),
            "temperature": float(os.getenv("OPENAI_TEMPERATURE", "0.1")),
            "max_tokens": int(os.getenv("OPENAI_MAX_TOKENS", "4000")),
        },
        "anthropic": {
            "api_key": os.getenv("ANTHROPIC_API_KEY"),
            "model": os.getenv("ANTHROPIC_MODEL", "claude-3-sonnet-20240229"),
            "temperature": float(os.getenv("ANTHROPIC_TEMPERATURE", "0.1")),
            "max_tokens": int(os.getenv("ANTHROPIC_MAX_TOKENS", "4000")),
        },
        "ollama": {
            "base_url": os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
            "model": os.getenv("OLLAMA_MODEL", "llama2:7b-chat"),
            "timeout": int(os.getenv("OLLAMA_TIMEOUT", "300")),
        }
    }
    
    return configs.get(provider_type, {})
