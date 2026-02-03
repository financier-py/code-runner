import secrets
import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from db_models import Snippet
from models import ShareRequest

async def create_snippet(db: AsyncSession, req: ShareRequest) -> str:
    snippet_id = secrets.token_urlsafe(4).replace("-", "").replace("_", "")
    
    # Создаем объект модели
    new_snippet = Snippet(
        id=snippet_id,
        runtime=req.runtime,
        code=req.code
    )
    
    db.add(new_snippet)  # Добавляем в сессию
    await db.commit()     # Фиксируем изменения в БД
    return snippet_id

async def get_snippet(db: AsyncSession, snippet_id: str):
    # Современный синтаксис SQLAlchemy 2.0 (select)
    result = await db.execute(select(Snippet).where(Snippet.id == snippet_id))
    return result.scalar_one_or_none() # Возвращает объект Snippet или None
    
async def delete_expired_snippets(db: AsyncSession, days: int = 30):
    """Удаляет сниппеты, созданные более чем 'days' назад."""
    threshold = datetime.datetime.now() - datetime.timedelta(days=days)
    
    # Формируем запрос на удаление
    query = delete(Snippet).where(Snippet.created_at < threshold)
    
    result = await db.execute(query)
    await db.commit()
    
    return result.rowcount  # Возвращаем количество удаленных строк