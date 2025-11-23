# db_router.py
from fastapi import APIRouter, HTTPException
from typing import Optional, List, Dict
from pydantic import BaseModel

# Импортируем DatabaseManager
from db.db import DatabaseManager

# Создаем экземпляр APIRouter
db_router = APIRouter(prefix="/db", tags=["database"])

# Создаем экземпляр DatabaseManager
db_manager = DatabaseManager()


# Pydantic модели для запросов
class CreateUserRequest(BaseModel):
    name: str
    role: str
    mentor: Optional[str] = None
    lvl: Optional[str] = None


class CreateTestRequest(BaseModel):
    user_id: int
    module_id: int
    corrects: int


class UpdateUserLevelRequest(BaseModel):
    new_lvl: str


# Роуты для пользователей
@db_router.post("/users/", response_model=Dict)
async def create_user(request: CreateUserRequest):
        
    user_id = db_manager.create_user(request.name, request.role, request.mentor, request.lvl)
    if user_id is None:
        raise HTTPException(status_code=500, detail="Не удалось создать пользователя")
    return {"id": user_id, "message": "Пользователь успешно создан"}


@db_router.get("/users/{user_id}", response_model=Dict)
async def read_user(user_id: int):
    user = db_manager.get_user_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return user


@db_router.get("/users/", response_model=List[Dict])
async def read_users():
    users = db_manager.get_all_users()
    return users


@db_router.put("/users/{user_id}/level", response_model=Dict)
async def update_user_level(user_id: int, request: UpdateUserLevelRequest):
    success = db_manager.update_user_lvl(user_id, request.new_lvl)
    if not success:
        raise HTTPException(status_code=404, detail="Пользователь не найден или не удалось обновить уровень")
    return {"message": "Уровень пользователя успешно обновлен"}


@db_router.delete("/users/{user_id}", response_model=Dict)
async def delete_user(user_id: int):
    success = db_manager.delete_user(user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Пользователь не найден или не удалось удалить")
    return {"message": "Пользователь успешно удален"}


# Роуты для тестов
@db_router.post("/tests/", response_model=Dict)
async def create_test(request: CreateTestRequest):
    
    
    
    # Тут обновление уровня
    test_id = db_manager.create_test(request.user_id, request.module_id, request.corrects)
    total_modules = db_manager.get_total_tests_correct(request.user_id)
    
    if total_modules < 3:
        new_lvl = 'Новичок'
    elif total_modules < 7:
        new_lvl = 'Опытный'
    elif total_modules < 10:
        new_lvl = 'Профессионал'
    elif total_modules == 10:
        new_lvl = 'Эксперт'
    else:
        new_lvl = 'Опытный'
    
    success = db_manager.update_user_lvl(request.user_id, new_lvl)
    
    if test_id is None:
        raise HTTPException(status_code=500, detail="Не удалось создать тест")
    return {"id": test_id, "message": "Тест успешно создан"}


# Роуты для аналитики
@db_router.get("/analytics/general", response_model=Dict)
async def get_general_stats():
    stats = db_manager.get_general_statistics()
    if not stats:
        raise HTTPException(status_code=500, detail="Не удалось получить общую статистику")
    return stats


@db_router.get("/analytics/user/{user_id}", response_model=Dict)
async def get_user_stats(user_id: int):
    stats = db_manager.get_user_statistics(user_id)
    if not stats:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return stats


@db_router.get("/analytics/mentor/{mentor_name}", response_model=Dict)
async def get_mentor_stats(mentor_name: str):
    stats = db_manager.get_mentor_statistics(mentor_name)
    if not stats:
        raise HTTPException(status_code=404, detail="Ментор не найден или нет данных")
    return stats