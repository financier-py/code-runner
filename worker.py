import redis
import time

from models import Job, RunResult
from runner import run_job
from config import REDIS_HOST, REDIS_PORT, REDIS_TIMEOUT, JOB_TTL, QUEUE_NAME, JOB_KEY_PREFIX

def get_redis() -> redis.Redis:
    return redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        decode_responses=True,
        socket_connect_timeout=REDIS_TIMEOUT,
        socket_timeout=REDIS_TIMEOUT,
    )

def load_job(r: redis.Redis, job_id: str) -> Job:
    raw = r.get(JOB_KEY_PREFIX + job_id)
    if raw is None:
        raise RuntimeError(f"Job {job_id} not found")

    return Job.model_validate_json(str(raw))

def save_job(r: redis.Redis, job: Job) -> None:
    r.set(
        JOB_KEY_PREFIX + job.id,
        job.model_dump_json(),
        ex=JOB_TTL,
    )


def process_job(r: redis.Redis, job_id: str) -> None:
    job = load_job(r, job_id)

    # помечаем, что job выполняется
    job.result = RunResult(
        stdout="",
        stderr="",
        returncode=None,
        status="running",
    )
    save_job(r, job)

    # выполняем
    result = run_job(
        runtime_name=job.runtime,
        code=job.code,
        stdin=job.stdin,
    )

    # сохраняем результат
    job.result = result
    save_job(r, job)


def worker_loop() -> None:
    r = get_redis()
    print("Worker started")

    while True:
        try:
            # блокирующее ожидание job
            print("Worker loop alive", flush=True)
            result = r.brpop(QUEUE_NAME, timeout=10)  # type: ignore # таймаут 10 сек
            if result is None:
                continue
            _, job_id = result # type: ignore
            print("Got job", job_id, flush=True)
            process_job(r, job_id)

        except Exception as e:
            # worker НЕ должен падать
            print("Worker error:", e)
            time.sleep(1)


if __name__ == "__main__":
    worker_loop()