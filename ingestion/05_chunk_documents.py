import json
from pathlib import Path

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter


# ------------------------------------------------------------
# FILE PATHS
# ------------------------------------------------------------

INPUT_FILE = Path("data/policies/documents.json")
OUTPUT_FILE = Path("data/policies/chunks.json")


# ------------------------------------------------------------
# CHUNK CONFIGURATION
# ------------------------------------------------------------

CHUNK_SIZE = 800
CHUNK_OVERLAP = 120


# ------------------------------------------------------------
# LOAD DOCUMENTS
# ------------------------------------------------------------

def load_documents() -> list[Document]:
    """Load processed documents from JSON."""

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Input file not found: {INPUT_FILE}"
        )

    with INPUT_FILE.open(
        "r",
        encoding="utf-8"
    ) as file:

        data = json.load(file)

    documents = []

    for item in data:

        document = Document(
            page_content=item["page_content"],
            metadata=item["metadata"]
        )

        documents.append(document)

    return documents


# ------------------------------------------------------------
# SPLIT DOCUMENTS
# ------------------------------------------------------------

def split_documents(
    documents: list[Document]
) -> list[Document]:

    # Create the recursive text splitter.
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=[
            "\n\n",
            "\n",
            ". ",
            " ",
            ""
        ]
    )

    # Split all documents into smaller chunks.
    chunks = splitter.split_documents(
        documents
    )

    # Add chunk metadata.
    for index, chunk in enumerate(chunks):

        chunk.metadata["chunk_index"] = index
        chunk.metadata["chunk_id"] = f"policy-{index}"

    return chunks


# ------------------------------------------------------------
# SAVE CHUNKS
# ------------------------------------------------------------

def save_chunks(
    chunks: list[Document]
) -> None:

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    data = []

    for chunk in chunks:

        data.append({
            "page_content": chunk.page_content,
            "metadata": chunk.metadata
        })

    with OUTPUT_FILE.open(
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            data,
            file,
            indent=4,
            ensure_ascii=False
        )


# ------------------------------------------------------------
# MAIN
# ------------------------------------------------------------

if __name__ == "__main__":

    print("=" * 60)
    print("ZYRA LUXE DOCUMENT CHUNKING")
    print("=" * 60)

    # Load documents.
    documents = load_documents()

    print(
        f"Documents loaded: {len(documents)}"
    )

    # Split documents.
    chunks = split_documents(
        documents
    )

    print(
        f"Chunks created: {len(chunks)}"
    )

    # Display chunk information.
    print()
    print("-" * 60)

    for chunk in chunks:

        print(
            f"Chunk ID: "
            f"{chunk.metadata['chunk_id']}"
        )

        print(
            f"Characters: "
            f"{len(chunk.page_content)}"
        )

        print(
            f"Preview: "
            f"{chunk.page_content[:120]}..."
        )

        print("-" * 60)

    # Save chunks.
    save_chunks(
        chunks
    )

    print()
    print("=" * 60)
    print("CHUNKING COMPLETED")
    print("=" * 60)

    print(
        f"Output file: {OUTPUT_FILE}"
    )