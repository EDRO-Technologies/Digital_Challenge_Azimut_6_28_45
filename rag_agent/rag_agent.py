"""
RAG агент для поиска релевантных чанков и ответов на вопросы.
Использует векторное хранилище FAISS и Ollama API с моделью bge-m3 для эмбеддингов.
"""

import json
import pickle
import numpy as np
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import sys
import faiss
import requests

# Установка кодировки для Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False


class RAGAgent:
    """RAG агент для поиска релевантных чанков и ответов на вопросы."""
    
    def __init__(
        self,
        vector_store_dir: str = "vector_store",
        ollama_model: str = "bge-m3",
        ollama_url: str = "http://localhost:11434",
        device: Optional[str] = None,
        top_k: int = 5
    ):
        """
        Инициализирует RAG агента.
        
        Args:
            vector_store_dir: Директория с векторным хранилищем
            ollama_model: Название модели в Ollama (по умолчанию "bge-m3")
            ollama_url: URL Ollama сервера (по умолчанию "http://localhost:11434")
            device: Устройство для вычислений ('cuda' или 'cpu') - используется только для FAISS
            top_k: Количество релевантных чанков для возврата
        """
        self.vector_store_dir = Path(vector_store_dir)
        self.ollama_model = ollama_model
        self.ollama_url = ollama_url.rstrip('/')
        self.top_k = top_k
        
        # Определяем устройство для FAISS (если доступен torch)
        if device is None:
            if TORCH_AVAILABLE and torch.cuda.is_available():
                self.device = 'cuda'
            else:
                self.device = 'cpu'
        else:
            self.device = device
        
        print("=" * 80)
        print("ИНИЦИАЛИЗАЦИЯ RAG АГЕНТА")
        print("=" * 80)
        print(f"  Используется Ollama API: {self.ollama_url}")
        print(f"  Модель: {self.ollama_model}")
        print(f"  Устройство для FAISS: {self.device}")
        if self.device == 'cuda' and TORCH_AVAILABLE:
            try:
                print(f"  GPU: {torch.cuda.get_device_name(0)}")
                print(f"  Память GPU: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.2f} GB")
            except:
                pass
        
        # Проверяем доступность Ollama
        self._check_ollama()
        
        # Загружаем векторное хранилище
        self._load_vector_store()
        
        print("\n[OK] RAG агент готов к работе!")
    
    def _check_ollama(self):
        """Проверяет доступность Ollama и модели."""
        print(f"\nПроверяю доступность Ollama...")
        try:
            # Проверяем доступность Ollama сервера
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            if response.status_code != 200:
                raise ConnectionError(f"Ollama сервер недоступен: HTTP {response.status_code}")
            
            # Проверяем наличие модели
            models = response.json().get('models', [])
            model_names = [m.get('name', '') for m in models]
            
            # Проверяем точное совпадение или совпадение с тегом (например, bge-m3:latest)
            model_found = False
            if self.ollama_model in model_names:
                model_found = True
            else:
                # Проверяем, есть ли модель с таким базовым именем (с любым тегом)
                base_name = self.ollama_model.split(':')[0]
                for model_name in model_names:
                    if model_name.startswith(base_name + ':') or model_name == base_name:
                        model_found = True
                        # Используем полное имя модели с тегом
                        if ':' not in self.ollama_model:
                            print(f"  [INFO] Найдена модель '{model_name}', используем её")
                            self.ollama_model = model_name
                        break
            
            if not model_found:
                print(f"  [WARNING] Модель '{self.ollama_model}' не найдена в Ollama")
                print(f"  Доступные модели: {', '.join(model_names[:5])}")
                print(f"  Убедитесь, что модель загружена: ollama pull {self.ollama_model}")
            else:
                print(f"  [OK] Модель '{self.ollama_model}' найдена в Ollama")
            
            # Тестовый запрос для определения размерности эмбеддингов
            test_response = requests.post(
                f"{self.ollama_url}/api/embeddings",
                json={"model": self.ollama_model, "prompt": "test"},
                timeout=10
            )
            
            if test_response.status_code == 200:
                embedding = test_response.json().get('embedding', [])
                self.embedding_dim = len(embedding)
                print(f"  [OK] Ollama доступен. Размерность эмбеддингов: {self.embedding_dim}")
            else:
                raise ConnectionError(f"Ошибка при тестовом запросе: HTTP {test_response.status_code}")
                
        except requests.exceptions.ConnectionError:
            raise ConnectionError(
                f"Не удалось подключиться к Ollama по адресу {self.ollama_url}\n"
                f"Убедитесь, что Ollama запущен: ollama serve"
            )
        except Exception as e:
            print(f"  [ERROR] Ошибка при проверке Ollama: {e}")
            raise
    
    def _load_vector_store(self):
        """Загружает векторное хранилище."""
        print(f"\nЗагружаю векторное хранилище из {self.vector_store_dir}...")
        
        # Загружаем FAISS индекс
        index_file = self.vector_store_dir / "faiss_index.bin"
        if not index_file.exists():
            raise FileNotFoundError(f"Файл индекса не найден: {index_file}")
        
        print("  Загружаю FAISS индекс...")
        self.index = faiss.read_index(str(index_file))
        print(f"  [OK] Индекс загружен. Векторов в индексе: {self.index.ntotal}")
        
        # Проверяем размерность индекса
        index_dim = self.index.d
        if hasattr(self, 'embedding_dim') and index_dim != self.embedding_dim:
            print(f"  [WARNING] Размерность индекса ({index_dim}) не совпадает с размерностью эмбеддингов Ollama ({self.embedding_dim})")
            print(f"  Это может привести к ошибкам при поиске!")
        
        # Загружаем метаданные
        metadata_file = self.vector_store_dir / "metadata.pkl"
        if not metadata_file.exists():
            raise FileNotFoundError(f"Файл метаданных не найден: {metadata_file}")
        
        print("  Загружаю метаданные...")
        with open(metadata_file, 'rb') as f:
            self.metadata = pickle.load(f)
        print(f"  [OK] Метаданные загружены. Чанков: {len(self.metadata)}")
        
        # Загружаем информацию об индексе
        info_file = self.vector_store_dir / "index_info.json"
        if info_file.exists():
            with open(info_file, 'r', encoding='utf-8') as f:
                self.index_info = json.load(f)
        else:
            self.index_info = {}
        
        # Проверяем доступность GPU для FAISS
        self.use_gpu_faiss = False
        try:
            if self.device == 'cuda' and TORCH_AVAILABLE and torch.cuda.is_available():
                try:
                    # Пробуем создать GPU ресурсы
                    res = faiss.StandardGpuResources()
                    self.use_gpu_faiss = True
                    print("  [OK] faiss-gpu доступен, будет использоваться GPU для поиска")
                except (AttributeError, RuntimeError):
                    print("  [INFO] faiss-gpu не установлен, поиск будет на CPU")
        except Exception as e:
            print(f"  [INFO] Не удалось определить доступность GPU для FAISS: {e}")
            print("  [INFO] Поиск будет на CPU")
    
    def _get_query_embedding(self, query: str) -> np.ndarray:
        """
        Создает эмбеддинг для запроса через Ollama API.
        
        Args:
            query: Текст запроса
            
        Returns:
            Эмбеддинг запроса
        """
        try:
            response = requests.post(
                f"{self.ollama_url}/api/embeddings",
                json={
                    "model": self.ollama_model,
                    "prompt": query
                },
                timeout=30
            )
            
            if response.status_code != 200:
                raise RuntimeError(f"Ошибка Ollama API: HTTP {response.status_code}, {response.text}")
            
            result = response.json()
            embedding = result.get('embedding', [])
            
            if not embedding:
                raise RuntimeError("Пустой эмбеддинг от Ollama")
            
            # Преобразуем в numpy массив
            embedding = np.array(embedding, dtype=np.float32)
            
            # Нормализуем эмбеддинг (важно для FAISS)
            norm = np.linalg.norm(embedding)
            if norm > 0:
                embedding = embedding / norm
            
            # Если это 1D массив, делаем его 2D
            if len(embedding.shape) == 1:
                embedding = embedding.reshape(1, -1)
            
            return embedding
            
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Ошибка при запросе к Ollama: {e}")
        except Exception as e:
            raise RuntimeError(f"Ошибка при создании эмбеддинга: {e}")
    
    def search(self, query: str, top_k: Optional[int] = None) -> List[Dict]:
        """
        Ищет релевантные чанки для запроса.
        
        Args:
            query: Текст запроса
            top_k: Количество релевантных чанков (если None, используется self.top_k)
            
        Returns:
            Список словарей с релевантными чанками и метаданными
        """
        if top_k is None:
            top_k = self.top_k
        
        # Создаем эмбеддинг для запроса
        query_embedding = self._get_query_embedding(query)
        
        # Выполняем поиск
        if self.use_gpu_faiss:
            # Используем GPU для поиска
            res = faiss.StandardGpuResources()
            index_gpu = faiss.index_cpu_to_gpu(res, 0, self.index)
            distances, indices = index_gpu.search(query_embedding, top_k)
        else:
            # Используем CPU для поиска
            distances, indices = self.index.search(query_embedding, top_k)
        
        # Формируем результаты
        results = []
        for i, (distance, idx) in enumerate(zip(distances[0], indices[0])):
            if idx < len(self.metadata):
                chunk_metadata = self.metadata[idx].copy()
                chunk_metadata['score'] = float(1 / (1 + distance))  # Конвертируем расстояние в score
                chunk_metadata['distance'] = float(distance)
                chunk_metadata['rank'] = i + 1
                results.append(chunk_metadata)
        
        return results
    
    def answer(self, query: str, top_k: Optional[int] = None, max_context_length: int = 2000) -> Dict:
        """
        Отвечает на вопрос, используя релевантные чанки.
        
        Args:
            query: Текст вопроса
            top_k: Количество релевантных чанков для использования
            max_context_length: Максимальная длина контекста в символах
            
        Returns:
            Словарь с ответом и релевантными чанками
        """
        # Ищем релевантные чанки
        relevant_chunks = self.search(query, top_k)
        
        # Формируем контекст из релевантных чанков
        context_parts = []
        current_length = 0
        
        for chunk in relevant_chunks:
            chunk_text = chunk.get('text', '')
            chunk_name = chunk.get('paragraph_name', '')
            
            # Формируем текст чанка с заголовком
            chunk_full_text = f"{chunk_name}\n\n{chunk_text}"
            
            if current_length + len(chunk_full_text) <= max_context_length:
                context_parts.append(chunk_full_text)
                current_length += len(chunk_full_text)
            else:
                # Если не помещается полностью, добавляем часть
                remaining = max_context_length - current_length
                if remaining > 100:  # Минимум 100 символов
                    context_parts.append(chunk_full_text[:remaining] + "...")
                break
        
        context = "\n\n---\n\n".join(context_parts)
        
        # Собираем уникальные источники документов
        sources = []
        seen_docs = set()
        for chunk in relevant_chunks[:len(context_parts)]:
            doc_short_name = chunk.get('document_short_name') or chunk.get('document_name', '')
            if doc_short_name and doc_short_name not in seen_docs:
                seen_docs.add(doc_short_name)
                sources.append({
                    'document_name': chunk.get('document_name', ''),
                    'document_short_name': doc_short_name,
                    'document_source': chunk.get('document_source', ''),
                    'document_number': chunk.get('document_number'),
                    'document_date': chunk.get('document_date')
                })
        
        # Формируем ответ
        answer = {
            'query': query,
            'context': context,
            'relevant_chunks': relevant_chunks,
            'num_chunks_used': len(context_parts),
            'context_length': len(context),
            'sources': sources
        }
        
        return answer
    
    def get_chunk_by_id(self, chunk_id: int) -> Optional[Dict]:
        """
        Получает чанк по его ID.
        
        Args:
            chunk_id: ID чанка
            
        Returns:
            Метаданные чанка или None
        """
        if 0 <= chunk_id < len(self.metadata):
            return self.metadata[chunk_id].copy()
        return None


