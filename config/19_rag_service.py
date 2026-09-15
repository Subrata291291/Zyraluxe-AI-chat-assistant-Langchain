import os

from dotenv import load_dotenv
from langchain_google_genai import (
    ChatGoogleGenerativeAI,
    GoogleGenerativeAIEmbeddings,
)
from pinecone import Pinecone


load_dotenv()


INDEX_NAME = "zyra-luxe-knowledge"
NAMESPACE = "knowledge"

EMBEDDING_MODEL = "models/gemini-embedding-001"
LLM_MODEL = "gemini-3.5-flash"

TOP_K = 5
MIN_SCORE = 0.60
MAX_CONTEXT_CHUNKS = 2


class RAGService:

    def __init__(self):

        google_api_key = os.getenv(
            "GOOGLE_API_KEY"
        )

        pinecone_api_key = os.getenv(
            "PINECONE_API_KEY"
        )

        if not google_api_key:
            raise ValueError(
                "GOOGLE_API_KEY not found in .env"
            )

        if not pinecone_api_key:
            raise ValueError(
                "PINECONE_API_KEY not found in .env"
            )

        self.embeddings = (
            GoogleGenerativeAIEmbeddings(
                model=EMBEDDING_MODEL
            )
        )

        self.llm = ChatGoogleGenerativeAI(
            model=LLM_MODEL,
            temperature=0
        )

        pc = Pinecone(
            api_key=pinecone_api_key
        )

        self.index = pc.Index(
            INDEX_NAME
        )

    def rewrite_query(
        self,
        query: str
    ) -> str:

        rewrites = {
            "refund how long?":
                "Zyra Luxe refund processing time",

            "can i send it back?":
                "Zyra Luxe return policy",

            "return?":
                "Zyra Luxe return policy",

            "refund?":
                "Zyra Luxe refund policy",

            "privacy?":
                "Zyra Luxe privacy policy",

            "do you sell my data?":
                "Does Zyra Luxe sell customer personal information?",
        }

        return rewrites.get(
            query.lower().strip(),
            query
        )

    def retrieve(
        self,
        query: str
    ) -> list[dict]:

        query_vector = (
            self.embeddings.embed_query(
                query
            )
        )

        results = self.index.query(
            vector=query_vector,
            top_k=TOP_K,
            namespace=NAMESPACE,
            include_metadata=True
        )

        matches = results.get(
            "matches",
            []
        )

        contexts = []
        seen_text = set()

        for match in matches:

            score = match.get(
                "score",
                0
            )

            if score < MIN_SCORE:
                continue

            metadata = match.get(
                "metadata",
                {}
            )

            text = metadata.get(
                "text",
                ""
            ).strip()

            if not text:
                continue

            if text in seen_text:
                continue

            seen_text.add(text)

            contexts.append({
                "text": text,
                "title": metadata.get(
                    "title"
                ),
                "url": metadata.get(
                    "url"
                ),
                "score": score
            })

            if len(contexts) >= MAX_CONTEXT_CHUNKS:
                break

        return contexts

    def generate_answer(
        self,
        question: str,
        contexts: list[dict]
    ) -> str:

        if not contexts:

            return (
                "I don't have enough information in "
                "the available Zyra Luxe knowledge base "
                "to answer that."
            )

        context_text = "\n\n".join(
            context["text"]
            for context in contexts
        )

        prompt = f"""
You are Zyra Luxe AI Assistant.

Answer the user's question using ONLY the provided context.

Rules:
- Do not invent information.
- Do not use outside knowledge.
- Keep the answer concise and customer-friendly.
- If the context does not contain enough information, say:
"I don't have enough information in the available Zyra Luxe knowledge base to answer that."

Context:
{context_text}

User question:
{question}

Answer:
"""

        response = self.llm.invoke(
            prompt
        )

        content = response.content

        if isinstance(content, list):
            return content[0]["text"].strip()

        return str(content).strip()

    def ask(
        self,
        question: str
    ) -> dict:

        rewritten_query = (
            self.rewrite_query(
                question
            )
        )

        contexts = self.retrieve(
            rewritten_query
        )

        answer = self.generate_answer(
            question,
            contexts
        )

        sources = []

        for context in contexts:

            source = {
                "title": context.get(
                    "title"
                ),
                "url": context.get(
                    "url"
                ),
                "score": context.get(
                    "score"
                )
            }

            if source not in sources:
                sources.append(source)

        return {
            "question": question,
            "rewritten_query": rewritten_query,
            "answer": answer,
            "sources": sources
        }


if __name__ == "__main__":

    print("=" * 60)
    print("ZYRA LUXE - RAG SERVICE")
    print("=" * 60)

    service = RAGService()

    print()
    print("Type 'exit' to stop.")

    while True:

        question = input(
            "\nYou: "
        ).strip()

        if question.lower() == "exit":
            break

        if not question:
            continue

        try:

            result = service.ask(
                question
            )

            print()
            print("Search Query:")
            print(
                result["rewritten_query"]
            )

            print()
            print("Bot:")
            print(
                result["answer"]
            )

            print()
            print("Sources")

            for source in result["sources"]:

                print(
                    f"- {source['title']}"
                )

                print(
                    f"  {source['url']}"
                )

                print(
                    f"  Score: "
                    f"{source['score']:.4f}"
                )

        except Exception as error:

            print()
            print("RAG Service Error:")
            print(error)

    print()
    print("RAG service stopped.")