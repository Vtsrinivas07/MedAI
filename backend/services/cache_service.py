from config.redis import redis_client
from typing import Optional, Any
import hashlib
import json


class CacheService:
    """Service for caching expensive operations"""
    
    @staticmethod
    def generate_cache_key(prefix: str, *args, **kwargs) -> str:
        """Generate unique cache key from arguments"""
        key_data = f"{prefix}:{str(args)}:{str(sorted(kwargs.items()))}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    @staticmethod
    async def get_chat_response(user_message: str) -> Optional[str]:
        """Get cached chatbot response"""
        cache_key = f"chat:{hashlib.md5(user_message.encode()).hexdigest()}"
        return await redis_client.get(cache_key)
    
    @staticmethod
    async def set_chat_response(user_message: str, response: str, expire: int = 3600):
        """Cache chatbot response (1 hour default)"""
        cache_key = f"chat:{hashlib.md5(user_message.encode()).hexdigest()}"
        await redis_client.set(cache_key, response, expire)
    
    @staticmethod
    async def get_rag_result(query: str) -> Optional[dict]:
        """Get cached RAG search result"""
        cache_key = f"rag:{hashlib.md5(query.encode()).hexdigest()}"
        return await redis_client.get(cache_key)
    
    @staticmethod
    async def set_rag_result(query: str, result: dict, expire: int = 7200):
        """Cache RAG result (2 hours default)"""
        cache_key = f"rag:{hashlib.md5(query.encode()).hexdigest()}"
        await redis_client.set(cache_key, result, expire)
    
    @staticmethod
    async def get_health_analytics(user_id: str) -> Optional[dict]:
        """Get cached health analytics"""
        cache_key = f"analytics:{user_id}"
        return await redis_client.get(cache_key)
    
    @staticmethod
    async def set_health_analytics(user_id: str, analytics: dict, expire: int = 1800):
        """Cache health analytics (30 minutes default)"""
        cache_key = f"analytics:{user_id}"
        await redis_client.set(cache_key, analytics, expire)
    
    @staticmethod
    async def invalidate_user_cache(user_id: str):
        """Clear all cache for a user (call after data updates)"""
        await redis_client.clear_pattern(f"analytics:{user_id}*")
        await redis_client.clear_pattern(f"chat:{user_id}*")
    
    @staticmethod
    async def get_medicine_reminders(user_id: str) -> Optional[list]:
        """Get cached medicine reminders"""
        cache_key = f"reminders:{user_id}"
        return await redis_client.get(cache_key)
    
    @staticmethod
    async def set_medicine_reminders(user_id: str, reminders: list, expire: int = 3600):
        """Cache medicine reminders (1 hour default)"""
        cache_key = f"reminders:{user_id}"
        await redis_client.set(cache_key, reminders, expire)
    
    @staticmethod
    async def cache_transformers_result(text: str, model_name: str, result: Any, expire: int = 86400):
        """Cache Hugging Face Transformers analysis (24 hours)"""
        cache_key = f"transformers:{model_name}:{hashlib.md5(text.encode()).hexdigest()}"
        await redis_client.set(cache_key, result, expire)
    
    @staticmethod
    async def get_transformers_result(text: str, model_name: str) -> Optional[Any]:
        """Get cached Transformers analysis"""
        cache_key = f"transformers:{model_name}:{hashlib.md5(text.encode()).hexdigest()}"
        return await redis_client.get(cache_key)


# Global cache service instance
cache_service = CacheService()
