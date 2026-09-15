import json
from pathlib import Path

from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings


PROJECT_ROOT = Path(__file__).resolve().parent.parent

INPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "products"
    / "product_embedding_records.json"
)

OUTPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "products"
    / "product_embeddings.json"
)

load_dotenv()


class ProductEmbeddingCreator:

    def __init__(self):
        self.records = self.load_records()

        self.embeddings = GoogleGenerativeAIEmbeddings(
            model="gemini-embedding-001"
        )

    def load_records(self):
        with open(INPUT_FILE, "r", encoding="utf-8") as file:
            return json.load(file)

    def create_embeddings(self):
        texts = [record["text"] for record in self.records]

        vectors = self.embeddings.embed_documents(texts)

        embedding_records = []

        for record, vector in zip(self.records, vectors):
            embedding_records.append({
                "id": record["id"],
                "text": record["text"],
                "metadata": record["metadata"],
                "embedding": vector
            })

        return embedding_records

    def save(self, records):
        with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
            json.dump(
                records,
                file,
                ensure_ascii=False,
                indent=2
            )


if __name__ == "__main__":

    print("=" * 60)
    print("ZYRA LUXE - PRODUCT EMBEDDING CREATION")
    print("=" * 60)

    creator = ProductEmbeddingCreator()

    print()
    print(f"Products Loaded: {len(creator.records)}")
    print()
    print("Creating embeddings...")

    records = creator.create_embeddings()

    creator.save(records)

    print()
    print(f"Embeddings Created: {len(records)}")

    if records:
        print(f"Vector Dimension: {len(records[0]['embedding'])}")

    print()
    print("-" * 60)
    print(f"Output: {OUTPUT_FILE}")
    print("-" * 60)

    print()
    print("=" * 60)
    print("PRODUCT EMBEDDING CREATION COMPLETED")
    print("=" * 60)