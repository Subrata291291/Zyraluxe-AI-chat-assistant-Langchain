import json
from pathlib import Path

from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec
import os


load_dotenv()

INPUT_FILE = Path("data/policies/embeddings.json")

INDEX_NAME = "zyra-luxe-knowledge"
CLOUD = "aws"
REGION = "us-east-1"


def load_embeddings() -> list[dict]:

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Input file not found: {INPUT_FILE}"
        )

    with INPUT_FILE.open(
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


def create_pinecone_index(
    pc: Pinecone,
    dimension: int
):

    existing_indexes = pc.list_indexes().names()

    if INDEX_NAME in existing_indexes:
        print(
            f"Index already exists: {INDEX_NAME}"
        )
        return

    print(
        f"Creating index: {INDEX_NAME}"
    )

    pc.create_index(
        name=INDEX_NAME,
        dimension=dimension,
        metric="cosine",
        spec=ServerlessSpec(
            cloud=CLOUD,
            region=REGION
        )
    )

    print("Index created.")


def upload_vectors(
    pc: Pinecone,
    embeddings: list[dict]
):

    index = pc.Index(INDEX_NAME)

    vectors = []

    for item in embeddings:

        vectors.append({
            "id": item["chunk_id"],
            "values": item["embedding"],
            "metadata": {
                "text": item["text"],
                "page_type": item["metadata"]["page_type"],
                "title": item["metadata"]["title"],
                "url": item["metadata"]["url"],
                "chunk_index": item["metadata"]["chunk_index"],
            }
        })

    index.upsert(
        vectors=vectors,
        namespace="knowledge"
    )

    print(
        f"Vectors uploaded: {len(vectors)}"
    )


if __name__ == "__main__":

    print("=" * 60)
    print("ZYRA LUXE - PINECONE VECTOR UPLOAD")
    print("=" * 60)

    api_key = os.getenv("PINECONE_API_KEY")

    if not api_key:
        raise ValueError(
            "PINECONE_API_KEY not found in .env"
        )

    embeddings = load_embeddings()

    print(
        f"Embeddings loaded: {len(embeddings)}"
    )

    if not embeddings:
        raise ValueError(
            "No embeddings found."
        )

    dimension = len(
        embeddings[0]["embedding"]
    )

    print(
        f"Vector dimension: {dimension}"
    )

    pc = Pinecone(
        api_key=api_key
    )

    create_pinecone_index(
        pc,
        dimension
    )

    upload_vectors(
        pc,
        embeddings
    )

    print()
    print("=" * 60)
    print("PINECONE UPLOAD COMPLETED")
    print("=" * 60)