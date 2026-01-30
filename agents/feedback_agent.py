
import json
from config import MISTRAL_CLIENT


class FeedbackAgent:
    def generate(self, interview_log, position, user_responses=None):
        """Генерация структурированного фидбэка с выводом в консоль"""
        user_responses = user_responses or []

        # Получаем имя кандидата из лога
        candidate_name = interview_log.get("participant_name", "Кандидат")

        # Собираем вопросы и ответы из лога
        qa_pairs = []
        turns = interview_log.get("turns", [])

        for turn in turns:
            if turn.get("agent_visible_message") and turn.get("user_message"):
                qa_pairs.append({
                    "question": turn["agent_visible_message"],
                    "answer": turn["user_message"]
                })

        prompt = f"""Ты - эксперт по оценке IT специалистов. Проанализируй интервью и создай детализированный фидбэк.

КОНТЕКСТ:
- Кандидат: {candidate_name}
- Позиция: {position}
- Количество вопросов: {len(qa_pairs)}

ВОПРОСЫ И ОТВЕТЫ:
{self._format_qa_pairs(qa_pairs)}

Проанализируй ответы кандидата и верни фидбэк в формате JSON со следующей структурой:
{{
  "verdict": {{
    "grade": "Junior / Middle / Senior",
    "recommendation": "Hire / No Hire / Strong Hire",
    "confidence_score": "число от 0 до 100"
  }},
  "hard_skills": {{
    "confirmed_skills": ["список тем, где кандидат дал точные ответы"],
    "knowledge_gaps": ["список тем, где были ошибки или кандидат сказал 'не знаю'"],
    "corrections": ["правильные ответы на вопросы, которые кандидат завалил"]
  }},
  "soft_skills": {{
    "clarity": "Low / Medium / High",
    "honesty": "Low / Medium / High", 
    "engagement": "Low / Medium / High"
  }},
  "roadmap": {{
    "topics": ["конкретные темы/технологии для изучения"],
    "resources": ["ссылки на документацию или статьи"]
  }}
}}

Важно: Для каждого knowledge_gap предоставь краткий правильный ответ в corrections."""

        try:
            response = MISTRAL_CLIENT.chat.complete(
                model="mistral-large-latest",
                messages=[
                    {"role": "system",
                     "content": "Ты эксперт по оценке IT специалистов. Анализируй ответы и давай структурированный фидбэк в JSON формате."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )

            content = response.choices[0].message.content.strip()

            # Извлекаем JSON из ответа
            json_start = content.find('{')
            json_end = content.rfind('}') + 1

            if json_start != -1 and json_end != 0:
                json_str = content[json_start:json_end]
                feedback_data = json.loads(json_str)

                # Валидация и форматирование данных
                feedback_data = self._validate_and_format_feedback(feedback_data)

                # Добавляем расширенные ресурсы
                feedback_data["roadmap_with_resources"] = self._add_learning_resources(
                    feedback_data.get("hard_skills", {}).get("knowledge_gaps", []),
                    position
                )

                # Выводим фидбэк в консоль
                self._print_feedback_to_console(candidate_name, position, feedback_data)

                return feedback_data
            else:
                print("⚠️ Не удалось найти JSON в ответе Mistral.")
                feedback_data = self._get_default_feedback(position, qa_pairs, candidate_name)
                self._print_feedback_to_console(candidate_name, position, feedback_data)
                return feedback_data

        except Exception as e:
            print(f"Ошибка генерации фидбэка: {e}")
            feedback_data = self._get_default_feedback(position, qa_pairs, candidate_name)
            self._print_feedback_to_console(candidate_name, position, feedback_data)
            return feedback_data

    def _print_feedback_to_console(self, candidate_name, position, feedback_data):
        """Выводит фидбэк в консоль в красивом формате"""
        print("\n" + "=" * 60)
        print("📊 ФИНАЛЬНЫЙ ФИДБЭК ПО ИНТЕРВЬЮ")
        print("=" * 60)
        print(f"👤 Кандидат: {candidate_name}")
        print(f"💼 Позиция: {position}")
        print("=" * 60)

        # А. Вердикт
        print("\n🎯 А. ВЕРДИКТ (Decision)")
        print("-" * 40)
        verdict = feedback_data.get("verdict", {})
        print(f"   Grade: {verdict.get('grade', 'Junior')}")
        print(f"   Hiring Recommendation: {verdict.get('recommendation', 'Hire')}")
        print(f"   Confidence Score: {verdict.get('confidence_score', 75)}%")

        # Б. Hard Skills
        print("\n💻 Б. АНАЛИЗ HARD SKILLS (Technical Review)")
        print("-" * 40)
        hard_skills = feedback_data.get("hard_skills", {})

        print("   ✅ Confirmed Skills:")
        for i, skill in enumerate(hard_skills.get("confirmed_skills", []), 1):
            print(f"      {i}. {skill}")

        print("\n   ❌ Knowledge Gaps:")
        knowledge_gaps = hard_skills.get("knowledge_gaps", [])
        corrections = hard_skills.get("corrections", [])

        for i, (gap, correction) in enumerate(zip(knowledge_gaps, corrections), 1):
            print(f"      {i}. {gap}")
            if i <= len(corrections):
                print(f"        💡 {correction}")

        # В. Soft Skills
        print("\n🗣️ В. АНАЛИЗ SOFT SKILLS & COMMUNICATION")
        print("-" * 40)
        soft_skills = feedback_data.get("soft_skills", {})
        print(f"   Clarity: {soft_skills.get('clarity', 'Medium')}")
        print(f"   Honesty: {soft_skills.get('honesty', 'Medium')}")
        print(f"   Engagement: {soft_skills.get('engagement', 'Medium')}")

        # Г. Roadmap
        print("\n📈 Г. ПЕРСОНАЛЬНЫЙ ROADMAP (Next Steps)")
        print("-" * 40)
        roadmap = feedback_data.get("roadmap", {})
        topics = roadmap.get("topics", [])
        resources = roadmap.get("resources", [])

        for i, topic in enumerate(topics, 1):
            print(f"   {i}. {topic}")
            if i <= len(resources):
                print(f"      🔗 {resources[i - 1]}")

        # Расширенные ресурсы
        roadmap_with_resources = feedback_data.get("roadmap_with_resources", [])
        if roadmap_with_resources:
            print("\n📚 ДОПОЛНИТЕЛЬНЫЕ РЕСУРСЫ:")
            for item in roadmap_with_resources[:3]:
                print(f"   • {item.get('topic', 'Тема')}")
                print(f"     📖 {item.get('description', 'Ресурс для изучения')}")
                print(f"     🔗 {item.get('resource', 'Ссылка')}")

        print("\n" + "=" * 60)
        print("✅ Фидбэк сгенерирован и сохранён в лог")
        print("=" * 60)

    def _validate_and_format_feedback(self, feedback_data):
        """Валидирует и форматирует фидбэк"""
        # Убедимся, что все необходимые поля существуют
        if "verdict" not in feedback_data:
            feedback_data["verdict"] = {}

        if "hard_skills" not in feedback_data:
            feedback_data["hard_skills"] = {}

        if "soft_skills" not in feedback_data:
            feedback_data["soft_skills"] = {}

        if "roadmap" not in feedback_data:
            feedback_data["roadmap"] = {}

        # Заполняем недостающие поля значениями по умолчанию
        verdict = feedback_data["verdict"]
        verdict.setdefault("grade", "Junior")
        verdict.setdefault("recommendation", "Hire")
        verdict.setdefault("confidence_score", 75)

        hard_skills = feedback_data["hard_skills"]
        hard_skills.setdefault("confirmed_skills", ["Базовые знания"])
        hard_skills.setdefault("knowledge_gaps", ["Требуется практика"])
        hard_skills.setdefault("corrections", ["Рекомендуется больше практиковаться"])

        soft_skills = feedback_data["soft_skills"]
        soft_skills.setdefault("clarity", "Medium")
        soft_skills.setdefault("honesty", "Medium")
        soft_skills.setdefault("engagement", "Medium")

        roadmap = feedback_data["roadmap"]
        roadmap.setdefault("topics", ["Практика на реальных проектах"])
        roadmap.setdefault("resources", ["https://roadmap.sh/"])

        return feedback_data

    def _format_qa_pairs(self, qa_pairs):
        """Форматирует вопросы и ответы для промпта"""
        if not qa_pairs:
            return "Нет вопросов и ответов в логе."

        formatted = []
        for i, pair in enumerate(qa_pairs[:6], 1):  # Берем первые 6 пар
            formatted.append(f"Вопрос {i}: {pair['question'][:200]}")
            formatted.append(f"Ответ {i}: {pair['answer'][:200]}")
            formatted.append("")
        return "\n".join(formatted)

    def _add_learning_resources(self, knowledge_gaps, position):
        """Добавляет расширенные ссылки на обучающие материалы"""
        resources_map = {
            "ml": {
                "Машинное обучение": {"url": "https://www.coursera.org/learn/machine-learning",
                                      "description": "Курс Andrew Ng по основам ML"},
                "Нейронные сети": {"url": "https://www.deeplearning.ai/courses/neural-networks-deep-learning/",
                                   "description": "Глубокое обучение от deeplearning.ai"},
                "Pandas/Numpy": {"url": "https://pandas.pydata.org/docs/",
                                 "description": "Официальная документация Pandas"},
                "Scikit-learn": {"url": "https://scikit-learn.org/stable/documentation.html",
                                 "description": "Документация Scikit-learn"},
                "PyTorch": {"url": "https://pytorch.org/tutorials/", "description": "Официальные туториалы PyTorch"}
            },
            "backend": {
                "Базы данных": {"url": "https://www.postgresql.org/docs/", "description": "Документация PostgreSQL"},
                "REST API": {"url": "https://restfulapi.net/", "description": "Руководство по REST API"},
                "Docker": {"url": "https://docs.docker.com/get-started/", "description": "Начало работы с Docker"},
                "Микросервисы": {"url": "https://microservices.io/",
                                 "description": "Паттерны микросервисной архитектуры"},
                "Алгоритмы": {"url": "https://leetcode.com/", "description": "Практика алгоритмов и структур данных"}
            },
            "frontend": {
                "React": {"url": "https://react.dev/learn", "description": "Официальное обучение React"},
                "JavaScript": {"url": "https://developer.mozilla.org/en-US/docs/Web/JavaScript",
                               "description": "MDN JavaScript документация"},
                "TypeScript": {"url": "https://www.typescriptlang.org/docs/", "description": "Документация TypeScript"},
                "CSS": {"url": "https://developer.mozilla.org/en-US/docs/Web/CSS",
                        "description": "MDN CSS документация"},
                "Веб-производительность": {"url": "https://web.dev/learn/",
                                           "description": "Оптимизация веб-производительности"}
            }
        }

        # Определяем категорию позиции
        category = self._detect_category(position)
        resources = resources_map.get(category, resources_map["backend"])

        roadmap_with_resources = []
        for gap in knowledge_gaps[:3]:  # Берем до 3 пробелов
            best_match = None
            for topic in resources:
                if any(word in gap.lower() for word in topic.lower().split()):
                    best_match = topic
                    break

            if best_match:
                roadmap_with_resources.append({
                    "topic": gap,
                    "resource": resources[best_match]["url"],
                    "description": resources[best_match]["description"],
                    "recommended_topic": best_match
                })
            else:
                roadmap_with_resources.append({
                    "topic": gap,
                    "resource": "https://learn.microsoft.com/en-us/training/",
                    "description": "Общие материалы по теме",
                    "recommended_topic": "Общие IT навыки"
                })

        return roadmap_with_resources

    def _detect_category(self, position):
        """Определяет IT категорию позиции"""
        pos_lower = position.lower()
        if any(word in pos_lower for word in ['ml', 'машин', 'data', 'ai', 'нейрон']):
            return 'ml'
        elif any(word in pos_lower for word in ['backend', 'бэкенд', 'api', 'server', 'java', 'python']):
            return 'backend'
        elif any(word in pos_lower for word in ['frontend', 'фронтенд', 'react', 'vue', 'javascript']):
            return 'frontend'
        elif any(word in pos_lower for word in ['qa', 'тестиров', 'test', 'quality']):
            return 'qa'
        elif any(word in pos_lower for word in ['devops', 'sre', 'инфраструктур', 'docker']):
            return 'devops'
        else:
            return 'backend'

    def _get_default_feedback(self, position, qa_pairs, candidate_name):
        """Резервный фидбэк при ошибке"""
        # Анализируем QA пары для определения уровня
        grade = "Junior"
        if qa_pairs and len(qa_pairs) > 3:
            avg_answer_length = sum(len(pair["answer"]) for pair in qa_pairs[:3]) / 3
            if avg_answer_length > 100:
                grade = "Middle"
            elif avg_answer_length > 200:
                grade = "Senior"

        return {
            "verdict": {
                "grade": grade,
                "recommendation": "Hire",
                "confidence_score": 75
            },
            "hard_skills": {
                "confirmed_skills": ["Базовые знания", "Понимание основных концепций"],
                "knowledge_gaps": ["Требуется практический опыт", "Углубление в конкретные технологии"],
                "corrections": [
                    "Рекомендуется больше практиковаться на реальных проектах",
                    "Изучить продвинутые концепции выбранной технологии"
                ]
            },
            "soft_skills": {
                "clarity": "Medium",
                "honesty": "High",
                "engagement": "Medium"
            },
            "roadmap": {
                "topics": [
                    "Практика на реальных проектах",
                    "Изучение современных технологий в области " + self._detect_category(position)
                ],
                "resources": [
                    "https://roadmap.sh/",
                    "https://github.com/practical-tutorials/project-based-learning"
                ]
            },
            "roadmap_with_resources": [
                {
                    "topic": "Общее развитие",
                    "resource": "https://learn.microsoft.com/",
                    "description": "Microsoft Learn - разнообразные курсы по IT",
                    "recommended_topic": "IT Fundamentals"
                }
            ]
        }