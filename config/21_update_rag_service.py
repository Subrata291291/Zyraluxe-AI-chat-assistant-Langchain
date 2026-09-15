import importlib.util
from pathlib import Path

from langchain_google_genai import (
    ChatGoogleGenerativeAI,
    GoogleGenerativeAIEmbeddings,
)
from pinecone import Pinecone


CONFIG_FILE = (
    Path(__file__).parent / "18_config.py"
)


def load_config():

    spec = importlib.util.spec_from_file_location(
        "zyra_config",
        CONFIG_FILE
    )

    if spec is None or spec.loader is None:
        raise ImportError(
            "Could not load configuration."
        )

    config = importlib.util.module_from_spec(
        spec
    )

    spec.loader.exec_module(config)

    return config


class ConfiguredRAGService:

    def __init__(self, config):

        self.config = config

        self.embeddings = (
            GoogleGenerativeAIEmbeddings(
                model=config.EMBEDDING_MODEL
            )
        )

        self.llm = ChatGoogleGenerativeAI(
            model=config.LLM_MODEL,
            temperature=0
        )

        pc = Pinecone(
            api_key=config.PINECONE_API_KEY
        )

        self.index = pc.Index(
            config.PINECONE_INDEX_NAME
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
            top_k=self.config.RETRIEVAL_TOP_K,
            namespace=self.config.PINECONE_NAMESPACE,
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

            if score < self.config.MIN_RETRIEVAL_SCORE:
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
                "title": metadata.get("title"),
                "url": metadata.get("url"),
                "score": score
            })

            if len(contexts) >= (
                self.config.MAX_CONTEXT_CHUNKS
            ):
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

        contexts = self.retrieve(
            question
        )

        answer = self.generate_answer(
            question,
            contexts
        )

        sources = []

        for context in contexts:

            source = {
                "title": context.get("title"),
                "url": context.get("url"),
                "score": context.get("score")
            }

            if source not in sources:
                sources.append(source)

        return {
            "question": question,
            "answer": answer,
            "sources": sources
        }


if __name__ == "__main__":

    print("=" * 60)
    print("ZYRA LUXE - CONFIGURED RAG SERVICE")
    print("=" * 60)

    config = load_config()

    print()
    print("Configuration loaded from 18_config.py")

    print(
        f"Model: {config.LLM_MODEL}"
    )

    print(
        f"Embedding: {config.EMBEDDING_MODEL}"
    )

    print(
        f"Index: {config.PINECONE_INDEX_NAME}"
    )

    print(
        f"Top K: {config.RETRIEVAL_TOP_K}"
    )

    print(
        f"Minimum Score: "
        f"{config.MIN_RETRIEVAL_SCORE}"
    )

    service = ConfiguredRAGService(
        config
    )

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
            print("Bot:")
            print(result["answer"])

            print()
            print("Sources")

            displayed_urls = set()

            for source in result["sources"]:

                url = source.get("url")

                if not url:
                    continue

                if url in displayed_urls:
                    continue

                displayed_urls.add(url)

                print(
                    f"- {source['title']}"
                )

                print(
                    f"  {url}"
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
    print("Configured RAG service stopped.")