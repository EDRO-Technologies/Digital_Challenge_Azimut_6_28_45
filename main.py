from fastapi import FastAPI, HTTPException, UploadFile
from pydantic import BaseModel
import logging
from models.prompts import chat_template, calibration_chat_template
from models.models import llm
from models.rag import get_context
from models.questions import generate_quiz_questions, get_context_quiz
from models.speech import get_text_from_speech
from db.db_router import db_router
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any, Optional
import json

from quiz import update_quiz_from_module, load_quiz_data


app = FastAPI(title="beZbot API", version="1.0.0")
app.include_router(db_router)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Уточните, откуда приходят запросы (например, ["http://localhost:3000"])
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class CalibrationResultRequest(BaseModel):
    answers: Dict[str, str]  # {'question': 'answer'}

class SkipModulesResponse(BaseModel):
    skipped_modules: List[int]
    message: str


class SpeechResponse(BaseModel):
    text: str


class ModuleRequest(BaseModel):
    module_id: int


class ModuleResponse(BaseModel):
    module_id: int
    module_name: str
    questions: List[Dict[str, Any]]
    total_questions: int


class QuestionRequest(BaseModel):
    question: str


class QuizRequest(BaseModel):
    id: str


class ScenarioRequest(BaseModel):
    id: str


class AnswerResponse(BaseModel):
    answer: str
    metadata: list


class QuizResponse(BaseModel):
    quiz: list


class ScenarioResponse(BaseModel):
    scenario: list


class UpdateModuleRequest(BaseModel):
    module_id: int = 1
    module_name: Optional[str] = None


class UpdateModuleResponse(BaseModel):
    success: bool
    message: str


@app.post("/get_answer", response_model=AnswerResponse)
async def get_answer(request: QuestionRequest):
    """Отвечает на вопрос: сначала проверяет FAQ, потом использует RAG + LLM."""
    
    try:
        context = get_context()
        # Строим промпт с учётом историизкщьзе = context
        prompt = chat_template.format(context=context, question=request.question)
        
        logging.error(prompt)
        
        answer = llm.predict(prompt)

        answer = answer.strip()
        
        logging.error(answer)

        return AnswerResponse(
            answer=answer,
            metadata=[]
        )

    except Exception as e:
        logging.error(f"Ошибка при обработке запроса: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка при обработке запроса: {str(e)}")


@app.get("/get_module/{module_id}", response_model=ModuleResponse)
async def get_module(module_id: int):
    test_names, tests = load_quiz_data()
    try:
        # Проверяем существование модуля
        if module_id not in tests:
            raise HTTPException(status_code=404, detail="Модуль не найден")
        
        # Получаем вопросы модуля
        module_questions = tests[module_id]
        
        # Словарь с названиями модулей
        test_names = {
            0: "КАЛИБРОВОЧНЫЙ ТЕСТ",
            1: "История и миссия", 
            2: "Структура и активы",
            3: "Технологии и модернизация",
            4: "Безопасность и экология",
            5: "Персонал и корпоративная культура",
            6: "Социальная ответственность",
            7: "Инновации и цифровизация",
            8: "Экономика и эффективность",
            9: "Перспективы и стратегия",
            10: "Регламенты и нормативная документация"
        }
        
        module_name = test_names.get(module_id, f"Модуль {module_id}")
        
        return {
            "module_id": module_id,
            "module_name": module_name,
            "questions": module_questions,
            "total_questions": len(module_questions)
        }
        
    except Exception as e:
        logging.error(f"Ошибка при обработке запроса: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка при обработке запроса: {str(e)}")


@app.post("/get_quiz", response_model=QuizResponse)
async def get_quiz(request: QuizRequest):
    """Генерирует проверочную викторину на основе контекста."""
    try:
        context = get_context_quiz(request.id)
        response = generate_quiz_questions(context)
        return QuizResponse(quiz=response)
    except Exception as e:
        logging.error(f"Ошибка при генерации викторины: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка при генерации викторины: {str(e)}")


@app.post('/speech_to_text', response_model=SpeechResponse)
async def speech_to_text(file: UploadFile):
    try:
        # Читаем содержимое файла
        file_content = await file.read()

        text = get_text_from_speech(file_content)

        return {'text': text}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@app.post("/analyze_calibration", response_model=SkipModulesResponse)
async def analyze_calibration(request: CalibrationResultRequest):
    """Анализирует результаты калибровочного теста и рекомендует модули для пропуска."""
    test_names, tests = load_quiz_data()
    try:
        
        logging.error(f"Analyzing calibration results: {request.answers}")
        
        prompt = calibration_chat_template.format(answers=request.answers)
        
        # Получаем ответ от LLM
        analysis_result = llm.predict(prompt).strip()
        
        logging.error(analysis_result)
        
        # Парсим JSON ответ
        try:
            result_data = json.loads(analysis_result.replace('```', ''))
            skipped_modules = result_data.get("skipped_modules", [])
            reasoning = result_data.get("reasoning", "Анализ завершен")
            
            # Проверяем, что не пропускаем все модули
            total_modules = len(test_names) - 1  # исключаем калибровочный
            if len(skipped_modules) >= total_modules - 3:  # оставляем минимум 4 модуля
                skipped_modules = skipped_modules[:total_modules - 4]
            
            # Убеждаемся, что модуль 0 не включен
            if 0 in skipped_modules:
                skipped_modules.remove(0)
                
            logging.info(f"Recommended to skip modules: {skipped_modules}, reasoning: {reasoning}")
            
            return SkipModulesResponse(
                skipped_modules=skipped_modules,
                message=reasoning
            )
            
        except json.JSONDecodeError:
            logging.error(f"Failed to parse LLM response: {analysis_result}")
            # Fallback: возвращаем пустой список при ошибке парсинга
            return SkipModulesResponse(
                skipped_modules=[],
                message="Рекомендуем пройти все модули для полноценного обучения"
            )

    except Exception as e:
        logging.error(f"Ошибка при анализе калибровочного теста: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка при анализе результатов: {str(e)}")


@app.post("/update_module", response_model=UpdateModuleResponse)
async def update_module(request: UpdateModuleRequest):
    """Обновляет версию вопросов для указанного модуля."""
    try:
        success = update_quiz_from_module(
            module_id=request.module_id,
            module_name=request.module_name
        )
        
        if success:
            return UpdateModuleResponse(
                success=True,
                message=f"Модуль {request.module_id} успешно обновлён"
            )
        else:
            return UpdateModuleResponse(
                success=False,
                message=f"Ошибка при обновлении модуля {request.module_id}"
            )
    except Exception as e:
        logging.error(f"Ошибка при обновлении модуля: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при обновлении модуля: {str(e)}"
        )


@app.get('/')
async def test_root():

    return {'result': 'it`s healty'}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8021)
