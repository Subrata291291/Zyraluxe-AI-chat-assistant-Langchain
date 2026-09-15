import importlib.util
import time
from pathlib import Path

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langchain_openrouter import ChatOpenRouter
from langchain_openai import ChatOpenAI


CONFIG_FILE = Path(__file__).parent / "18_config.py"
ERROR_FILE = Path(__file__).parent / "34_llm_error_classification.py"


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


class ConfiguredRetryManager:

    def __init__(self, config, error_classifier):

        self.config = config
        self.error_classifier = error_classifier

        self.max_retries = (
            config.MAX_LLM_RETRIES
        )

        self.base_delay = (
            config.RETRY_BASE_DELAY
        )

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
                    model="openai/gpt-oss-20b",
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

    def _try_provider(
        self,
        provider,
        llm,
        prompt
    ):

        for attempt in range(
            self.max_retries + 1
        ):

            try:

                print(
                    f"Trying {provider} "
                    f"(attempt {attempt + 1})"
                )

                response = llm.invoke(prompt)

                answer = self._extract_content(
                    response
                )

                return {
                    "success": True,
                    "answer": answer
                }

            except Exception as error:

                analysis = (
                    self.error_classifier
                    .analyze_error(error)
                )

                print(
                    f"{provider} error: "
                    f"{analysis['error_type']}"
                )

                if not analysis["should_fallback"]:

                    return {
                        "success": False,
                        "answer": None,
                        "stop": True,
                        "error_type": (
                            analysis["error_type"]
                        )
                    }

                if attempt < self.max_retries:

                    delay = (
                        self.base_delay
                        * (2 ** attempt)
                    )

                    print(
                        f"Retrying in "
                        f"{delay} seconds..."
                    )

                    time.sleep(delay)

        return {
            "success": False,
            "answer": None,
            "stop": False,
            "error_type": "provider_failed"
        }

    def generate(self, prompt):

        for provider, llm in self.providers:

            result = self._try_provider(
                provider,
                llm,
                prompt
            )

            if result["success"]:

                return {
                    "success": True,
                    "provider": provider,
                    "answer": result["answer"]
                }

            if result.get("stop"):

                return {
                    "success": False,
                    "provider": provider,
                    "answer": None,
                    "error_type": result["error_type"]
                }

            print(
                f"Moving to next provider "
                f"after {provider} failure..."
            )

        return {
            "success": False,
            "provider": None,
            "answer": None,
            "error_type": "all_providers_failed"
        }


if __name__ == "__main__":

    print("=" * 60)
    print("ZYRA LUXE - CONFIGURED RETRY MANAGER")
    print("=" * 60)

    config = load_module(
        "zyra_config",
        CONFIG_FILE
    )

    error_classifier = load_module(
        "error_classifier",
        ERROR_FILE
    )

    manager = ConfiguredRetryManager(
        config,
        error_classifier
    )

    print()
    print(
        f"Max Retries: "
        f"{manager.max_retries}"
    )

    print(
        f"Base Delay: "
        f"{manager.base_delay} seconds"
    )

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

    if "error_type" in result:
        print(
            f"Error Type: "
            f"{result['error_type']}"
        )

    print()
    print("=" * 60)
    print("CONFIGURED RETRY MANAGER CHECK COMPLETED")
    print("=" * 60)