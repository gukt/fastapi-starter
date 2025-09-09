import json
import logging
import pickle
from typing import Any

import redis

from app.core.config import settings

logger = logging.getLogger(__name__)


class RedisCache:
    """Redis缓存管理器"""

    def __init__(self):
        self.redis_client = redis.Redis.from_url(
            settings.redis_url,
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5
        )
        self.default_timeout = 3600  # 默认1小时过期

    async def get(self, key: str) -> Any | None:
        """获取缓存值"""
        try:
            value = self.redis_client.get(key)
            if value is None:
                return None

            # 尝试解析JSON
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                # 如果不是JSON，返回原始值
                return value
        except Exception as e:
            logger.error(f"Redis GET error: {e}")
            return None

    async def set(
        self,
        key: str,
        value: Any,
        timeout: int | None = None,
        use_json: bool = True
    ) -> bool:
        """设置缓存值"""
        try:
            if timeout is None:
                timeout = self.default_timeout

            # 序列化值
            if use_json:
                try:
                    serialized_value = json.dumps(value, ensure_ascii=False)
                except (TypeError, ValueError):
                    # 如果不能序列化为JSON，使用pickle
                    serialized_value = pickle.dumps(value)
                    use_json = False
            else:
                serialized_value = value

            # 设置缓存
            if use_json:
                result = self.redis_client.setex(key, timeout, serialized_value)
            else:
                result = self.redis_client.setex(key, timeout, pickle.dumps(value))

            return result
        except Exception as e:
            logger.error(f"Redis SET error: {e}")
            return False

    async def delete(self, key: str) -> bool:
        """删除缓存值"""
        try:
            result = self.redis_client.delete(key)
            return result > 0
        except Exception as e:
            logger.error(f"Redis DELETE error: {e}")
            return False

    async def exists(self, key: str) -> bool:
        """检查键是否存在"""
        try:
            return self.redis_client.exists(key) > 0
        except Exception as e:
            logger.error(f"Redis EXISTS error: {e}")
            return False

    async def expire(self, key: str, timeout: int) -> bool:
        """设置键的过期时间"""
        try:
            return self.redis_client.expire(key, timeout)
        except Exception as e:
            logger.error(f"Redis EXPIRE error: {e}")
            return False

    async def ttl(self, key: str) -> int:
        """获取键的剩余生存时间"""
        try:
            return self.redis_client.ttl(key)
        except Exception as e:
            logger.error(f"Redis TTL error: {e}")
            return -1

    async def clear_pattern(self, pattern: str) -> int:
        """清除匹配模式的所有键"""
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                return self.redis_client.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Redis CLEAR_PATTERN error: {e}")
            return 0

    async def increment(self, key: str, amount: int = 1) -> int | None:
        """递增键的值"""
        try:
            return self.redis_client.incr(key, amount)
        except Exception as e:
            logger.error(f"Redis INCREMENT error: {e}")
            return None

    async def decrement(self, key: str, amount: int = 1) -> int | None:
        """递减键的值"""
        try:
            return self.redis_client.decr(key, amount)
        except Exception as e:
            logger.error(f"Redis DECREMENT error: {e}")
            return None

    async def get_keys(self, pattern: str = "*") -> list:
        """获取匹配模式的所有键"""
        try:
            return self.redis_client.keys(pattern)
        except Exception as e:
            logger.error(f"Redis KEYS error: {e}")
            return []

    async def close(self):
        """关闭Redis连接"""
        try:
            self.redis_client.close()
        except Exception as e:
            logger.error(f"Redis CLOSE error: {e}")


# 全局Redis缓存实例
redis_cache = RedisCache()


class CacheKeyBuilder:
    """缓存键构建器"""

    @staticmethod
    def build_key(prefix: str, *args, **kwargs) -> str:
        """构建缓存键"""
        parts = [prefix]
        parts.extend(str(arg) for arg in args)
        if kwargs:
            sorted_kwargs = sorted(kwargs.items())
            parts.extend(f"{k}={v}" for k, v in sorted_kwargs)
        return ":".join(parts)

    @staticmethod
    def user_cache_key(user_id: str | int) -> str:
        """用户缓存键"""
        return CacheKeyBuilder.build_key("user", user_id)

    @staticmethod
    def post_cache_key(post_id: str | int) -> str:
        """文章缓存键"""
        return CacheKeyBuilder.build_key("post", post_id)

    @staticmethod
    def posts_list_cache_key(page: int, size: int, **filters) -> str:
        """文章列表缓存键"""
        return CacheKeyBuilder.build_key("posts", "list", page, size, **filters)

    @staticmethod
    def rate_limit_key(identifier: str, endpoint: str) -> str:
        """速率限制键"""
        return CacheKeyBuilder.build_key("rate_limit", identifier, endpoint)
