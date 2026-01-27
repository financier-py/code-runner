import os

# Redis configuration
REDIS_HOST = os.environ.get("REDIS_HOST", "redis")
REDIS_PORT = int(os.environ.get("REDIS_PORT", 6379))
REDIS_TIMEOUT = int(os.environ.get("REDIS_TIMEOUT", 5))  # seconds

# Job configuration
JOB_TTL = int(os.environ.get("JOB_TTL", 86400))  # 24 hours in seconds
JOB_POLL_INTERVAL = int(os.environ.get("JOB_POLL_INTERVAL", 500))  # milliseconds

# Queue configuration
QUEUE_NAME = "jobs_queue"
JOB_KEY_PREFIX = "job:"
