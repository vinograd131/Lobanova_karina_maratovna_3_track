
from agents import InterviewerAgent, ObserverAgent, FeedbackAgent
from knowledge_base import ITKnowledgeBase


class InterviewDispatcher:
    def __init__(self):
        self.interviewer = None
        self.observer = ObserverAgent()
        self.feedback = FeedbackAgent()
        self.knowledge_base = ITKnowledgeBase()

    def init_interviewer(self, name, position):
        self.interviewer = InterviewerAgent(name, position, self.knowledge_base)
        return self.interviewer

    def dispatch(self, action, args):
        if action == "analyze":
            return self.observer.analyze(
                user_response=args["user_response"],
                position=args["position"],
                question=args.get("question", "")
            )
        elif action == "generate_question":
            if not self.interviewer:
                raise ValueError("Interviewer не инициализирован")
            return self.interviewer.generate_question(
                instruction=args["instruction"],
                question_count=args.get("question_count", 1)  # Исправлено здесь
            )
        elif action == "handle_offtopic":
            if not self.interviewer:
                raise ValueError("Interviewer не инициализирован")
            return self.interviewer.handle_offtopic(args["user_input"])
        elif action == "generate_feedback":
            return self.feedback.generate(
                interview_log=args["interview_log"],
                position=args["position"],
                user_responses=args.get("user_responses", [])
            )
        else:
            raise ValueError(f"Неизвестное действие: {action}")