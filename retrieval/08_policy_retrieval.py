import os

from dotenv import load_dotenv
from pinecone import Pinecone
from langchain_google_genai import GoogleGenerativeAIEmbeddings


load_dotenv()

INDEX_NAME = "zyra-luxe-knowledge"
NAMESPACE = "knowledge"
EMBEDDING_MODEL = "models/gemini-embedding-001"


def create_embedding_model():
    return GoogleGenerativeAIEmbeddings(
        model=EMBEDDING_MODEL
    )


def search_policy(
    question: str,
    embeddings_model,
    index,
    top_k: int = 3
):

    query_vector = embeddings_model.embed_query(
        question
    )

    results = index.query(
        vector=query_vector,
        top_k=top_k,
        namespace=NAMESPACE,
        include_metadata=True
    )

    return results


def display_results(
    question: str,
    results
):

    print()
    print("=" * 60)
    print("QUESTION")
    print("=" * 60)
    print(question)

    print()
    print("=" * 60)
    print("RETRIEVED RESULTS")
    print("=" * 60)

    for rank, match in enumerate(
        results.matches,
        start=1
    ):

        metadata = match.metadata

        print()
        print(f"Rank: {rank}")
        print(f"Score: {match.score}")
        print(f"Source: {metadata.get('title')}")
        print(f"Page Type: {metadata.get('page_type')}")
        print()
        print(metadata.get("text"))


if __name__ == "__main__":

    print("=" * 60)
    print("ZYRA LUXE - POLICY RETRIEVAL")
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

        display_results(
            question,
            results
        )

    print()
    print("Retrieval stopped.")