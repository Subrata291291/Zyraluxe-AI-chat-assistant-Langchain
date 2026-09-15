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
        content: str,
        products: list[dict] | None = None
    ) -> None:

        self.create_session(session_id)

        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        }

        if products:
            message["products"] = products

        self.sessions[session_id].append(message)

    def get_history(self, session_id: str) -> list[dict]:

        return self.sessions.get(
            session_id,
            []
        )

    def get_recent_history(
        self,
        session_id: str,
        limit: int = 6
    ) -> list[dict]:

        history = self.sessions.get(
            session_id,
            []
        )

        return history[-limit:]

    def clear_session(self, session_id: str) -> None:

        self.sessions.pop(
            session_id,
            None
        )

    def session_exists(self, session_id: str) -> bool:

        return session_id in self.sessions


if __name__ == "__main__":

    print("=" * 60)
    print("SESSION MANAGER TEST")
    print("=" * 60)

    manager = SessionManager()

    session_id = "test-session"

    manager.add_message(
        session_id,
        "user",
        "Show me oxidized jewellery"
    )

    products = [
        {
            "name": "Designer Oxidized Jhumka",
            "url": "https://zyraluxe.in/product/designer-oxidized-jhumka/",
            "price": 160.0
        },
        {
            "name": "Antique Designer Oxidized Jhumka",
            "url": "https://zyraluxe.in/product/antique-designer-oxidized-jhumka/",
            "price": 120.0
        }
    ]

    manager.add_message(
        session_id,
        "assistant",
        "I found 2 products matching your request.",
        products=products
    )

    history = manager.get_history(
        session_id
    )

    print()
    print("Full History:")

    for message in history:
        print()
        print(message)

    recent_history = manager.get_recent_history(
        session_id,
        limit=1
    )

    print()
    print("Recent History:")
    print(recent_history)

    print()
    print("=" * 60)
    print("SESSION MANAGER TEST COMPLETED")
    print("=" * 60)