import importlib.util
from pathlib import Path

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langchain_openrouter import ChatOpenRouter
from langchain_openai import ChatOpenAI


CONFIG_FILE = Path(__file__).parent / "18_config.py"


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


def extract_content(response):

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


def create_llm_chain(config):

    return [
        (
            "gemini",
            ChatGoogleGenerativeAI(
                model="invalid-gemini-model",
                temperature=0
            )
        ),
        (
            "groq",
            ChatGroq(
                model="llama-3.3-70b-versatile",
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


def test_fallback(prompt, llm_chain):

    for provider, llm in llm_chain:

        try:

            print()
            print(f"Trying: {provider}")

            response = llm.invoke(prompt)

            answer = extract_content(response)

            print(f"{provider} succeeded.")

            return {
                "success": True,
                "provider": provider,
                "answer": answer
            }

        except Exception as error:

            print(f"{provider} failed.")
            print(f"Error: {error}")

    return {
        "success": False,
        "provider": None,
        "answer": None
    }


if __name__ == "__main__":

    print("=" * 60)
    print("ZYRA LUXE - FALLBACK TEST")
    print("=" * 60)

    config = load_config()

    llm_chain = create_llm_chain(config)

    prompt = """
    Answer in one short sentence:

    What is customer service?
    """

    result = test_fallback(
        prompt,
        llm_chain
    )

    print()
    print("=" * 60)
    print("FINAL RESULT")
    print("=" * 60)

    print(f"Success: {result['success']}")
    print(f"Provider: {result['provider']}")
    print(f"Answer: {result['answer']}")

    print()
    print("=" * 60)
    print("FALLBACK TEST COMPLETED")
    print("=" * 60)