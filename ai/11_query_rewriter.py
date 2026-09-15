import os

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI


load_dotenv()

MODEL_NAME = "gemini-3.5-flash"


def create_llm():

    return ChatGoogleGenerativeAI(
        model=MODEL_NAME,
        temperature=0
    )


def simple_rewrite(query: str) -> str | None:

    query_lower = query.lower().strip()

    rewrites = {
        "refund how long?":
            "Zyra Luxe refund processing time",

        "can i send it back?":
            "Zyra Luxe return policy",

        "return?":
            "Zyra Luxe return policy",

        "refund?":
            "Zyra Luxe refund policy",

        "privacy?":
            "Zyra Luxe privacy policy",

        "do you sell my data?":
            "Does Zyra Luxe sell customer personal information?",
    }

    return rewrites.get(query_lower)


def rewrite_with_llm(
    query: str,
    llm
) -> str:

    prompt = f"""
Rewrite the user's query into a clear and specific
search query for the Zyra Luxe knowledge base.

Keep the original meaning.
Do not answer the question.
Do not add unsupported information.

Original query:
{query}

Rewritten search query:
"""

    response = llm.invoke(prompt)

    content = response.content

    if isinstance(content, list):
        return content[0]["text"].strip()

    return str(content).strip()


def rewrite_query(
    query: str,
    llm
) -> str:

    simple_result = simple_rewrite(query)

    if simple_result:
        return simple_result

    try:
        return rewrite_with_llm(
            query,
            llm
        )

    except Exception as error:

        print(
            f"Rewrite failed: {error}"
        )

        print(
            "Using original query."
        )

        return query


if __name__ == "__main__":

    print("=" * 60)
    print("ZYRA LUXE - QUERY REWRITER")
    print("=" * 60)

    api_key = os.getenv(
        "GOOGLE_API_KEY"
    )

    if not api_key:
        raise ValueError(
            "GOOGLE_API_KEY not found in .env"
        )

    llm = create_llm()

    print()
    print("Type 'exit' to stop.")

    while True:

        query = input(
            "\nOriginal query: "
        ).strip()

        if query.lower() == "exit":
            break

        if not query:
            continue

        rewritten = rewrite_query(
            query,
            llm
        )

        print()
        print(
            f"Rewritten query: {rewritten}"
        )

    print()
    print("Query rewriting stopped.")