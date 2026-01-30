
import os
import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer


class ITKnowledgeBase:
    """RAG база знаний для всех IT собеседований"""

    def __init__(self, model_name="sentence-transformers/all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)
        self.index = None
        self.documents = []
        self.metadata = []

    def load_default_knowledge(self):
        """Загружает базовые IT знания для всех направлений"""
        it_knowledge = [
            # Backend разработка
            {
                "text": "Java Spring Framework: фреймворк для создания enterprise приложений на Java. Основные модули: Spring Core, Spring MVC, Spring Boot.",
                "category": "backend", "topic": "frameworks", "position": "Backend Developer"},
            {
                "text": "Python Django: высокоуровневый Python веб-фреймворк, который позволяет быстро создавать безопасные и поддерживаемые веб-сайты.",
                "category": "backend", "topic": "frameworks", "position": "Backend Developer"},
            {
                "text": "Node.js: среда выполнения JavaScript на стороне сервера, построенная на движке V8 от Chrome. Используется для создания масштабируемых сетевых приложений.",
                "category": "backend", "topic": "languages", "position": "Backend Developer"},
            {
                "text": "Базы данных: реляционные (PostgreSQL, MySQL) vs NoSQL (MongoDB, Redis). Транзакции, индексы, нормализация.",
                "category": "backend", "topic": "databases", "position": "Backend Developer"},
            {
                "text": "REST API vs GraphQL: REST использует различные HTTP методы, GraphQL имеет единую точку входа и позволяет клиенту запрашивать нужные данные.",
                "category": "backend", "topic": "api", "position": "Backend Developer"},
            {
                "text": "Микросервисная архитектура: подход к разработке приложений как набора небольших сервисов, каждый из которых работает в собственном процессе.",
                "category": "backend", "topic": "architecture", "position": "Backend Developer"},

            # Frontend разработка
            {
                "text": "React: JavaScript библиотека для создания пользовательских интерфейсов. Основные концепции: компоненты, состояния, пропсы, хуки.",
                "category": "frontend", "topic": "frameworks", "position": "Frontend Developer"},
            {
                "text": "Vue.js: прогрессивный JavaScript фреймворк для создания UI. Отличия: реактивность, директивы, компоненты.",
                "category": "frontend", "topic": "frameworks", "position": "Frontend Developer"},
            {
                "text": "TypeScript: типизированное надмножество JavaScript, компилируемое в чистый JavaScript. Преимущества: статическая типизация, улучшенный автокомплит.",
                "category": "frontend", "topic": "languages", "position": "Frontend Developer"},
            {
                "text": "CSS Flexbox и Grid: современные методы верстки. Flexbox для одномерных макетов, Grid для двумерных.",
                "category": "frontend", "topic": "styling", "position": "Frontend Developer"},
            {"text": "Веб-производительность: оптимизация загрузки, lazy loading, code splitting, кэширование.",
             "category": "frontend", "topic": "performance", "position": "Frontend Developer"},
            {
                "text": "Accessibility (a11y): обеспечение доступности веб-сайтов для людей с ограниченными возможностями.",
                "category": "frontend", "topic": "best practices", "position": "Frontend Developer"},

            # QA/Тестирование
            {
                "text": "Тест-кейс: документированная последовательность шагов для проверки конкретной функции. Должен содержать: предусловия, шаги, ожидаемый результат.",
                "category": "qa", "topic": "testing basics", "position": "QA Engineer"},
            {"text": "Виды тестирования: функциональное, регрессионное, нагрузочное, usability, security тестирование.",
             "category": "qa", "topic": "testing types", "position": "QA Engineer"},
            {"text": "Selenium: фреймворк для автоматизации веб-приложений. Поддерживает多种语言包括 Java, Python, C#.",
             "category": "qa", "topic": "automation", "position": "QA Engineer"},
            {
                "text": "API тестирование: проверка взаимодействия между различными программными компонентами. Инструменты: Postman, SoapUI.",
                "category": "qa", "topic": "api testing", "position": "QA Engineer"},
            {
                "text": "Bug Report: документ, описывающий найденный дефект. Должен содержать: заголовок, шаги воспроизведения, фактический и ожидаемый результат.",
                "category": "qa", "topic": "bug reporting", "position": "QA Engineer"},
            {
                "text": "Тестирование мобильных приложений: особенности тестирования на iOS и Android, эмуляторы vs реальные устройства.",
                "category": "qa", "topic": "mobile testing", "position": "QA Engineer"},

            # DevOps/Инфраструктура
            {
                "text": "Docker: платформа для контейнеризации приложений. Основные команды: docker build, docker run, docker-compose.",
                "category": "devops", "topic": "containers", "position": "DevOps Engineer"},
            {
                "text": "Kubernetes: система оркестрации контейнеров. Основные понятия: pod, service, deployment, namespace.",
                "category": "devops", "topic": "orchestration", "position": "DevOps Engineer"},
            {"text": "CI/CD: Continuous Integration/Continuous Deployment. Jenkins, GitLab CI, GitHub Actions.",
             "category": "devops", "topic": "automation", "position": "DevOps Engineer"},
            {"text": "Инфраструктура как код (IaC): Terraform, Ansible, CloudFormation для управления инфраструктурой.",
             "category": "devops", "topic": "infrastructure", "position": "DevOps Engineer"},
            {"text": "Мониторинг: Prometheus для сбора метрик, Grafana для визуализации, ELK stack для логов.",
             "category": "devops", "topic": "monitoring", "position": "DevOps Engineer"},
            {"text": "Облачные платформы: AWS, Azure, Google Cloud. Основные сервисы: вычисления, хранение, сети.",
             "category": "devops", "topic": "cloud", "position": "DevOps Engineer"},

            # Data Science/ML
            {
                "text": "Машинное обучение: supervised learning (классификация, регрессия), unsupervised learning (кластеризация), reinforcement learning.",
                "category": "ml", "topic": "ml basics", "position": "Data Scientist"},
            {
                "text": "Библиотеки Python: NumPy для численных вычислений, Pandas для анализа данных, Scikit-learn для ML алгоритмов.",
                "category": "ml", "topic": "libraries", "position": "Data Scientist"},
            {"text": "Нейронные сети: CNN для изображений, RNN/LSTM для последовательностей, Transformers для NLP.",
             "category": "ml", "topic": "neural networks", "position": "Data Scientist"},
            {"text": "Обработка естественного языка (NLP): токенизация, стемминг, лемматизация, word embeddings.",
             "category": "ml", "topic": "nlp", "position": "Data Scientist"},
            {
                "text": "Data Engineering: ETL процессы, Apache Spark для обработки больших данных, Airflow для оркестрации.",
                "category": "ml", "topic": "data engineering", "position": "Data Engineer"},
            {"text": "Хранение данных: data lakes vs data warehouses, SQL vs NoSQL для аналитики.",
             "category": "ml", "topic": "data storage", "position": "Data Engineer"},

            # Общие IT концепции
            {"text": "ООП: инкапсуляция, наследование, полиморфизм, абстракция. Принципы SOLID.",
             "category": "general", "topic": "programming paradigms", "position": "All IT"},
            {"text": "Алгоритмы и структуры данных: массивы, списки, стеки, очереди, хэш-таблицы, деревья, графы.",
             "category": "general", "topic": "algorithms", "position": "All IT"},
            {"text": "Сложность алгоритмов: Big O нотация. O(1), O(log n), O(n), O(n log n), O(n²), O(2^n).",
             "category": "general", "topic": "complexity", "position": "All IT"},
            {"text": "Паттерны проектирования: Singleton, Factory, Observer, Strategy, Decorator.",
             "category": "general", "topic": "design patterns", "position": "All IT"},
            {
                "text": "Git: система контроля версий. Основные команды: clone, commit, push, pull, branch, merge, rebase.",
                "category": "general", "topic": "version control", "position": "All IT"},
            {"text": "Agile методологии: Scrum, Kanban. Спринты, daily standups, ретроспективы.",
             "category": "general", "topic": "methodologies", "position": "All IT"},
        ]

        self.documents = [item["text"] for item in it_knowledge]
        self.metadata = it_knowledge

        # Создаём векторный индекс
        embeddings = self.model.encode(self.documents)
        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dimension)
        self.index.add(embeddings.astype('float32'))

        print(f"✅ Загружено {len(self.documents)} документов IT знаний для всех направлений")
        return self

    def get_position_context(self, position):
        """Возвращает контекст для конкретной позиции"""
        relevant_docs = []
        for i, meta in enumerate(self.metadata):
            if meta["position"] == position or meta["position"] == "All IT":
                relevant_docs.append(self.documents[i])

        if relevant_docs:
            return "Контекст для позиции:\n" + "\n".join(relevant_docs[:5])
        return ""

    def search_by_position(self, position, query, k=3):
        """Ищет знания для конкретной позиции"""
        # Сначала находим категорию позиции
        category_map = {
            "backend": ["backend developer", "бэкенд", "back-end"],
            "frontend": ["frontend developer", "фронтенд", "front-end"],
            "qa": ["qa engineer", "тестировщик", "quality assurance"],
            "devops": ["devops engineer", "инфраструктура"],
            "ml": ["data scientist", "ml engineer", "data engineer", "машинное обучение"]
        }

        category = "general"
        for cat, keywords in category_map.items():
            if any(keyword in position.lower() for keyword in keywords):
                category = cat
                break

        return self.search(query, category=category, k=k)