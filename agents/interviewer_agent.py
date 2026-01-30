
from config import MISTRAL_CLIENT
import re


class InterviewerAgent:
    def __init__(self, name, position, knowledge_base=None):
        self.name = name
        self.position = position
        self.asked_questions = []

    def generate_question(self, instruction, question_count=1, asked_questions=None):
        """Генерация вопроса БЕЗ пояснений"""
        if asked_questions:
            self.asked_questions = asked_questions

        prompt = f"""Ты - IT интервьюер. Сгенерируй ОДИН технический вопрос.

КОНТЕКСТ:
- Позиция: {self.position}
- Номер вопроса: {question_count}
- Инструкция Observer: {instruction}

ПРАВИЛА:
1. генерируй вопрос и поддержку кандидату
2. Максимум 2 предложения
3. Адаптируй сложность: {instruction}
4. Тема должна соответствовать позиции {self.position}

Примеры ПРАВИЛЬНОГО формата:
"Расскажите о вашем опыте работы с Python для анализа данных?"
"Как бы вы спроектировали систему кэширования для высоконагруженного приложения?"
"Какие методы оптимизации вы применяли при работе с большими данными?"

"""

        response = MISTRAL_CLIENT.chat.complete(
            model="mistral-large-latest",
            messages=[
                {"role": "system",
                 "content": "Ты строгий интервьюер. Возвращай ТОЛЬКО вопрос, без пояснений, без форматирования, без маркеров."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )

        question = response.choices[0].message.content.strip()

        # Очищаем от возможных кавычек и маркеров
        question = question.replace('"', '').replace("'", "")
        question = question.replace('*', '').replace('**', '')
        question = question.replace('---', '').replace('___', '')
        question = re.sub(r'^\d+[\.\)]\s*', '', question)  # Убираем нумерацию

        # Убираем всё после пояснений
        for stop_word in ['Почему', 'Например', 'Задача:', 'Цель:', 'Пример:', 'Если', '//', '---']:
            if stop_word in question:
                question = question.split(stop_word)[0].strip()

        self.asked_questions.append(question)

        return question

    def handle_offtopic(self, user_input):
        """Обработка оффтопика"""
        prompt = f"""Кандидат ответил не по теме: '{user_input}'
        Вежливо верни к теме {self.position}.
        Одним предложением вежливо направь к теме
        """

        response = MISTRAL_CLIENT.chat.complete(
            model="mistral-large-latest",
            messages=[
                {"role": "system", "content": "Ты вежливый интервьюер. Возвращай к теме двумя предложением."},
                {"role": "user", "content": prompt}
            ]
        )

        return response.choices[0].message.content.strip()