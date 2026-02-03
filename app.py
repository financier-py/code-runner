import uuid
import json
import redis
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

import crud
from models import RunRequest, Job, RunResult, ShareRequest
from database import engine, Base, SessionLocal, get_db
from runtimes import RUNTIMES
from config import REDIS_HOST, REDIS_PORT, REDIS_TIMEOUT, JOB_TTL, QUEUE_NAME, JOB_KEY_PREFIX


async def cleanup_task():
    """Фоновая задача очистки."""
    while True:
        await asyncio.sleep(86400) # Спим сутки
        try:
            async with SessionLocal() as session:
                await crud.delete_expired_snippets(session)
        except Exception as e:
            print(f"Cleanup error: {e}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Работа с БД: Создаем таблицы
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # 2. Запуск фоновых процессов
    task = asyncio.create_task(cleanup_task())
    
    yield # Здесь приложение работает и принимает запросы
    
    # 3. Завершение работы
    task.cancel() # Останавливаем фоновую задачу
    await engine.dispose() # Закрываем базу

app = FastAPI(lifespan=lifespan)

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
    # Для главной страницы ставим дефолтные теги
    html = Path("index.html").read_text(encoding="utf-8")
    html = html.replace('{{TITLE}}', 'Code Runner - Запускай код онлайн')
    html = html.replace('{{DESCRIPTION}}', 'Облачная песочница для Python, C, C++ и Node.js')
    return html
    
@app.post("/share")
async def share_code(
    req: ShareRequest, 
    db: AsyncSession = Depends(get_db) # Получаем сессию SQLAlchemy
):
    snippet_id = await crud.create_snippet(db, req)
    return {"id": snippet_id, "url": f"/s/{snippet_id}"}

@app.get("/s/{snippet_id}", response_class=HTMLResponse)
async def get_snippet_page(
    snippet_id: str, 
    db: AsyncSession = Depends(get_db)
):
    snippet = await crud.get_snippet(db, snippet_id)
    
    if not snippet:
        raise HTTPException(status_code=404, detail="Snippet not found")
    
    # Готовим данные
    runtime_name = snippet.runtime.split(":")[0].upper() # Из 'python:3.11' сделает 'PYTHON'
    code_preview = snippet.code[:100].replace("\n", " ") # Берем первые 100 символов для описания
    
    preloaded_data = json.dumps({"runtime": snippet.runtime, "code": snippet.code})
    
    # Читаем HTML
    html = Path("index.html").read_text(encoding="utf-8")
    
    # 1. Вставляем код в редактор (как было)
    html = html.replace('const PRELOADED_DATA = null;', f'const PRELOADED_DATA = {preloaded_data};')
    
    # 2. Вставляем красивые мета-теги
    html = html.replace('{{TITLE}}', f'Code Runner | {runtime_name} Snippet')
    html = html.replace('{{DESCRIPTION}}', f'Посмотри мой код: {code_preview}...')
    
    return html