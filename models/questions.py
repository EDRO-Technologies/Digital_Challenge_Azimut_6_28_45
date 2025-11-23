from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
from typing import List
import logging

from models.prompts import quiz_prompt
from models.models import llm
import os 


# Модель для структурированного вывода викторины
class QuizQuestion(BaseModel):
    title: str = Field(description="Текст вопроса")
    variant_a: str = Field(description="Вариант ответа A")
    variant_b: str = Field(description="Вариант ответа B")
    variant_c: str = Field(description="Вариант ответа C")
    variant_d: str = Field(description="Вариант ответа D")
    correct_answer: str = Field(description="Правильный ответ (A, B, C или D)")
    explanation: str = Field(description="Краткое пояснение правильного ответа")

class QuizResponseModel(BaseModel):
    questions: List[QuizQuestion] = Field(description="Список вопросов викторины")

# Модель для структурированного вывода сценария
class Scenario(BaseModel):
    scenario_description: str = Field(description="Реалистичное описание происшествия на рабочем месте")
    question: str = Field(description="Вопрос о том, что должен сделать работник или ответственное лицо")
    variant_a: str = Field(description="Вариант действия №1")
    variant_b: str = Field(description="Вариант действия №2")
    variant_c: str = Field(description="Вариант действия №3")
    variant_d: str = Field(description="Вариант действия №4")
    correct_answer: str = Field(description="Правильный ответ (A, B, C или D)")
    explanation: str = Field(description="Пояснение почему выбранный вариант правильный")

class ScenarioResponseModel(BaseModel):
    scenario: Scenario = Field(description="Учебная ситуационная задача")

# Парсеры для JSON вывода
scenario_parser = JsonOutputParser(pydantic_object=ScenarioResponseModel)
quiz_parser = JsonOutputParser(pydantic_object=QuizResponseModel)

def generate_quiz_questions(context: str) -> list:
    """
    Генерирует вопросы викторины на основе переданного контекста.
    
    Args:
        context (str): Контекст для генерации вопросов
        
    Returns:
        list: Список вопросов в формате JSON
    """
    try:
        # Форматируем промпт с инструкциями для JSON вывода
        prompt = quiz_prompt.format(
            context=context,
            format_instructions=quiz_parser.get_format_instructions()
        )
        
        # Получаем ответ от LLM
        quiz_text = llm.predict(prompt)
        
        # Парсим JSON ответ
        parsed_quiz = quiz_parser.parse(quiz_text)
        # Преобразуем в список вопросов
        quiz_list = []
        for question in parsed_quiz["questions"]:
            quiz_list.append({
                "title": question["title"],
                "variant_a": question["variant_a"],
                "variant_b": question["variant_b"], 
                "variant_c": question["variant_c"],
                "variant_d": question["variant_d"],
                "correct_answer": question["correct_answer"],
                "explanation": question["explanation"]
            })
        
        return quiz_list
    
        if quiz_list[0]['title'] == '':
            logging.error(f"Ошибка при генерации вопросов викторины: {e}")
            # Возвращаем пустой список в случае ошибки
            return get_fallback_quiz()
    
    except Exception as e:
        logging.error(f"Ошибка при генерации вопросов викторины: {e}")
        # Возвращаем пустой список в случае ошибки
        return get_fallback_quiz()
    

def get_context_quiz(id_module):
    files = os.listdir('data/data_summary')

    filename = 'data/data_summary/' + [f for f in files if f[0] == str(id_module)][0]
    with open(filename, 'r', encoding='utf-8') as file:
        lines = file.readlines()
        
    return ''.join(lines)


def generate_scenario_questions() -> list:
    try:
        # Форматируем промпт с инструкциями для JSON вывода
        prompt = scenario_prompt.format(
            format_instructions=quiz_parser.get_format_instructions()
        )
        
        # Получаем ответ от LLM
        scenario_text = llm.predict(prompt)
        
        # Парсим JSON ответ
        parsed_quiz = quiz_parser.parse(scenario_text)

        # Преобразуем в список вопросов
        scenario_list = []
        for question in parsed_quiz["questions"]:
            scenario_list.append({
                "title": question["title"],
                "variant_a": question["variant_a"],
                "variant_b": question["variant_b"], 
                "variant_c": question["variant_c"],
                "variant_d": question["variant_d"],
                "correct_answer": question["correct_answer"],
                "explanation": question["explanation"]
            })
        
        return scenario_list
        
    except Exception as e:
        logging.error(f"Ошибка при генерации вопросов викторины: {e}")
        # Возвращаем пустой список в случае ошибки
        return get_fallback_scenario()


