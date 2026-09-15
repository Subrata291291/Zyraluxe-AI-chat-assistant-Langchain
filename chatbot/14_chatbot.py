import os

from dotenv import load_dotenv
from langchain_google_genai import (
    ChatGoogleGenerativeAI,
    GoogleGenerativeAIEmbeddings,
)
from pinecone import Pinecone


load_dotenv()


INDEX_NAME = "zyra-luxe-knowledge"
NAMESPACE = "knowledge"
EMBEDDING_MODEL = "models/gemini-embedding-001"
MODEL_NAME = "gemini-3.5-flash"

TOP_K = 5
MIN_SCORE = 0.60
MAX_CONTEXT_CHUNKS = 2


def create_embeddings():

    return GoogleGenerativeAIEmbeddings(
        model=EMBEDDING_MODEL
    )


def create_llm():

    return ChatGoogleGenerativeAI(
        model=MODEL_NAME,
        temperature=0
    )


def create_index():

    api_key = os.getenv("PINECONE_API_KEY")

    if not api_key:
        raise ValueError(
            "PINECONE_API_KEY not found in .env"
        )

    pc = Pinecone(api_key=api_key)

    return pc.Index(INDEX_NAME)


def route_query(query: str) -> str:

    query_lower = query.lower()

    policy_keywords = [
        "return",
        "refund",
        "exchange",
        "privacy",
        "data",
        "personal information",
        "policy",
        "damaged",
        "defective",
        "shipping",
    ]

    product_keywords = [
        "price",
        "buy",
        "product",
        "earring",
        "necklace",
        "ring",
        "bracelet",
        "jewellery",
        "jewelry",
    ]

    order_keywords = [
        "order",
        "track",
        "delivery status",
        "where is my",
    ]

    if any(
        keyword in query_lower
        for keyword in order_keywords
    ):
        return "order"

    if any(
        keyword in query_lower
        for keyword in product_keywords
    ):
        return "product"

    if any(
        keyword in query_lower
        for keyword in policy_keywords
    ):
        return "policy"

    return "general"


def rewrite_query(query: str) -> str:

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

    return rewrites.get(
        query.lower().strip(),
        query
    )


def retrieve_context(
    query: str,
    embeddings,
    index
) -> list[dict]:

    query_vector = embeddings.embed_query(query)

    results = index.query(
        vector=query_vector,
        top_k=TOP_K,
        namespace=NAMESPACE,
        include_metadata=True
    )

    matches = results.get("matches", [])

    compressed = []
    seen_text = set()

    for match in matches:

        score = match.get("score", 0)

        if score < MIN_SCORE:
            continue

        metadata = match.get("metadata", {})
        text = metadata.get("text", "").strip()

        if not text:
            continue

        if text in seen_text:
            continue

        seen_text.add(text)

        compressed.append({
            "text": text,
            "title": metadata.get("title"),
            "page_type": metadata.get("page_type"),
            "url": metadata.get("url"),
            "score": score,
        })

        if len(compressed) >= MAX_CONTEXT_CHUNKS:
            break

    return compressed


def generate_answer(
    question: str,
    contexts: list[dict],
    llm
) -> str:

    if not contexts:
        return (
            "I don't have enough information in the "
            "available Zyra Luxe knowledge base to answer that."
        )

    context_text = "\n\n".join(
        item["text"]
        for item in contexts
    )

    prompt = f"""
You are Zyra Luxe AI Assistant.

Answer the user's question using ONLY the provided context.

Rules:
- Do not invent information.
- Do not use outside knowledge.
- Keep the answer concise and customer-friendly.
- If the context does not contain enough information, say:
"I don't have enough information in the available Zyra Luxe knowledge base to answer that."

Context:
{context_text}

User question:
{question}

Answer:
"""

    response = llm.invoke(prompt)

    content = response.content

    if isinstance(content, list):
        return content[0]["text"].strip()

    return str(content).strip()


def display_sources(contexts: list[dict]) -> None:

    print()
    print("Sources")
    print("-" * 60)

    displayed_urls = set()

    for item in contexts:

        url = item.get("url")

        if not url or url in displayed_urls:
            continue

        displayed_urls.add(url)

        print(f"Title: {item.get('title')}")
        print(f"URL: {url}")
        print(f"Score: {item.get('score'):.4f}")
        print()


def chatbot(
    question: str,
    embeddings,
    index,
    llm
):

    route = route_query(question)

    print()
    print(f"Route: {route}")

    if route == "order":
        return (
            "Order tracking will be connected to the "
            "live order system in a later step."
        ), []

    if route == "product":
        return (
            "Product search will be connected to the "
            "structured product database in a later step."
        ), []

    rewritten = rewrite_query(question)

    print(f"Search query: {rewritten}")

    contexts = retrieve_context(
        rewritten,
        embeddings,
        index
    )

    print(
        f"Retrieved context chunks: {len(contexts)}"
    )

    answer = generate_answer(
        question,
        contexts,
        llm
    )

    return answer, contexts


if __name__ == "__main__":

    print("=" * 60)
    print("ZYRA LUXE - RAG CHATBOT")
    print("=" * 60)

    if not os.getenv("GOOGLE_API_KEY"):
        raise ValueError(
            "GOOGLE_API_KEY not found in .env"
        )

    embeddings = create_embeddings()
    llm = create_llm()
    index = create_index()

    print()
    print("Type 'exit' to stop.")

    while True:

        question = input(
            "\nYou: "
        ).strip()

        if question.lower() == "exit":
            break

        if not question:
            continue

        try:

            answer, contexts = chatbot(
                question,
                embeddings,
                index,
                llm
            )

            print()
            print("Bot:")
            print(answer)

            if contexts:
                display_sources(contexts)

        except Exception as error:

            print()
            print("Chatbot error:")
            print(error)

    print()
    print("Chatbot stopped.")