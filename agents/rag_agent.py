
from config import MISTRAL_CLIENT


class RAGAgent:
    """Агент с доступом к базе знаний через RAG"""

    def __init__(self, knowledge_base):
        self.kb = knowledge_base

    def retrieve_context(self, position, user_response, topic=None):
        """Извлекает контекст из базы знаний для вопроса интервьюера"""
        # Определяем IT категорию по позиции
        category = self._detect_category(position)

        # Формируем запрос
        if topic:
            query = f"{topic} тестирование проверка {user_response}"
        else:
            query = f"{position} {user_response}"

        # Ищем релевантные знания
        results = self.kb.search(query, category=category, k=2)

        if results:
            context_items = []
            for r in results:
                # Форматируем для промпта интервьюера
                context_items.append(f"- {r['text']}")

            context = "\n".join(context_items)
            return f"📚 Релевантная информация:\n{context}"

        return ""

    def _detect_category(self, position):
        """Определяет IT категорию позиции"""
        pos_lower = position.lower()

        if any(word in pos_lower for word in ['backend', 'бэкенд', 'api', 'server']):
            return 'backend'
        elif any(word in pos_lower for word in ['frontend', 'фронтенд', 'javascript', 'react', 'vue']):
            return 'frontend'
        elif any(word in pos_lower for word in ['ml', 'машин', 'data', 'ai', 'нейрон']):
            return 'ml'
        elif any(word in pos_lower for word in ['devops', 'sre', 'инфраструктур', 'docker']):
            return 'devops'
        elif any(word in pos_lower for word in ['qa', 'тестиров', 'test', 'quality']):
            return 'qa'
        else:
            return 'general'