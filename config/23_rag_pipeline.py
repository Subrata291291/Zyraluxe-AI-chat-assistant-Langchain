from pathlib import Path
import importlib.util


CONFIG_FILE = (
    Path(__file__).parent / "18_config.py"
)

FACTORY_FILE = (
    Path(__file__).parent / "22_rag_service_factory.py"
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


def retrieve_context(
    query: str,
    components: dict,
    config
) -> list[dict]:

    embeddings = components["embeddings"]
    index = components["index"]

    query_vector = embeddings.embed_query(
        query
    )

    results = index.query(
        vector=query_vector,
        top_k=config.RETRIEVAL_TOP_K,
        namespace=config.PINECONE_NAMESPACE,
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

        if score < config.MIN_RETRIEVAL_SCORE:
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
            config.MAX_CONTEXT_CHUNKS
        ):
            break

    return contexts


def generate_answer(
    question: str,
    contexts: list[dict],
    components: dict
) -> str:

    if not contexts:

        return (
            "I don't have enough information in "
            "the available Zyra Luxe knowledge base "
            "to answer that."
        )

    llm = components["llm"]

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

    response = llm.invoke(
        prompt
    )

    content = response.content

    if isinstance(content, list):
        return content[0]["text"].strip()

    return str(content).strip()


def run_pipeline(
    question: str,
    components: dict,
    config
) -> dict:

    contexts = retrieve_context(
        question,
        components,
        config
    )

    answer = generate_answer(
        question,
        contexts,
        components
    )

    sources = []

    for context in contexts:

        url = context.get("url")

        if not url:
            continue

        if any(
            source["url"] == url
            for source in sources
        ):
            continue

        sources.append({
            "title": context.get("title"),
            "url": url,
            "score": context.get("score")
        })

    return {
        "question": question,
        "answer": answer,
        "sources": sources
    }


if __name__ == "__main__":

    print("=" * 60)
    print("ZYRA LUXE - RAG PIPELINE")
    print("=" * 60)

    config = load_module(
        "zyra_config",
        CONFIG_FILE
    )

    factory = load_module(
        "zyra_factory",
        FACTORY_FILE
    )

    components = factory.create_components(
        config
    )

    print()
    print("RAG pipeline initialized.")

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

            result = run_pipeline(
                question,
                components,
                config
            )

            print()
            print("Bot:")
            print(result["answer"])

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
            print("Pipeline Error:")
            print(error)

    print()
    print("RAG pipeline stopped.")