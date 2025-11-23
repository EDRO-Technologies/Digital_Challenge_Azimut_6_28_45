"""
FastAPI сервер для RAG агента.
Предоставляет REST API для поиска релевантных чанков и получения ответов.
"""

import sys
import io
import os
from pathlib import Path
from typing import List, Dict, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn

# Установка кодировки для Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from rag_agent import RAGAgent

# Инициализация FastAPI приложения
app = FastAPI(
    title="RAG Agent API",
    description="API для поиска релевантных чанков и получения ответов на основе документов",
    version="1.0.0"
)

# Настройка CORS для разрешения запросов с других доменов
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене лучше указать конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Глобальный экземпляр RAG агента
rag_agent: Optional[RAGAgent] = None


# Pydantic модели для запросов и ответов
class SearchRequest(BaseModel):
    """Модель запроса для поиска."""
    query: str = Field(..., description="Текст запроса для поиска", min_length=1)
    top_k: int = Field(5, description="Количество релевантных чанков для возврата", ge=1, le=20)


class AnswerRequest(BaseModel):
    """Модель запроса для получения ответа с контекстом."""
    query: str = Field(..., description="Текст вопроса", min_length=1)
    top_k: int = Field(5, description="Количество релевантных чанков для использования", ge=1, le=20)
    max_context_length: int = Field(2000, description="Максимальная длина контекста в символах", ge=100, le=10000)


class ChunkResponse(BaseModel):
    """Модель ответа с информацией о чанке."""
    rank: int
    score: float
    distance: float
    document_name: Optional[str] = None
    document_short_name: Optional[str] = None
    document_source: Optional[str] = None
    document_number: Optional[str] = None
    document_date: Optional[str] = None
    paragraph_name: Optional[str] = None
    paragraph_number: Optional[int] = None
    page_number: Optional[int] = None
    text: str
    text_length: int


class SearchResponse(BaseModel):
    """Модель ответа на запрос поиска."""
    query: str
    total_results: int
    chunks: List[ChunkResponse]


class SourceResponse(BaseModel):
    """Модель источника документа."""
    document_name: Optional[str] = None
    document_short_name: Optional[str] = None
    document_source: Optional[str] = None
    document_number: Optional[str] = None
    document_date: Optional[str] = None


class AnswerResponse(BaseModel):
    """Модель ответа с контекстом."""
    query: str
    context: str
    context_length: int
    num_chunks_used: int
    sources: List[SourceResponse]
    relevant_chunks: List[ChunkResponse]


class HealthResponse(BaseModel):
    """Модель ответа для проверки здоровья сервиса."""
    status: str
    message: str
    agent_loaded: bool
    vector_store_loaded: bool


@app.on_event("startup")
async def startup_event():
    """Инициализация RAG агента при запуске сервера."""
    global rag_agent
    try:
        print("=" * 80)
        print("ИНИЦИАЛИЗАЦИЯ RAG АГЕНТА")
        print("=" * 80)
        
        vector_store_dir = Path("vector_store")
        if not vector_store_dir.exists():
            raise FileNotFoundError(f"Директория vector_store не найдена: {vector_store_dir}")
        
        # Инициализация с Ollama
        # Можно настроить через переменные окружения
        ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
        ollama_model = os.getenv("OLLAMA_MODEL", "bge-m3")
        
        rag_agent = RAGAgent(
            vector_store_dir=str(vector_store_dir),
            ollama_model=ollama_model,
            ollama_url=ollama_url
        )
        print("\n[OK] RAG агент успешно инициализирован!")
        
    except Exception as e:
        print(f"\n[ERROR] Ошибка при инициализации RAG агента: {e}")
        import traceback
        traceback.print_exc()
        raise


@app.get("/", tags=["Общие"])
async def root():
    """Корневой endpoint с информацией об API."""
    return {
        "message": "RAG Agent API",
        "version": "1.0.0",
        "endpoints": {
            "/health": "Проверка здоровья сервиса",
            "/search": "Поиск релевантных чанков (POST)",
            "/answer": "Получение ответа с контекстом (POST)",
            "/docs": "Интерактивная документация API"
        }
    }


