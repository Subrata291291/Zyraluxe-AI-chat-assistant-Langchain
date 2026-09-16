import hashlib
import importlib.util
import json
import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pinecone import Pinecone


load_dotenv()


BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent

EMBEDDING_MODEL = "models/gemini-embedding-001"

INDEX_NAME = "zyra-luxe-knowledge"
NAMESPACE = "knowledge"

EMBEDDINGS_FILE = (
    PROJECT_ROOT
    / "data"
    / "policies"
    / "embeddings.json"
)

SYNC_STATE_FILE = (
    PROJECT_ROOT
    / "data"
    / "policies"
    / "sync_state.json"
)

SCRAPER_FILE = (
    BASE_DIR
    / "02_scrape_pages.py"
)


def load_module(
    name: str,
    file_path: Path
):
    spec = importlib.util.spec_from_file_location(
        name,
        file_path
    )

    if spec is None or spec.loader is None:
        raise ImportError(
            f"Could not load module: {file_path}"
        )

    module = importlib.util.module_from_spec(
        spec
    )

    spec.loader.exec_module(module)

    return module


scraper = load_module(
    "scrape_pages",
    SCRAPER_FILE
)


def create_content_hash(
    content: str
) -> str:

    normalized_content = " ".join(
        content.split()
    )

    return hashlib.sha256(
        normalized_content.encode("utf-8")
    ).hexdigest()


def load_existing_embeddings() -> list[dict]:

    if not EMBEDDINGS_FILE.exists():
        return []

    with EMBEDDINGS_FILE.open(
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


def load_sync_state() -> dict:

    if not SYNC_STATE_FILE.exists():
        return {}

    with SYNC_STATE_FILE.open(
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


def save_sync_state(
    state: dict
) -> None:

    SYNC_STATE_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with SYNC_STATE_FILE.open(
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            state,
            file,
            indent=4,
            ensure_ascii=False
        )


def initialize_sync_state(
    embeddings: list[dict]
) -> dict:

    state = {}

    for item in embeddings:

        metadata = item.get(
            "metadata",
            {}
        )

        page_id = metadata.get(
            "page_id"
        )

        modified = metadata.get(
            "modified"
        )

        if page_id is not None and modified:

            state[str(page_id)] = {
                "page_id": page_id,
                "slug": metadata.get(
                    "slug"
                ),
                "title": metadata.get(
                    "title"
                ),
                "url": metadata.get(
                    "url"
                ),
                "modified": modified,
                "modified_gmt": metadata.get(
                    "modified_gmt"
                ),
                "content_hash": None
            }

    return state


def create_chunks(
    page: dict
) -> list[Document]:

    document = Document(
        page_content=page["content"],
        metadata={
            "page_id": page.get(
                "page_id"
            ),
            "page_type": page.get(
                "page_type"
            ),
            "slug": page.get(
                "slug"
            ),
            "title": page.get(
                "title"
            ),
            "url": page.get(
                "url"
            ),
            "modified": page.get(
                "modified"
            ),
            "modified_gmt": page.get(
                "modified_gmt"
            )
        }
    )

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=120,
        separators=[
            "\n\n",
            "\n",
            ". ",
            " ",
            ""
        ]
    )

    chunks = splitter.split_documents(
        [document]
    )

    page_id = page.get(
        "page_id"
    )

    for index, chunk in enumerate(chunks):

        chunk.metadata["chunk_index"] = index

        chunk.metadata["chunk_id"] = (
            f"page-{page_id}-chunk-{index}"
        )

    return chunks


def create_embeddings(
    chunks: list[Document]
) -> list[dict]:

    embeddings_model = (
        GoogleGenerativeAIEmbeddings(
            model=EMBEDDING_MODEL
        )
    )

    texts = [
        chunk.page_content
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
            "chunk_id": chunk.metadata[
                "chunk_id"
            ],
            "text": chunk.page_content,
            "metadata": chunk.metadata,
            "embedding": vector
        })

    return results


def delete_page_vectors(
    index,
    page_id: int
) -> None:

    print(
        f"Deleting old Pinecone vectors "
        f"for page_id={page_id}"
    )

    index.delete(
        filter={
            "page_id": {
                "$eq": page_id
            }
        },
        namespace=NAMESPACE
    )

    print(
        "Old page vectors deleted."
    )


