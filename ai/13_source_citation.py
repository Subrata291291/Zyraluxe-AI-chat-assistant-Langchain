import json
from pathlib import Path


INPUT_FILE = Path("data/policies/chunks.json")


def load_chunks() -> list[dict]:
    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Input file not found: {INPUT_FILE}"
        )

    with INPUT_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


def create_source_info(chunk: dict) -> dict:

    metadata = chunk.get("metadata", {})

    return {
        "title": metadata.get("title"),
        "page_type": metadata.get("page_type"),
        "url": metadata.get("url"),
        "chunk_index": metadata.get("chunk_index"),
    }


def display_source(source: dict) -> None:

    print()
    print("Source")
    print("-" * 60)
    print(f"Title: {source['title']}")
    print(f"Page Type: {source['page_type']}")
    print(f"URL: {source['url']}")
    print(f"Chunk Index: {source['chunk_index']}")


if __name__ == "__main__":

    print("=" * 60)
    print("ZYRA LUXE - SOURCE CITATION")
    print("=" * 60)

    chunks = load_chunks()

    print(f"Total chunks: {len(chunks)}")

    if not chunks:
        raise ValueError("No chunks found.")

    source = create_source_info(chunks[0])

    display_source(source)

    print()
    print("=" * 60)
    print("SOURCE CITATION COMPLETED")
    print("=" * 60)