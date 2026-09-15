import json
from pathlib import Path

from dotenv import load_dotenv
from pinecone import Pinecone
import os


PROJECT_ROOT = Path(__file__).resolve().parent.parent

INPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "products"
    / "product_embeddings.json"
)

INDEX_NAME = "zyra-luxe-knowledge"
NAMESPACE = "products"

load_dotenv()


class ProductEmbeddingUploader:

    def __init__(self):
        api_key = os.getenv("PINECONE_API_KEY")

        if not api_key:
            raise ValueError("PINECONE_API_KEY not found")

        self.pc = Pinecone(api_key=api_key)
        self.records = self.load_records()

    def load_records(self):
        with open(INPUT_FILE, "r", encoding="utf-8") as file:
            return json.load(file)

    def check_index(self):

        indexes = self.pc.list_indexes()

        index_names = [index["name"] for index in indexes]

        if INDEX_NAME not in index_names:
            raise ValueError(
                f"Pinecone index '{INDEX_NAME}' not found"
            )

        index_info = self.pc.describe_index(INDEX_NAME)
        index_dimension = index_info.dimension
        embedding_dimension = len(
            self.records[0]["embedding"]
        )

        print(f"Index Dimension: {index_dimension}")
        print(f"Embedding Dimension: {embedding_dimension}")

        if index_dimension != embedding_dimension:
            raise ValueError(
                "Dimension mismatch between Pinecone index "
                "and product embeddings"
            )

        print("Dimension check: OK")

    def upload(self):

        index = self.pc.Index(INDEX_NAME)

        vectors = []

        for record in self.records:
            vectors.append({
                "id": record["id"],
                "values": record["embedding"],
                "metadata": {
                    "name": record["metadata"]["name"],
                    "url": record["metadata"]["url"],
                    "categories": record["metadata"].get(
                        "categories", []
                    ),
                    "tags": record["metadata"].get(
                        "tags", []
                    ),
                    "text": record["text"]
                }
            })

        index.upsert(
            vectors=vectors,
            namespace=NAMESPACE
        )

        return len(vectors)


if __name__ == "__main__":

    print("=" * 60)
    print("ZYRA LUXE - PRODUCT PINECONE UPLOAD")
    print("=" * 60)

    uploader = ProductEmbeddingUploader()

    print()
    print(f"Products Loaded: {len(uploader.records)}")

    print()
    print("Checking Pinecone index...")
    uploader.check_index()

    print()
    print("Uploading product vectors...")

    count = uploader.upload()

    print()
    print(f"Vectors Uploaded: {count}")
    print(f"Index: {INDEX_NAME}")
    print(f"Namespace: {NAMESPACE}")

    print()
    print("=" * 60)
    print("PRODUCT PINECONE UPLOAD COMPLETED")
    print("=" * 60)