import os
from pathlib import Path

from dotenv import load_dotenv
from pinecone import Pinecone
from langchain_google_genai import GoogleGenerativeAIEmbeddings


PROJECT_ROOT = Path(__file__).resolve().parent.parent

INDEX_NAME = "zyra-luxe-knowledge"
NAMESPACE = "products"

load_dotenv()


class SemanticProductSearch:

    def __init__(self, top_k=5):
        api_key = os.getenv("PINECONE_API_KEY")

        if not api_key:
            raise ValueError("PINECONE_API_KEY not found")

        self.top_k = top_k

        self.pc = Pinecone(api_key=api_key)
        self.index = self.pc.Index(INDEX_NAME)

        self.embeddings = GoogleGenerativeAIEmbeddings(
            model="gemini-embedding-001"
        )

    def search(self, query):
        query_vector = self.embeddings.embed_query(query)

        results = self.index.query(
            namespace=NAMESPACE,
            vector=query_vector,
            top_k=self.top_k,
            include_metadata=True
        )

        return results.matches


if __name__ == "__main__":

    print("=" * 60)
    print("ZYRA LUXE - SEMANTIC PRODUCT SEARCH")
    print("=" * 60)

    searcher = SemanticProductSearch(top_k=5)

    queries = [
        "I want beautiful oxidized earrings",
        "Show me something for a wedding",
        "I want stylish jewellery for women"
    ]

    for query in queries:

        print()
        print("-" * 60)
        print(f"Query: {query}")
        print("-" * 60)

        matches = searcher.search(query)

        for rank, match in enumerate(matches, start=1):

            metadata = match.metadata

            print()
            print(f"Rank: {rank}")
            print(f"Score: {match.score:.4f}")
            print(f"Name: {metadata.get('name')}")
            print(f"URL: {metadata.get('url')}")

    print()
    print("=" * 60)
    print("SEMANTIC PRODUCT SEARCH COMPLETED")
    print("=" * 60)