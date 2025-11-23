from dotenv import load_dotenv
import os
from redis.asyncio import Redis

load_dotenv()


class RedisClient:
    def __init__(self):
        self.redis: Redis = Redis(
            host=os.getenv('REDIS_HOST'),
            port=int(os.getenv('REDIS_PORT')),
            db=int(os.getenv('REDIS_DB')),
        )

    async def setex(self, key: str, value: str, time: int):
        await self.redis.setex(key, time, value)

    async def get(self, key: str):
        return await self.redis.get(key)


redis_client = RedisClient()
