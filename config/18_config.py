import os

from dotenv import load_dotenv


load_dotenv()


def get_required_env(name: str) -> str:

    value = os.getenv(name)

    if not value:
        raise ValueError(
            f"{name} not found in .env"
        )

    return value


GOOGLE_API_KEY = get_required_env(
    "GOOGLE_API_KEY"
)

PINECONE_API_KEY = get_required_env(
    "PINECONE_API_KEY"
)


LLM_MODEL = "gemini-3.5-flash"

EMBEDDING_MODEL = "models/gemini-embedding-001"


PINECONE_INDEX_NAME = "zyra-luxe-knowledge"

PINECONE_NAMESPACE = "knowledge"

PINECONE_CLOUD = "aws"

PINECONE_REGION = "us-east-1"


RETRIEVAL_TOP_K = 5

MIN_RETRIEVAL_SCORE = 0.60

MAX_CONTEXT_CHUNKS = 2


API_HOST = "127.0.0.1"
API_PORT = 8000

MAX_LLM_RETRIES = 0
RETRY_BASE_DELAY = 2


if __name__ == "__main__":

    print("=" * 60)
    print("ZYRA LUXE - CONFIGURATION")
    print("=" * 60)

    print()
    print("Configuration loaded successfully.")

    print()
    print(f"LLM Model: {LLM_MODEL}")
    print(f"Embedding Model: {EMBEDDING_MODEL}")
    print(f"Pinecone Index: {PINECONE_INDEX_NAME}")
    print(f"Namespace: {PINECONE_NAMESPACE}")
    print(f"Retrieval Top K: {RETRIEVAL_TOP_K}")
    print(f"Minimum Score: {MIN_RETRIEVAL_SCORE}")
    print(f"Maximum Context Chunks: {MAX_CONTEXT_CHUNKS}")
    print(f"API Host: {API_HOST}")
    print(f"API Port: {API_PORT}")

    print()
    print("=" * 60)
    print("CONFIGURATION CHECK COMPLETED")
    print("=" * 60)