@app.get("/health", response_model=HealthResponse, tags=["Общие"])
async def health_check():
    """Проверка здоровья сервиса."""
    global rag_agent
    
    agent_loaded = rag_agent is not None
    vector_store_loaded = False
    
    if agent_loaded:
        try:
            vector_store_loaded = rag_agent.index is not None and len(rag_agent.metadata) > 0
        except:
            pass
    
    status = "healthy" if agent_loaded and vector_store_loaded else "unhealthy"
    message = "Сервис работает нормально" if status == "healthy" else "Сервис не готов"
    
    return HealthResponse(
        status=status,
        message=message,
        agent_loaded=agent_loaded,
        vector_store_loaded=vector_store_loaded
    )


@app.post("/search", response_model=SearchResponse, tags=["Поиск"])
async def search(request: SearchRequest):
    """
    Поиск релевантных чанков по запросу.
    
    Пример запроса:
    ```json
    {
        "query": "Какие требования к газоопасным работам?",
        "top_k": 5
    }
    ```
    """
    global rag_agent
    
    if rag_agent is None:
        raise HTTPException(status_code=503, detail="RAG агент не инициализирован")
    
    try:
        # Выполняем поиск
        results = rag_agent.search(request.query, top_k=request.top_k)
        
        # Преобразуем результаты в формат ответа
        chunks = []
        for i, result in enumerate(results, 1):
            chunk = ChunkResponse(
                rank=i,
                score=result.get('score', 0.0),
                distance=result.get('distance', 0.0),
                document_name=result.get('document_name'),
                document_short_name=result.get('document_short_name'),
                document_source=result.get('document_source'),
                document_number=result.get('document_number'),
                document_date=result.get('document_date'),
                paragraph_name=result.get('paragraph_name'),
                paragraph_number=result.get('paragraph_number'),
                page_number=result.get('page_number'),
                text=result.get('text', ''),
                text_length=len(result.get('text', ''))
            )
            chunks.append(chunk)
        
        return SearchResponse(
            query=request.query,
            total_results=len(chunks),
            chunks=chunks
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при поиске: {str(e)}")


@app.post("/answer", response_model=AnswerResponse, tags=["Ответы"])
async def answer(request: AnswerRequest):
    """
    Получение ответа с контекстом на основе релевантных чанков.
    
    Пример запроса:
    ```json
    {
        "query": "Какие требования к газоопасным работам?",
        "top_k": 5,
        "max_context_length": 2000
    }
    ```
    """
    global rag_agent
    
    if rag_agent is None:
        raise HTTPException(status_code=503, detail="RAG агент не инициализирован")
    
    try:
        # Получаем ответ с контекстом
        answer_data = rag_agent.answer(
            request.query,
            top_k=request.top_k,
            max_context_length=request.max_context_length
        )
        
        # Преобразуем источники
        sources = []
        for source in answer_data.get('sources', []):
            source_resp = SourceResponse(
                document_name=source.get('document_name'),
                document_short_name=source.get('document_short_name'),
                document_source=source.get('document_source'),
                document_number=source.get('document_number'),
                document_date=source.get('document_date')
            )
            sources.append(source_resp)
        
        # Преобразуем релевантные чанки
        relevant_chunks = []
        for i, chunk in enumerate(answer_data.get('relevant_chunks', []), 1):
            chunk_resp = ChunkResponse(
                rank=i,
                score=chunk.get('score', 0.0),
                distance=chunk.get('distance', 0.0),
                document_name=chunk.get('document_name'),
                document_short_name=chunk.get('document_short_name'),
                document_source=chunk.get('document_source'),
                document_number=chunk.get('document_number'),
                document_date=chunk.get('document_date'),
                paragraph_name=chunk.get('paragraph_name'),
                paragraph_number=chunk.get('paragraph_number'),
                page_number=chunk.get('page_number'),
                text=chunk.get('text', ''),
                text_length=len(chunk.get('text', ''))
            )
            relevant_chunks.append(chunk_resp)
        
        return AnswerResponse(
            query=request.query,
            context=answer_data.get('context', ''),
            context_length=answer_data.get('context_length', 0),
            num_chunks_used=answer_data.get('num_chunks_used', 0),
            sources=sources,
            relevant_chunks=relevant_chunks
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при получении ответа: {str(e)}")


if __name__ == "__main__":
    # Запуск сервера
    uvicorn.run(
        "rag_api_server:app",
        host="0.0.0.0",
        port=8022,
        reload=False,  # В продакшене лучше False
        log_level="info"
    )