def upload_page_vectors(
    index,
    embeddings: list[dict]
) -> None:

    vectors = []

    for item in embeddings:

        metadata = item["metadata"]

        vectors.append({
            "id": item["chunk_id"],
            "values": item["embedding"],
            "metadata": {
                "text": item["text"],
                "page_id": metadata[
                    "page_id"
                ],
                "page_type": metadata[
                    "page_type"
                ],
                "slug": metadata[
                    "slug"
                ],
                "title": metadata[
                    "title"
                ],
                "url": metadata[
                    "url"
                ],
                "modified": metadata[
                    "modified"
                ],
                "modified_gmt": metadata[
                    "modified_gmt"
                ],
                "chunk_index": metadata[
                    "chunk_index"
                ],
                "chunk_id": metadata[
                    "chunk_id"
                ]
            }
        })

    index.upsert(
        vectors=vectors,
        namespace=NAMESPACE
    )

    print(
        f"New vectors uploaded: "
        f"{len(vectors)}"
    )


def sync_page(
    index,
    page: dict
) -> dict:

    page_id = page[
        "page_id"
    ]

    print()
    print("=" * 60)
    print(
        f"SYNCING PAGE: "
        f"{page['title']}"
    )
    print(
        f"Page ID: {page_id}"
    )
    print(
        f"Modified: "
        f"{page['modified']}"
    )
    print("=" * 60)

    chunks = create_chunks(
        page
    )

    print(
        f"Chunks created: "
        f"{len(chunks)}"
    )

    embeddings = create_embeddings(
        chunks
    )

    print(
        f"Embeddings created: "
        f"{len(embeddings)}"
    )

    delete_page_vectors(
        index,
        page_id
    )

    upload_page_vectors(
        index,
        embeddings
    )

    return {
        "page_id": page_id,
        "slug": page.get(
            "slug"
        ),
        "title": page.get(
            "title"
        ),
        "url": page.get(
            "url"
        ),
        "modified": page.get(
            "modified"
        ),
        "modified_gmt": page.get(
            "modified_gmt"
        ),
        "content_hash": create_content_hash(
            page.get(
                "content",
                ""
            )
        )
    }


def run_sync(
    client
) -> None:

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

    embeddings = load_existing_embeddings()

    state = load_sync_state()

    if not state:

        state = initialize_sync_state(
            embeddings
        )

        save_sync_state(
            state
        )

        print(
            "Initial sync state created."
        )

    print()
    print("=" * 60)
    print("ZYRA LUXE KNOWLEDGE SYNC")
    print("=" * 60)

    changed_pages = []
    unchanged_pages = []

    for page_type, slug in (
        scraper.KNOWLEDGE_PAGES.items()
    ):

        page = scraper.fetch_page(
            client,
            page_type,
            slug
        )

        if not page:
            continue

        page_id = page[
            "page_id"
        ]

        previous = state.get(
            str(page_id)
        )

        current_modified = page.get(
            "modified"
        )

        previous_modified = (
            previous.get("modified")
            if previous
            else None
        )

        current_hash = create_content_hash(
            page.get(
                "content",
                ""
            )
        )

        previous_hash = (
            previous.get(
                "content_hash"
            )
            if previous
            else None
        )

        is_unchanged = (
            previous is not None
            and previous_modified
            == current_modified
            and previous_hash is not None
            and previous_hash
            == current_hash
        )

        if is_unchanged:

            print()
            print(
                f"UNCHANGED: "
                f"{page['title']}"
            )

            unchanged_pages.append(
                page
            )

            continue

        print()
        print(
            f"CHANGED: "
            f"{page['title']}"
        )

        changed_pages.append(
            page
        )

    for page in changed_pages:

        synced_page = sync_page(
            index,
            page
        )

        state[
            str(
                synced_page["page_id"]
            )
        ] = synced_page

        save_sync_state(
            state
        )

    print()
    print("=" * 60)
    print("KNOWLEDGE SYNC COMPLETED")
    print("=" * 60)

    print(
        f"Changed pages: "
        f"{len(changed_pages)}"
    )

    print(
        f"Unchanged pages: "
        f"{len(unchanged_pages)}"
    )


if __name__ == "__main__":

    with scraper.httpx.Client(
        headers=scraper.HEADERS,
        timeout=20.0,
        follow_redirects=True
    ) as client:

        run_sync(client)