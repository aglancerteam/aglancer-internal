import json
import os
import redis

REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
QUEUE_NAME = os.getenv("QUEUE_NAME", "aglancer_jobs")


def get_redis():
    return redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)


def enqueue_job(job_data: dict):
    r = get_redis()
    r.rpush(QUEUE_NAME, json.dumps(job_data))


def dequeue_job(timeout: int = 5):
    r = get_redis()
    item = r.blpop(QUEUE_NAME, timeout=timeout)
    if not item:
        return None
    _, payload = item
    return json.loads(payload)