import os

from dotenv import load_dotenv
from pinecone import Pinecone
from langchain_google_genai import GoogleGenerativeAIEmbeddings


load_dotenv()

INDEX_NAME = "zyra-luxe-knowledge"
NAMESPACE = "knowledge"
EMBEDDING_MODEL = "models/gemini-embedding-001"

TOP_K = 5
MIN_SCORE = 0.60
MAX_CONTEXT_CHUNKS = 2


def create_embedding_model():
    return GoogleGenerativeAIEmbeddings(
        model=EMBEDDING_MODEL
    )


def search_policy(
    question: str,
    embeddings_model,
    index
):

    query_vector = embeddings_model.embed_query(
        question
    )

    results = index.query(
        vector=query_vector,
        top_k=TOP_K,
        namespace=NAMESPACE,
        include_metadata=True
    )

    return results


def compress_results(results):

    compressed = []

    seen_text = set()

    for match in results.matches:

        if match.score < MIN_SCORE:
            continue

        text = match.metadata.get("text", "").strip()

        if not text:
            continue

        if text in seen_text:
            continue

        seen_text.add(text)

        compressed.append({
            "score": match.score,
            "text": text,
            "title": match.metadata.get("title"),
            "url": match.metadata.get("url"),
            "page_type": match.metadata.get("page_type"),
        })

        if len(compressed) >= MAX_CONTEXT_CHUNKS:
            break

    return compressed


def display_context(
    question: str,
    context: list[dict]
):

    print()
    print("=" * 60)
    print("QUESTION")
    print("=" * 60)
    print(question)

    print()
    print("=" * 60)
    print("COMPRESSED CONTEXT")
    print("=" * 60)

    if not context:
        print("No sufficiently relevant context found.")
        return

    for index, item in enumerate(
        context,
        start=1
    ):

        print()
        print(f"Context {index}")
        print(f"Score: {item['score']}")
        print(f"Source: {item['title']}")
        print(f"Page Type: {item['page_type']}")
        print()
        print(item["text"])


if __name__ == "__main__":

    print("=" * 60)
    print("ZYRA LUXE - CONTEXT COMPRESSION")
    print("=" * 60)

    api_key = os.getenv(
        "PINECONE_API_KEY"
    )

    if not api_key:
        raise ValueError(
            "PINECONE_API_KEY not found in .env"
        )

    pc = Pinecone(
        api_key=api_key
    )

    index = pc.Index(
        INDEX_NAME
    )

    embeddings_model = create_embedding_model()

    print()
    print("Type 'exit' to stop.")

    while True:

        question = input(
            "\nQuestion: "
        ).strip()

        if question.lower() == "exit":
            break

        if not question:
            continue

        results = search_policy(
            question,
            embeddings_model,
            index
        )

        context = compress_results(
            results
        )

        display_context(
            question,
            context
        )

    print()
    print("Context compression stopped.")