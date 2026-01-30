
import json
import os
from datetime import datetime


class InterviewLogger:
    def __init__(self, logs_dir="sessions"):
        self.logs_dir = logs_dir
        self.session_data = None
        if not os.path.exists(logs_dir):
            os.makedirs(logs_dir)

    def start_session(self, name, position):
        self.session_data = {
            "participant_name": name,
            "position": position,
            "start_time": datetime.now().isoformat(),
            "turns": []
        }

    def add_turn(self, agent_msg, user_msg, internal):
        if not self.session_data:
            return

        turn = {
            "turn_id": len(self.session_data["turns"]) + 1,
            "agent_visible_message": agent_msg,
            "user_message": user_msg,
            "internal_thoughts": internal,  # Сохраняем полные мысли
            "timestamp": datetime.now().isoformat()
        }

        self.session_data["turns"].append(turn)

    def add_feedback(self, feedback):
        if self.session_data:
            self.session_data["final_feedback"] = feedback

    def save(self):
        if not self.session_data:
            return None

        filename = f"sessions/Лобанова_Карина_Маратовна_сценарий_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.session_data, f, ensure_ascii=False, indent=2)

        print(f"✅ Лог сохранён: {filename}")
        return filename