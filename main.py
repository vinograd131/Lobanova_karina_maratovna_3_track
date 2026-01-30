
import os
from dotenv import load_dotenv
from interview_loop import InterviewSystem

load_dotenv()


def main():
    print("=" * 50)
    print("🤖 IT ИНТЕРВЬЮ СИСТЕМА")
    print("=" * 50)
    print("Система задает вопросы. Отвечайте подробно.")
    print("Для завершения напишите 'стоп'")
    print("=" * 50)

    name = input("\n👤 Ваше имя: ").strip()
    position = input("💼 Позиция (например, Data Scientist): ").strip()

    system = InterviewSystem()
    system.start_interview(name, position)

    while True:
        user_input = input("\n📝 Ответ: ").strip()

        if not user_input:
            continue

        response = system.process_response(user_input)

        if response:
            print(response)
            break


if __name__ == "__main__":
    main()