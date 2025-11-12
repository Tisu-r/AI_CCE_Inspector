"""
Caching utilities for AI responses.

Provides disk-based caching to reduce API costs and improve response times.
"""

import json
import hashlib
import time
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime, timedelta


class ResponseCache:
    """
    Disk-based cache for AI responses.

    Uses SHA-256 hash of prompt as cache key.
    """

    def __init__(self, cache_dir: Path, ttl: int = 86400, enabled: bool = True):
        """
        Initialize response cache.

        Args:
            cache_dir: Directory for cache files
            ttl: Time-to-live in seconds (default: 24 hours)
            enabled: Whether caching is enabled
        """
        self.cache_dir = cache_dir
        self.ttl = ttl
        self.enabled = enabled

        if self.enabled:
            self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _get_cache_key(self, prompt: str, system_prompt: Optional[str] = None, model: str = "") -> str:
        """
        Generate cache key from prompt and system prompt.

        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            model: Model name

        Returns:
            str: SHA-256 hash as cache key
        """
        # Combine all inputs that affect the response
        content = f"{model}||{system_prompt or ''}||{prompt}"
        return hashlib.sha256(content.encode('utf-8')).hexdigest()

    def _get_cache_path(self, cache_key: str) -> Path:
        """
        Get file path for cache entry.

        Args:
            cache_key: Cache key hash

        Returns:
            Path: Cache file path
        """
        # Use first 2 chars of hash as subdirectory for better file distribution
        subdir = cache_key[:2]
        cache_subdir = self.cache_dir / subdir
        cache_subdir.mkdir(parents=True, exist_ok=True)
        return cache_subdir / f"{cache_key}.json"

    def get(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        model: str = ""
    ) -> Optional[Dict[str, Any]]:
        """
        Retrieve cached response.

        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            model: Model name

        Returns:
            Cached response dict or None if not found/expired
        """
        if not self.enabled:
            return None

        cache_key = self._get_cache_key(prompt, system_prompt, model)
        cache_path = self._get_cache_path(cache_key)

        if not cache_path.exists():
            return None

        try:
            with open(cache_path, 'r', encoding='utf-8') as f:
                cached_data = json.load(f)

            # Check if cache entry has expired
            cached_time = cached_data.get('timestamp', 0)
            if time.time() - cached_time > self.ttl:
                # Cache expired, delete it
                cache_path.unlink()
                return None

            return cached_data.get('response')

        except (json.JSONDecodeError, KeyError, OSError):
            # If cache file is corrupted, delete it
            if cache_path.exists():
                cache_path.unlink()
            return None

    def set(
        self,
        prompt: str,
        response: Dict[str, Any],
        system_prompt: Optional[str] = None,
        model: str = ""
    ) -> None:
        """
        Store response in cache.

        Args:
            prompt: User prompt
            response: Response data to cache
            system_prompt: Optional system prompt
            model: Model name
        """
        if not self.enabled:
            return

        cache_key = self._get_cache_key(prompt, system_prompt, model)
        cache_path = self._get_cache_path(cache_key)

        cache_entry = {
            'timestamp': time.time(),
            'model': model,
            'response': response
        }

        try:
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(cache_entry, f, ensure_ascii=False, indent=2)
        except OSError:
            # If write fails, just continue without caching
            pass

    def clear(self) -> int:
        """
        Clear all cached entries.

        Returns:
            int: Number of entries cleared
        """
        if not self.enabled or not self.cache_dir.exists():
            return 0

        count = 0
        for cache_file in self.cache_dir.rglob("*.json"):
            try:
                cache_file.unlink()
                count += 1
            except OSError:
                pass

        return count

    def clear_expired(self) -> int:
        """
        Clear only expired cache entries.

        Returns:
            int: Number of expired entries cleared
        """
        if not self.enabled or not self.cache_dir.exists():
            return 0

        count = 0
        current_time = time.time()

        for cache_file in self.cache_dir.rglob("*.json"):
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cached_data = json.load(f)

                cached_time = cached_data.get('timestamp', 0)
                if current_time - cached_time > self.ttl:
                    cache_file.unlink()
                    count += 1

            except (json.JSONDecodeError, KeyError, OSError):
                # If file is corrupted, delete it
                try:
                    cache_file.unlink()
                    count += 1
                except OSError:
                    pass

        return count

    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.

        Returns:
            Dict with cache stats (total entries, total size, oldest/newest entry)
        """
        if not self.enabled or not self.cache_dir.exists():
            return {
                'enabled': False,
                'total_entries': 0,
                'total_size_bytes': 0,
                'total_size_mb': 0.0
            }

        total_entries = 0
        total_size = 0
        oldest_time = None
        newest_time = None
        expired_count = 0

        current_time = time.time()

        for cache_file in self.cache_dir.rglob("*.json"):
            try:
                file_size = cache_file.stat().st_size
                total_size += file_size
                total_entries += 1

                with open(cache_file, 'r', encoding='utf-8') as f:
                    cached_data = json.load(f)

                cached_time = cached_data.get('timestamp', 0)

                if oldest_time is None or cached_time < oldest_time:
                    oldest_time = cached_time

                if newest_time is None or cached_time > newest_time:
                    newest_time = cached_time

                if current_time - cached_time > self.ttl:
                    expired_count += 1

            except (json.JSONDecodeError, KeyError, OSError):
                pass

        stats = {
            'enabled': True,
            'total_entries': total_entries,
            'expired_entries': expired_count,
            'total_size_bytes': total_size,
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'ttl_hours': self.ttl / 3600
        }

        if oldest_time:
            stats['oldest_entry'] = datetime.fromtimestamp(oldest_time).isoformat()
        if newest_time:
            stats['newest_entry'] = datetime.fromtimestamp(newest_time).isoformat()

        return stats


# Global cache instance
_cache: Optional[ResponseCache] = None


def get_cache(cache_dir: Path = None, ttl: int = 86400, enabled: bool = True) -> ResponseCache:
    """
    Get or create the global cache instance.

    Args:
        cache_dir: Cache directory
        ttl: Time-to-live in seconds
        enabled: Whether caching is enabled

    Returns:
        ResponseCache: Global cache instance
    """
    global _cache

    if _cache is None:
        if cache_dir is None:
            cache_dir = Path.cwd() / ".cache"
        _cache = ResponseCache(cache_dir, ttl, enabled)

    return _cache


def configure_cache_from_config(config) -> ResponseCache:
    """
    Configure cache from CCEConfig instance.

    Args:
        config: CCEConfig instance

    Returns:
        ResponseCache: Configured cache instance
    """
    return get_cache(
        cache_dir=config.cache_dir,
        ttl=config.cache_ttl,
        enabled=config.enable_cache
    )