def get_fallback_scenario() -> dict:
    """
    Возвращает fallback сценарий в случае ошибки генерации.
    """
    return {
        "scenario_description": "Работник в производственном цехе заметил, что из электрощита идет дым и слышен треск. В это время рядом находятся другие сотрудники, продолжающие работу.",
        "question": "Что должен сделать работник в данной ситуации?",
        "variant_a": "Продолжить работу, так как это не его зона ответственности",
        "variant_b": "Немедленно сообщить руководителю и покинуть опасную зону вместе с другими сотрудниками",
        "variant_c": "Попытаться самостоятельно потушить возможное возгорание",
        "variant_d": "Ждать, пока кто-то другой заметит проблему",
        "correct_answer": "B",
        "explanation": "При обнаружении признаков возгорания в электроустановке необходимо немедленно сообщить руководителю, отключить питание и покинуть опасную зону для обеспечения безопасности всех сотрудников."
    }



def get_fallback_quiz() -> list:
    """
    Возвращает fallback вопросы викторины в случае ошибки генерации.
    """
    
    return [
        {
            "title": "Какие обязанности работодателя указаны в приказе № 753н?",
            "variant_a": "Разработка инструкций по охране труда на основе технической документации производителя оборудования",
            "variant_b": "Обеспечение работников средствами индивидуальной защиты", 
            "variant_c": "Организация безопасных рабочих мест",
            "variant_d": "Проведение регулярных медицинских осмотров сотрудников",
            "correct_answer": "A",
            "explanation": "Приказ № 753н требует от работодателя разработку инструкций по охране труда на основе технической документации производителя оборудования."
        },
        {
            "title": "Какие меры безопасности предписаны для работы с опасными грузами?",
            "variant_a": "Использование специализированной упаковки и транспортных средств",
            "variant_b": "Проведение регулярных медицинских осмотров сотрудников",
            "variant_c": "Обеспечение работников средствами индивидуальной защиты",
            "variant_d": "Организация дополнительных перерывов для работников",
            "correct_answer": "A", 
            "explanation": "При работе с опасными грузами обязательна маркировка, использование специализированной упаковки и транспортных средств."
        },
        {
            "title": "Какие требования предъявляются к транспортировке грузов?",
            "variant_a": "Обеспечение устойчивости транспортных средств",
            "variant_b": "Обеспечение дополнительных перерывов для водителей",
            "variant_c": "Обеспечение регулярной проверки технического состояния транспортных средств",
            "variant_d": "Обеспечение работников средствами индивидуальной защиты",
            "correct_answer": "A",
            "explanation": "Систематизированы требования к транспортировке грузов, обеспечивающие безопасность движения, устойчивость транспортных средств."
        },
        {
            "title": "Что должен сделать работник при обнаружении неисправного оборудования?",
            "variant_a": "Продолжить работу",
            "variant_b": "Немедленно сообщить руководителю",
            "variant_c": "Попытаться самостоятельно починить", 
            "variant_d": "Игнорировать неисправность",
            "correct_answer": "B",
            "explanation": "При обнаружении неисправности оборудования работник должен немедленно сообщить руководителю для обеспечения безопасности."
        },
        {
            "title": "Какие средства индивидуальной защиты обязательны при работе с химическими веществами?",
            "variant_a": "Только перчатки",
            "variant_b": "Перчатки, защитные очки и респиратор",
            "variant_c": "Защитный костюм и обувь",
            "variant_d": "Зависит от конкретного вещества и условий работы",
            "correct_answer": "D",
            "explanation": "Выбор СИЗ зависит от типа химического вещества, его концентрации и условий работы."
        }
    ]
