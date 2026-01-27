import uuid
import json
import redis
from fastapi import FastAPI, HTTPException

from models import RunRequest, Job, RunResult
from runtimes import RUNTIMES
from config import REDIS_HOST, REDIS_PORT, REDIS_TIMEOUT, JOB_TTL, QUEUE_NAME, JOB_KEY_PREFIX

app = FastAPI()

redis_client = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    decode_responses=True,
    socket_connect_timeout=REDIS_TIMEOUT,
    socket_timeout=REDIS_TIMEOUT,
)

@app.post("/run")
def submit_job(req: RunRequest):
    # 1. проверяем runtime
    if req.runtime not in RUNTIMES:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported runtime: {req.runtime}",
        )

    # 2. создаём job
    job_id = str(uuid.uuid4())

    job = Job(
        id=job_id,
        runtime=req.runtime,
        code=req.code,
        stdin=req.stdin,
        result=RunResult(
            stdout="",
            stderr="",
            returncode=None,
            status="queued",
        ),
    )

    # 3. сохраняем job
    redis_client.set(
        JOB_KEY_PREFIX + job_id,
        job.model_dump_json(),
        ex=JOB_TTL,
    )

    # 4. кладём job в очередь
    redis_client.lpush(QUEUE_NAME, job_id)

    # 5. возвращаем ответ
    return {
        "job_id": job_id,
        "status": "queued",
    }

@app.get("/jobs/{job_id}")
def get_job(job_id: str):
    raw = redis_client.get(JOB_KEY_PREFIX + job_id)

    if raw is None:
        raise HTTPException(
            status_code=404,
            detail="Job not found",
        )

    job = Job.model_validate_json(str(raw))
    return job


from fastapi.responses import HTMLResponse
from pathlib import Path

@app.get("/", response_class=HTMLResponse)
def index():
    return Path("index.html").read_text()