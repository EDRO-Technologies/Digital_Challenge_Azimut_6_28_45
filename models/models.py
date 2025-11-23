from langchain_core.language_models.llms import BaseLLM
from langchain_core.callbacks.manager import CallbackManagerForLLMRun
from langchain_core.outputs import LLMResult, Generation
from pydantic import Field
from typing import Any, List, Optional
import requests

from config import model_url, model_name


class YandexGPTLangChain(BaseLLM):
    """LangChain обертка для YandexGPT API"""
    
    api_url: str = Field(default=model_url)
    model_name: str = Field(default=model_name)

    def predict(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        """Вызов YandexGPT API"""
        try:
            payload = {
                "prompt": prompt,
                "max_tokens": kwargs.get("max_tokens", 120000),
                "temperature": kwargs.get("temperature", 0.7),
                "top_p": kwargs.get("top_p", 0.9)
            }

            response = requests.post(
                f"{self.api_url}/chat",
                json=payload,
                timeout=60
            )

            if response.status_code == 200:
                data = response.json()
                return data.get("response", "")
            else:
                raise Exception(f"YandexGPT API error: {response.status_code} — {response.text}")

        except Exception as e:
            raise Exception(f"Ошибка вызова YandexGPT: {e}")

    @property
    def _llm_type(self) -> str:
        return "yandexgpt"

    def _generate(
        self, 
        prompts: List[str], 
        stop: Optional[List[str]] = None, 
        **kwargs
    ) -> LLMResult:
        """Основной метод генерации для LangChain"""
        generations = []
        for prompt in prompts:
            text = self._call(prompt, stop=stop, **kwargs)
            generations.append([Generation(text=text)])
        return LLMResult(generations=generations)


# Создание экземпляра
llm = YandexGPTLangChain(api_url=model_url, model_name=model_name)

print(f"Модель и URL: {llm.model_name}, {llm.api_url}")