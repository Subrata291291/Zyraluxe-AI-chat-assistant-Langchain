import os
import importlib.util
from pathlib import Path

from dotenv import load_dotenv
from pinecone import Pinecone
from langchain_google_genai import (
    GoogleGenerativeAIEmbeddings,
    ChatGoogleGenerativeAI
)
from langchain_groq import ChatGroq


load_dotenv()


PROJECT_ROOT = Path(__file__).resolve().parent.parent


ROUTER_FILE = (
    PROJECT_ROOT
    / "product"
    / "80_zyra_query_router.py"
)


def load_module(name, file_path):

    spec = importlib.util.spec_from_file_location(
        name,
        file_path
    )

    module = importlib.util.module_from_spec(spec)

    spec.loader.exec_module(module)

    return module


class PolicyRAGService:

    def __init__(self):

        router_module = load_module(
            "zyra_query_router",
            ROUTER_FILE
        )

        self.router = router_module.ZyraQueryRouter()

        self.embeddings = GoogleGenerativeAIEmbeddings(
            model="gemini-embedding-001"
        )

        self.pinecone = Pinecone(
            api_key=os.getenv("PINECONE_API_KEY")
        )

        self.index = self.pinecone.Index(
            "zyra-luxe-knowledge"
        )

        self.namespace = "knowledge"

    def retrieve(self, query, top_k=4):

        query_vector = self.embeddings.embed_query(
            query
        )

        result = self.index.query(
            namespace=self.namespace,
            vector=query_vector,
            top_k=top_k,
            include_metadata=True
        )

        documents = []

        for match in result.matches:

            metadata = match.metadata or {}

            documents.append({
                "score": match.score,
                "text": metadata.get("text", ""),
                "title": metadata.get("title", ""),
                "url": metadata.get("url", "")
            })

        return documents

    def generate_answer(self, query, documents):

        context = "\n\n".join(
            document["text"]
            for document in documents
            if document["text"]
        )

        prompt = f"""
You are the customer support assistant for Zyra Luxe.

Answer the customer's question using ONLY the
provided Zyra Luxe policy information.

If the information is not available in the context,
say that you do not have enough information.

Do not invent policy details.

Customer question:
{query}

Zyra Luxe policy information:
{context}

Give a concise and helpful answer.
"""

        try:

            llm = ChatGoogleGenerativeAI(
                model="gemini-3.5-flash",
                temperature=0
            )

            response = llm.invoke(prompt)

        except Exception as gemini_error:

            print(
                f"Gemini policy answer failed: "
                f"{type(gemini_error).__name__}"
            )

            llm = ChatGroq(
                model="openai/gpt-oss-20b",
                temperature=0
            )

            response = llm.invoke(prompt)

        if isinstance(response.content, list):

            return "".join(
                part.get("text", "")
                for part in response.content
                if isinstance(part, dict)
            ).strip()

        return str(response.content).strip()

    def answer(self, customer_query):

        route = self.router.route(
            customer_query
        )

        if route != "POLICY":

            return {
                "success": False,
                "route": route,
                "answer": "This query is not a policy query."
            }

        documents = self.retrieve(
            customer_query
        )

        if not documents:

            return {
                "success": False,
                "route": "POLICY",
                "answer": (
                    "I could not find the relevant "
                    "Zyra Luxe policy information."
                ),
                "sources": []
            }

        answer = self.generate_answer(
            customer_query,
            documents
        )

        sources = [
            {
                "title": document["title"],
                "url": document["url"],
                "score": document["score"]
            }
            for document in documents
        ]

        return {
            "success": True,
            "route": "POLICY",
            "answer": answer,
            "sources": sources
        }


if __name__ == "__main__":

    service = PolicyRAGService()

    queries = [
        "What is your return policy?",
        "Can I get a refund?",
        "What is your privacy policy?"
    ]

    print("=" * 60)
    print("ZYRA LUXE - POLICY RAG")
    print("=" * 60)

    for query in queries:

        print()
        print("-" * 60)
        print(f"Question: {query}")
        print("-" * 60)

        result = service.answer(query)

        print()
        print(f"Route: {result['route']}")
        print(f"Success: {result['success']}")
        print(f"Answer: {result['answer']}")

        print()
        print("Sources:")

        for source in result.get("sources", []):

            print(
                f"- {source['title']} "
                f"(score={source['score']:.4f})"
            )

    print()
    print("=" * 60)
    print("POLICY RAG TEST COMPLETED")
    print("=" * 60)