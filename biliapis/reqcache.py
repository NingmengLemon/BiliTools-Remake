import sqlite3
import hashlib
import time
import threading
import atexit
import logging
import os
import pickle

DEFAULT_DB_PATH = "./bilicache.db"

__all__ = ["cache", "init"]


class _RequestCache:
    # mainly powered by ChatGPT w
    def __init__(self, db_name: str, expire_time: int):
        self.db_name = db_name
        self.expire_time = expire_time  # 缓存过期时间（秒）
        self._lock = threading.Lock()
        self._last_vacuum = 0.0

        # 确保数据库表已创建
        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                """-- sql
                CREATE TABLE IF NOT EXISTS cache (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    hash_key TEXT UNIQUE,
                    response BLOB,
                    timestamp INTEGER
                )
            """
            )
            conn.commit()
        self.clear_expired()
        atexit.register(self.clear_expired)
        logging.info("cache db init")

    def _get_connection(self):
        """为每个线程创建一个新的数据库连接"""
        return sqlite3.connect(self.db_name)

    def _generate_hash_key(self, request_params):
        """生成请求参数的哈希值"""
        hash_key = hashlib.sha256(str(request_params).encode("utf-8")).hexdigest()
        return hash_key

    def get(self, request_params):
        """获取缓存"""
        hash_key = self._generate_hash_key(request_params)
        with self._lock:
            with self._get_connection() as conn:
                cur = conn.cursor()
                cur.execute(
                    "SELECT response, timestamp FROM cache WHERE hash_key = ?",
                    (hash_key,),
                )
                result = cur.fetchone()

                if result:
                    response, timestamp = result
                    # 检查缓存是否过期
                    if time.time() - timestamp < self.expire_time:
                        logging.debug("cache found, ok: %s", hash_key)
                        return pickle.loads(response)
                    else:
                        # 缓存过期，删除记录
                        cur.execute("DELETE FROM cache WHERE hash_key = ?", (hash_key,))
                        conn.commit()
                        logging.debug("cache expired, deleted: %s", hash_key)
                        return None
                return None

    def vacuum(self):
        with self._lock:
            if time.time() - self._last_vacuum < 2 * 60:
                logging.debug("skip vacuum due to too-small interval")
                return
            with self._get_connection() as conn:
                cur = conn.cursor()
                cur.execute("VACUUM")
                conn.commit()
            self._last_vacuum = time.time()
        logging.debug("vacuumed cache")

    def set(self, request_params, response):
        """设置缓存"""
        hash_key = self._generate_hash_key(request_params)
        timestamp = int(time.time())
        with self._lock:
            with self._get_connection() as conn:
                cur = conn.cursor()
                cur.execute(
                    """-- sql
                    INSERT OR REPLACE INTO cache (hash_key, response, timestamp)
                    VALUES (?, ?, ?)
                """,
                    (hash_key, pickle.dumps(response), timestamp),
                )
                conn.commit()
        logging.debug("cache set: %s", hash_key)
        if os.path.getsize(self.db_name) > 128 * 1024 * 1024:
            self.clear_expired()

    def clear(self):
        """清理所有缓存"""
        with self._lock:
            with self._get_connection() as conn:
                cur = conn.cursor()
                cur.execute("DELETE FROM cache")
                conn.commit()
        logging.debug("clear all cache")
        self.vacuum()

    def clear_expired(self):
        """清理过期缓存"""
        current_time = int(time.time())
        with self._lock:
            with self._get_connection() as conn:
                cur = conn.cursor()
                cur.execute(
                    "DELETE FROM cache WHERE ? - timestamp > ?",
                    (current_time, self.expire_time),
                )
                deleted_rows = cur.rowcount
                conn.commit()
                logging.debug("cleared expired cache: %d items", deleted_rows)
        if deleted_rows > 0:
            self.vacuum()


cache: _RequestCache | None = None


def init(db_name: str = DEFAULT_DB_PATH, expire_time: int = 60 * 5):
    global cache
    if not cache:
        cache = _RequestCache(db_name, expire_time)
