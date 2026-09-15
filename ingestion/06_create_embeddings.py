import json
from pathlib import Path

from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings


load_dotenv()

INPUT_FILE = Path("data/policies/chunks.json")
OUTPUT_FILE = Path("data/policies/embeddings.json")

EMBEDDING_MODEL = "models/gemini-embedding-001"


def load_chunks() -> list[dict]:

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Input file not found: {INPUT_FILE}"
        )

    with INPUT_FILE.open(
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


def create_embeddings(
    chunks: list[dict]
) -> list[dict]:

    embeddings_model = GoogleGenerativeAIEmbeddings(
        model=EMBEDDING_MODEL
    )

    texts = [
        chunk["page_content"]
        for chunk in chunks
    ]

    vectors = embeddings_model.embed_documents(
        texts
    )

    results = []

    for chunk, vector in zip(
        chunks,
        vectors
    ):

        results.append({
            "chunk_id": chunk["metadata"]["chunk_id"],
            "text": chunk["page_content"],
            "metadata": chunk["metadata"],
            "embedding": vector,
        })

    return results


def save_embeddings(
    embeddings: list[dict]
) -> None:

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with OUTPUT_FILE.open(
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            embeddings,
            file,
            indent=2,
            ensure_ascii=False
        )


if __name__ == "__main__":

    print("=" * 60)
    print("ZYRA LUXE - EMBEDDING CREATION")
    print("=" * 60)

    chunks = load_chunks()

    print(
        f"Chunks loaded: {len(chunks)}"
    )

    embeddings = create_embeddings(
        chunks
    )

    print(
        f"Embeddings created: "
        f"{len(embeddings)}"
    )

    if embeddings:

        print(
            f"Vector dimensions: "
            f"{len(embeddings[0]['embedding'])}"
        )

    save_embeddings(
        embeddings
    )

    print()
    print("=" * 60)
    print("EMBEDDING CREATION COMPLETED")
    print("=" * 60)

    print(
        f"Output file: {OUTPUT_FILE}"
    )