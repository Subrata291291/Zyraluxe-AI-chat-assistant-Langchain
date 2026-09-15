import importlib.util
from pathlib import Path


CONFIG_FILE = (
    Path(__file__).parent / "18_config.py"
)


def load_config():

    spec = importlib.util.spec_from_file_location(
        "zyra_config",
        CONFIG_FILE
    )

    if spec is None or spec.loader is None:
        raise ImportError(
            "Could not load configuration."
        )

    config = importlib.util.module_from_spec(
        spec
    )

    spec.loader.exec_module(config)

    return config


def create_llm(config):

    from langchain_google_genai import (
        ChatGoogleGenerativeAI
    )

    return ChatGoogleGenerativeAI(
        model=config.LLM_MODEL,
        temperature=0
    )


def stream_answer(
    question: str,
    context: str,
    llm
):

    prompt = f"""
You are Zyra Luxe AI Assistant.

Answer the user's question using ONLY
the provided context.

Rules:
- Do not invent information.
- Do not use outside knowledge.
- Keep the answer concise and customer-friendly.
- If the context does not contain enough information, say:
"I don't have enough information in the available Zyra Luxe knowledge base to answer that."

Context:
{context}

User question:
{question}

Answer:
"""

    for chunk in llm.stream(prompt):

        content = chunk.content

        if isinstance(content, list):

            for item in content:

                if isinstance(item, dict):
                    text = item.get(
                        "text",
                        ""
                    )

                    if text:
                        yield text

                elif isinstance(item, str):

                    yield item

        elif content:

            yield str(content)


if __name__ == "__main__":

    print("=" * 60)
    print("ZYRA LUXE - STREAMING RESPONSE")
    print("=" * 60)

    config = load_config()

    llm = create_llm(config)

    question = (
        "How long does a refund take?"
    )

    context = """
Refunds will be processed within 7–10 business days
after the returned product has been received and inspected.
"""

    print()
    print("Question:")
    print(question)

    print()
    print("Streaming Answer:")
    print()

    try:

        for text in stream_answer(
            question,
            context,
            llm
        ):

            print(
                text,
                end="",
                flush=True
            )

        print()

    except Exception as error:

        print()
        print("Streaming Error:")
        print(error)

    print()
    print("=" * 60)
    print("STREAMING RESPONSE COMPLETED")
    print("=" * 60)