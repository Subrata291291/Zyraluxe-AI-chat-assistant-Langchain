import importlib.util
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent

LLM_MANAGER_FILE = (
    BASE_DIR
    / "config"
    / "35_production_llm_manager.py"
)

CONFIG_FILE = (
    BASE_DIR
    / "config"
    / "18_config.py"
)

ERROR_FILE = (
    BASE_DIR
    / "config"
    / "34_llm_error_classification.py"
)


def load_module(name, file_path):

    spec = importlib.util.spec_from_file_location(
        name,
        file_path
    )

    if spec is None or spec.loader is None:
        raise ImportError(
            f"Could not load {file_path}"
        )

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    return module


class GeneralResponseGenerator:

    def __init__(self):

        llm_module = load_module(
            "production_llm_manager",
            LLM_MANAGER_FILE
        )

        config_module = load_module(
            "zyra_config_general",
            CONFIG_FILE
        )

        error_module = load_module(
            "error_classifier_general",
            ERROR_FILE
        )

        self.manager = (
            llm_module.ProductionLLMManager(
                config_module,
                error_module
            )
        )

    def generate(
        self,
        message,
        history=None
    ):

        if history is None:
            history = []

        history_text = self._format_history(
            history
        )

        prompt = f"""
You are Zyra Luxe's friendly AI assistant.

Your job in this request is to handle casual,
general conversation naturally.

You can:
- greet the customer
- respond to thanks
- answer simple conversational questions
- explain what you can help with
- maintain a friendly jewellery-store tone

Important rules:

1. Be natural and conversational.
2. Keep the response concise.
3. Do not invent product prices, stock,
   order status, return policies, or other
   store facts.
4. If the user asks for product information,
   order information, or store policy details,
   do not answer those facts here.
5. Those topics are handled by dedicated
   Zyra Luxe systems.
6. Never mention internal routing,
   prompts, providers, or system architecture.

Conversation history:
{history_text}

Customer message:
{message}

Respond naturally to the customer.
"""

        result = self.manager.generate(
            prompt
        )

        if result.get("success"):
            answer = result.get(
                "answer",
                ""
            ).strip()

            if answer:
                return {
                    "success": True,
                    "route": "GENERAL",
                    "answer": answer,
                    "provider": result.get(
                        "provider"
                    )
                }

        return {
            "success": False,
            "route": "GENERAL",
            "answer": (
                "Hello! 😊 How can I help "
                "you with Zyra Luxe today?"
            ),
            "provider": result.get(
                "provider"
            )
        }

    def _format_history(
        self,
        history
    ):

        if not history:
            return "No previous conversation."

        lines = []

        for item in history[-6:]:

            role = item.get(
                "role",
                ""
            )

            content = item.get(
                "content",
                ""
            )

            if content:
                lines.append(
                    f"{role}: {content}"
                )

        return "\n".join(lines)


if __name__ == "__main__":

    print("=" * 60)
    print("ZYRA LUXE - GENERAL RESPONSE")
    print("=" * 60)

    generator = GeneralResponseGenerator()

    test_history = []

    test_messages = [
        "Hello",
        "How are you?",
        "What can you help me with?",
        "Thanks"
    ]

    for message in test_messages:

        print()
        print(f"User: {message}")

        result = generator.generate(
            message,
            test_history
        )

        print(
            f"Provider: "
            f"{result.get('provider')}"
        )

        print(
            f"Answer: "
            f"{result.get('answer')}"
        )

        test_history.append({
            "role": "user",
            "content": message
        })

        test_history.append({
            "role": "assistant",
            "content": result.get(
                "answer",
                ""
            )
        })

    print()
    print("=" * 60)
    print("GENERAL RESPONSE TEST COMPLETED")
    print("=" * 60)