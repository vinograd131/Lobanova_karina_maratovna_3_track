#config
import os
from dotenv import load_dotenv
from mistralai import Mistral

load_dotenv()


class Config:
    # API ключи
    MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")

    # Модели
    MODEL_INTERVIEWER = "mistral-large-latest"
    MODEL_OBSERVER = "mistral-large-latest"
    MODEL_FEEDBACK = "mistral-large-latest"

    # RAG настройки
    EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
    KNOWLEDGE_BASE_PATH = "knowledge/"

    # Логирование
    LOGS_DIR = "sessions/"

    @staticmethod
    def get_mistral_client():
        """Создаёт клиент Mistral"""
        if not Config.MISTRAL_API_KEY:
            raise ValueError("MISTRAL_API_KEY не найден в .env")
        return Mistral(api_key=Config.MISTRAL_API_KEY)


# Глобальный клиент
MISTRAL_CLIENT = Config.get_mistral_client()