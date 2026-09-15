from datetime import datetime


class SessionManager:

    def __init__(self):
        self.sessions = {}

    def create_session(self, session_id: str) -> None:

        if session_id not in self.sessions:
            self.sessions[session_id] = []

    def add_message(
        self,
        session_id: str,
        role: str,
        content: str
    ) -> None:

        self.create_session(session_id)

        self.sessions[session_id].append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })

    def get_history(
        self,
        session_id: str
    ) -> list[dict]:

        return self.sessions.get(
            session_id,
            []
        )

    def clear_session(
        self,
        session_id: str
    ) -> None:

        self.sessions.pop(
            session_id,
            None
        )

    def session_exists(
        self,
        session_id: str
    ) -> bool:

        return session_id in self.sessions


if __name__ == "__main__":

    print("=" * 60)
    print("ZYRA LUXE - SESSION MANAGER")
    print("=" * 60)

    manager = SessionManager()

    session_id = "user-001"

    manager.create_session(session_id)

    manager.add_message(
        session_id,
        "user",
        "Can I return an item?"
    )

    manager.add_message(
        session_id,
        "assistant",
        "Yes, you can request a return within 2 hours of delivery."
    )

    manager.add_message(
        session_id,
        "user",
        "What about sale items?"
    )

    manager.add_message(
        session_id,
        "assistant",
        "Sale items are non-returnable."
    )

    print()
    print(f"Session ID: {session_id}")

    print()
    print("Conversation History")
    print("-" * 60)

    history = manager.get_history(session_id)

    for message in history:

        print(
            f"{message['role'].upper()}: "
            f"{message['content']}"
        )

    print()
    print(f"Total messages: {len(history)}")

    print()
    print("=" * 60)
    print("SESSION MANAGER COMPLETED")
    print("=" * 60)