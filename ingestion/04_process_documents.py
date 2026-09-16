import json
from pathlib import Path

from langchain_core.documents import Document


# ------------------------------------------------------------
# FILE PATHS
# ------------------------------------------------------------

INPUT_FILE = Path("data/raw/pages_raw.json")
OUTPUT_FILE = Path("data/policies/documents.json")


# ------------------------------------------------------------
# LOAD RAW PAGES
# ------------------------------------------------------------

def load_pages() -> list[dict]:
    """Load scraped pages from JSON."""

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Input file not found: {INPUT_FILE}"
        )

    with INPUT_FILE.open(
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


# ------------------------------------------------------------
# CREATE DOCUMENTS
# ------------------------------------------------------------

def create_documents(
    pages: list[dict]
) -> list[Document]:

    documents = []

    for page in pages:

        content = page.get("content", "").strip()

        if not content:
            continue

        metadata = {
            "page_id": page.get("page_id"),
            "page_type": page.get("page_type"),
            "slug": page.get("slug"),
            "title": page.get("title"),
            "url": page.get("url"),
            "modified": page.get("modified"),
            "modified_gmt": page.get("modified_gmt"),
        }

        document = Document(
            page_content=content,
            metadata=metadata
        )

        documents.append(document)

    return documents

# ------------------------------------------------------------
# VALIDATE DOCUMENTS
# ------------------------------------------------------------

def validate_documents(
    documents: list[Document]
) -> list[Document]:

    valid_documents = []

    for document in documents:

        # A document must contain content and a source URL.
        if (
            document.page_content.strip()
            and document.metadata.get("url")
        ):
            valid_documents.append(document)

    return valid_documents


# ------------------------------------------------------------
# SAVE DOCUMENTS
# ------------------------------------------------------------

def save_documents(
    documents: list[Document]
) -> None:

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    # Convert Document objects into JSON-compatible dictionaries.
    data = []

    for document in documents:

        data.append({
            "page_content": document.page_content,
            "metadata": document.metadata,
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
    print("ZYRA LUXE DOCUMENT PROCESSING")
    print("=" * 60)

    # Load raw page data.
    pages = load_pages()

    print(
        f"Raw pages: {len(pages)}"
    )

    # Convert pages into LangChain Documents.
    documents = create_documents(
        pages
    )

    print(
        f"Documents created: {len(documents)}"
    )

    # Validate documents.
    documents = validate_documents(
        documents
    )

    print(
        f"Valid documents: {len(documents)}"
    )

    # Save processed documents.
    save_documents(
        documents
    )

    print()
    print("=" * 60)
    print("DOCUMENT PROCESSING COMPLETED")
    print("=" * 60)

    print(
        f"Output file: {OUTPUT_FILE}"
    )