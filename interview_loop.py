
from interview_logger import InterviewLogger
from dispatcher import InterviewDispatcher
import re


class InterviewSystem:
    def __init__(self):
        self.logger = InterviewLogger()
        self.dispatcher = InterviewDispatcher()
        self.candidate_name = None
        self.position = None
        self.last_question = None
        self.user_responses = []
        self.question_count = 0
        self.max_questions = 10

    def start_interview(self, name, position):
        self.candidate_name = name
        self.position = position
        self.question_count = 0

        self.logger.start_session(name, position)
        self.dispatcher.init_interviewer(name, position)

        greeting = f"Привет, {name}! Я провожу техническое интервью для позиции {position}. Давайте начнём."
        first_q = "Расскажите о вашем опыте работы с основными технологиями для этой позиции?"

        self.last_question = first_q
        self.question_count = 1

        self.logger.add_turn(greeting, "", "[System] Начало интервью")
        self.logger.add_turn(first_q, "", f"[Interviewer] Первый вопрос")

        # Выводим только вопрос
        print(f"\n🤖: {first_q}")
        return ""

    def process_response(self, user_input):
        if "стоп" in user_input.lower() or self.question_count >= self.max_questions:
            return self._end_interview()

        if not user_input.strip():
            print("🤖: Пожалуйста, дайте развернутый ответ.")
            return ""

        self.user_responses.append(user_input)

        # Observer анализирует ответ
        observer_analysis = self._get_observer_analysis(user_input)

        # Генерация вопроса
        question = self.dispatcher.dispatch("generate_question", {
            "instruction": observer_analysis,
            "question_count": self.question_count + 1
        })

        # ОЧИСТКА: убираем всё, что не вопрос
        clean_question = self._clean_question(question)

        # Генерация мыслей для лога
        interviewer_thoughts = self._generate_interviewer_thoughts(observer_analysis, user_input)

        # Сохраняем в лог
        thoughts = f"[Observer]: {observer_analysis}\n[Interviewer]: {interviewer_thoughts}"
        self.logger.add_turn(clean_question, user_input, thoughts)

        self.last_question = clean_question
        self.question_count += 1

        # В консоль ТОЛЬКО чистый вопрос
        print(f"\n🤖: {clean_question}")
        return ""

    def _get_observer_analysis(self, user_response):
        """Анализ ответа кандидата"""
        from config import MISTRAL_CLIENT

        prompt = f"""Анализируй ответ кандидата на позицию {self.position}.

Вопрос: {self.last_question}
Ответ: {user_response}

Проанализируй качество ответа и дай инструкцию для следующего вопроса:
1. Если ответ хороший (глубокий, с примерами) - предложи повысить сложность
2. Если ответ средний (знает основы) - предложи сохранить уровень
3. Если ответ слабый (поверхностный) - предложи упростить вопрос
4. Если ответ не по теме - предложи вернуть к теме

Примеры инструкций:
- "Кандидат хорошо ответил. Похвали его.  Задай более сложный вопрос о {self.position}."
- "Ответ поверхностный. Поддержи. Задай более простой вопрос об основах."
- "Ответ не по теме. Вежливо верни к теме {self.position}."

Твоя инструкция (2-3 предложения):"""

        response = MISTRAL_CLIENT.chat.complete(
            model="mistral-large-latest",
            messages=[
                {"role": "system", "content": "Ты аналитик собеседований. Анализируй ответы кандидатов."},
                {"role": "user", "content": prompt}
            ]
        )

        return response.choices[0].message.content.strip()

    def _clean_question(self, question):
        """Очистка вопроса от пояснений"""
        # Убираем всё после маркеров пояснений
        stop_markers = [
            'Почему', 'Например', 'Пример:', 'Если',
            'Задача:', 'Цель:', '---', '###', '**Почему',
            '📌', '💡', '🎯', '🤔', '🔍'
        ]

        clean_q = question.strip()

        # Ищем настоящий вопрос (обычно это первое предложение/абзац)
        lines = clean_q.split('\n')
        for line in lines:
            line = line.strip()
            if line and len(line) > 10:
                # Убираем маркеры
                if not any(marker in line for marker in ['---', '###', '***']):
                    clean_q = line
                    break

        # Убираем всё после стоп-слов
        for marker in stop_markers:
            if marker in clean_q:
                clean_q = clean_q.split(marker)[0].strip()

        # Убираем кавычки и лишние пробелы
        clean_q = clean_q.replace('"', '').replace("'", "")
        clean_q = re.sub(r'\s+', ' ', clean_q)

        # Если вопрос слишком короткий, возвращаем первую осмысленную часть
        if len(clean_q) < 15 and len(question) > 30:
            # Берем первую строку без маркеров
            for line in question.split('\n'):
                line = line.strip()
                if len(line) > 20 and not line.startswith(('*', '-', '#', 'Почему')):
                    clean_q = line
                    break

        return clean_q.strip()

    def _generate_interviewer_thoughts(self, observer_analysis, user_response):
        """Генерация мыслей интервьюера для лога"""
        from config import MISTRAL_CLIENT

        prompt = f"""Ты - интервьюер. Сформулируй мысли для лога.

Анализ Observer: {observer_analysis}
Ответ кандидата: {user_response}

Опиши свои мысли о качестве ответа и почему следующий вопрос будет такой сложности.
(2 предложения):"""

        response = MISTRAL_CLIENT.chat.complete(
            model="mistral-large-latest",
            messages=[
                {"role": "system", "content": "Ты интервьюер. Пиши мысли для внутреннего лога."},
                {"role": "user", "content": prompt}
            ]
        )

        return response.choices[0].message.content.strip()

    def _end_interview(self):
        """Завершение интервью"""
        feedback = self.dispatcher.dispatch("generate_feedback", {
            "interview_log": self.logger.session_data,
            "position": self.position,
            "user_responses": self.user_responses
        })

        if not isinstance(feedback, dict) or 'verdict' not in feedback:
            feedback = self._get_default_feedback()

        self.logger.add_feedback(feedback)
        log_file = self.logger.save()
        candidate_name = self.candidate_name
        self.dispatcher.feedback._print_feedback_to_console(candidate_name, self.position, feedback)

        result = f"\n{'=' * 50}"
        result += f"\n✅ ИНТЕРВЬЮ ЗАВЕРШЕНО!"
        result += f"\n{'=' * 50}"
        result += f"\n📊 РЕЗУЛЬТАТЫ:"
        result += f"\n{'─' * 30}"
        result += f"\n🏆 Уровень: {feedback['verdict']['grade']}"
        result += f"\n📈 Рекомендация: {feedback['verdict']['recommendation']}"
        result += f"\n🎯 Уверенность: {feedback['verdict']['confidence_score']}%"
        result += f"\n❓ Вопросов: {self.question_count}"
        result += f"\n{'─' * 30}"
        result += f"\n📁 Лог: {log_file}"
        result += f"\n{'=' * 50}"

        return result

    def _get_default_feedback(self):
        return {
            "verdict": {"grade": "Junior", "recommendation": "Hire", "confidence_score": 75},
            "hard_skills": {"confirmed_skills": ["Основы"], "knowledge_gaps": []},
            "soft_skills": {"clarity": "Medium", "honesty": "High", "engagement": "Medium"},
            "roadmap": ["Продолжить обучение"]
        }