def main():
    """Пример использования RAG агента."""
    import sys
    
    vector_store_dir = "vector_store"
    if len(sys.argv) > 1:
        vector_store_dir = sys.argv[1]
    
    if not Path(vector_store_dir).exists():
        print(f"Ошибка: директория '{vector_store_dir}' не найдена!")
        print("Сначала создайте векторное хранилище, запустив:")
        print("  python create_embeddings.py")
        sys.exit(1)
    
    # Создаем RAG агента
    print("\n" + "=" * 80)
    print("СОЗДАНИЕ RAG АГЕНТА")
    print("=" * 80)
    agent = RAGAgent(vector_store_dir=vector_store_dir)
    
    # Интерактивный режим
    print("\n" + "=" * 80)
    print("ИНТЕРАКТИВНЫЙ РЕЖИМ")
    print("=" * 80)
    print("Введите вопросы для поиска релевантных чанков.")
    print("Для выхода введите 'exit' или 'quit'.\n")
    
    while True:
        try:
            query = input("Вопрос: ").strip()
            
            if query.lower() in ['exit', 'quit', 'выход']:
                print("До свидания!")
                break
            
            if not query:
                continue
            
            # Ищем релевантные чанки
            print("\n" + "-" * 80)
            print("РЕЗУЛЬТАТЫ ПОИСКА:")
            print("-" * 80)
            
            results = agent.search(query, top_k=5)
            
            for i, result in enumerate(results, 1):
                print(f"\n{i}. Релевантность: {result['score']:.4f} (расстояние: {result['distance']:.4f})")
                print(f"   Заголовок: {result.get('paragraph_name', 'Не указано')}")
                print(f"   Номер параграфа: {result.get('paragraph_number', 'Не указано')}")
                if result.get('page_number'):
                    print(f"   Страница: {result.get('page_number')}")
                print(f"   Текст: {result.get('text', '')[:200]}...")
            
            # Формируем ответ с контекстом
            print("\n" + "-" * 80)
            print("КОНТЕКСТ ДЛЯ ОТВЕТА:")
            print("-" * 80)
            answer = agent.answer(query, top_k=5)
            print(f"\nИспользовано чанков: {answer['num_chunks_used']}")
            print(f"Длина контекста: {answer['context_length']} символов")
            print(f"\nКонтекст:\n{answer['context'][:500]}...")
            
            print("\n" + "=" * 80 + "\n")
            
        except KeyboardInterrupt:
            print("\n\nДо свидания!")
            break
        except Exception as e:
            print(f"\n[ERROR] Ошибка: {e}")
            import traceback
            traceback.print_exc()


if __name__ == '__main__':
    main()
