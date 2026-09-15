import importlib.util
import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent

MANAGER_FILE = (
    PROJECT_ROOT
    / "config"
    / "39_configured_retry_manager.py"
)


def load_class(file_path, class_name):

    spec = importlib.util.spec_from_file_location(
        class_name,
        file_path
    )

    if spec is None or spec.loader is None:
        raise ImportError(
            f"Could not load {file_path}"
        )

    module = importlib.util.module_from_spec(
        spec
    )

    spec.loader.exec_module(module)

    return getattr(module, class_name)


ConfiguredRetryManager = load_class(
    MANAGER_FILE,
    "ConfiguredRetryManager"
)


class LLMProductQueryParser:

    def __init__(self):

        config_module = importlib.util.spec_from_file_location(
            "zyra_config",
            PROJECT_ROOT / "config" / "18_config.py"
        )

        config = importlib.util.module_from_spec(
            config_module
        )

        config_module.loader.exec_module(config)

        error_module = importlib.util.spec_from_file_location(
            "error_classifier",
            PROJECT_ROOT / "config" / "34_llm_error_classification.py"
        )

        error_classifier = importlib.util.module_from_spec(
            error_module
        )

        error_module.loader.exec_module(
            error_classifier
        )

        self.manager = ConfiguredRetryManager(
            config,
            error_classifier
        )

    def parse(self, query):

        prompt = f"""
You are a product search filter extractor for an e-commerce store.

Convert the customer's request into JSON.

Allowed fields:
- query: product keyword or feature, otherwise null
- category: earrings, necklace, bangles, combo, otherwise null
- min_price: minimum price as a number, otherwise null
- max_price: maximum price as a number, otherwise null
- in_stock: true, false, or null

Return ONLY valid JSON.

Customer request:
{query}
"""

        result = self.manager.generate(prompt)

        if not result["success"]:

            raise RuntimeError(
                f"All LLM providers failed: "
                f"{result.get('error_type')}"
            )

        content = result["answer"].strip()

        if content.startswith("```"):

            content = content.replace(
                "```json",
                ""
            )

            content = content.replace(
                "```",
                ""
            )

            content = content.strip()

        filters = json.loads(content)

        filters["provider"] = result["provider"]

        return filters


if __name__ == "__main__":

    print("=" * 60)
    print("ZYRA LUXE - LLM PRODUCT QUERY PARSER")
    print("=" * 60)

    parser = LLMProductQueryParser()

    queries = [
        "I need oxidized earrings under 300 that are available",
        "Show me something for a wedding below 500",
        "I want bangles under ₹200",
        "Do you have earrings around 150?"
    ]

    for query in queries:

        print()
        print("-" * 60)
        print(f"Customer Query: {query}")

        try:

            result = parser.parse(query)

            print(f"Provider: {result['provider']}")

            print(
                f"Filters: {result}"
            )

        except Exception as error:

            print(
                f"Error: {error}"
            )

    print()
    print("=" * 60)
    print("LLM PRODUCT QUERY PARSER CHECK COMPLETED")
    print("=" * 60)