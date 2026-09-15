import importlib.util
from pathlib import Path

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langchain_openrouter import ChatOpenRouter
from langchain_openai import ChatOpenAI


CONFIG_FILE = Path(__file__).parent / "18_config.py"


class LLMProviderManager:

    def __init__(self, config):

        self.config = config
        self.providers = self._create_providers()

    def _create_providers(self):

        return [
            (
                "gemini",
                ChatGoogleGenerativeAI(
                    model=self.config.LLM_MODEL,
                    temperature=0
                )
            ),
            (
                "groq",
                ChatGroq(
                    model="llama-3.1-8b-instant",
                    temperature=0
                )
            ),
            (
                "openrouter",
                ChatOpenRouter(
                    model="openai/gpt-oss-20b",
                    temperature=0
                )
            ),
            (
                "openai",
                ChatOpenAI(
                    model="gpt-5-nano",
                    temperature=0
                )
            )
        ]

    def _extract_content(self, response):

        content = response.content

        if isinstance(content, list):

            text_parts = []

            for item in content:

                if isinstance(item, dict):
                    if item.get("type") == "text":
                        text_parts.append(
                            item.get("text", "")
                        )

            return "".join(text_parts)

        return str(content)

    def generate(self, prompt):

        for provider, llm in self.providers:

            try:

                print(f"Trying provider: {provider}")

                response = llm.invoke(prompt)

                answer = self._extract_content(response)

                return {
                    "success": True,
                    "provider": provider,
                    "answer": answer
                }

            except Exception as error:

                print(
                    f"{provider} failed: {error}"
                )

        return {
            "success": False,
            "provider": None,
            "answer": None
        }


def load_config():

    spec = importlib.util.spec_from_file_location(
        "zyra_config",
        CONFIG_FILE
    )

    if spec is None or spec.loader is None:
        raise ImportError("Could not load configuration.")

    config = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(config)

    return config


if __name__ == "__main__":

    print("=" * 60)
    print("ZYRA LUXE - LLM PROVIDER MANAGER")
    print("=" * 60)

    config = load_config()

    manager = LLMProviderManager(config)

    prompt = """
    Answer in one short sentence:

    What is a return policy?
    """

    result = manager.generate(prompt)

    print()
    print("=" * 60)
    print("RESULT")
    print("=" * 60)

    print(f"Success: {result['success']}")
    print(f"Provider: {result['provider']}")
    print(f"Answer: {result['answer']}")

    print()
    print("=" * 60)
    print("LLM PROVIDER MANAGER CHECK COMPLETED")
    print("=" * 60)