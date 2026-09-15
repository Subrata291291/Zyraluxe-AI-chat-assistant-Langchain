import importlib.util
from pathlib import Path


CONFIG_FILE = Path(__file__).parent / "18_config.py"
FACTORY_FILE = Path(__file__).parent / "22_rag_service_factory.py"
LLM_MANAGER_FILE = Path(__file__).parent / "32_llm_provider_manager.py"


def load_module(name, file_path):

    spec = importlib.util.spec_from_file_location(
        name,
        file_path
    )

    if spec is None or spec.loader is None:
        raise ImportError(
            f"Could not load {file_path}"
        )

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    return module


def retrieve_context(
    query,
    components,
    config
):

    query_vector = components[
        "embeddings"
    ].embed_query(query)

    results = components[
        "index"
    ].query(
        namespace=config.PINECONE_NAMESPACE,
        vector=query_vector,
        top_k=config.RETRIEVAL_TOP_K,
        include_metadata=True
    )

    contexts = []

    for match in results["matches"]:

        score = match["score"]

        if score < config.MIN_RETRIEVAL_SCORE:
            continue

        metadata = match.get(
            "metadata",
            {}
        )

        text = metadata.get(
            "text",
            ""
        )

        if text:
            contexts.append({
                "text": text,
                "score": score,
                "title": metadata.get(
                    "title",
                    ""
                ),
                "url": metadata.get(
                    "url",
                    ""
                )
            })

    unique_contexts = []
    seen_text = set()

    for context in contexts:

        if context["text"] in seen_text:
            continue

        seen_text.add(
            context["text"]
        )

        unique_contexts.append(
            context
        )

        if len(unique_contexts) >= config.MAX_CONTEXT_CHUNKS:
            break

    return unique_contexts


def build_prompt(
    question,
    contexts
):

    context_text = "\n\n".join(
        context["text"]
        for context in contexts
    )

    return f"""
You are the Zyra Luxe customer support assistant.

Answer the customer's question using only
the provided context.

If the context does not contain the answer,
say that you do not have enough information.

Do not invent policies or facts.

Context:
{context_text}

Customer Question:
{question}

Answer:
"""


def create_sources(contexts):

    sources = []
    seen_urls = set()

    for context in contexts:

        url = context["url"]

        if not url:
            continue

        if url in seen_urls:
            continue

        seen_urls.add(url)

        sources.append({
            "title": context["title"],
            "url": url
        })

    return sources


def run_rag(
    question,
    components,
    config,
    llm_manager
):

    contexts = retrieve_context(
        question,
        components,
        config
    )

    if not contexts:

        return {
            "success": False,
            "answer": (
                "I don't have enough information "
                "to answer that question."
            ),
            "provider": None,
            "sources": []
        }

    prompt = build_prompt(
        question,
        contexts
    )

    result = llm_manager.generate(
        prompt
    )

    if not result["success"]:

        return {
            "success": False,
            "answer": (
                "Sorry, I am temporarily unable "
                "to process your request."
            ),
            "provider": None,
            "sources": create_sources(contexts)
        }

    return {
        "success": True,
        "answer": result["answer"],
        "provider": result["provider"],
        "sources": create_sources(contexts)
    }


if __name__ == "__main__":

    print("=" * 60)
    print("ZYRA LUXE - RAG + LLM INTEGRATION")
    print("=" * 60)

    config = load_module(
        "zyra_config",
        CONFIG_FILE
    )

    factory = load_module(
        "rag_factory",
        FACTORY_FILE
    )

    llm_module = load_module(
        "llm_manager",
        LLM_MANAGER_FILE
    )

    components = factory.create_components(
        config
    )

    llm_manager = llm_module.LLMProviderManager(
        config
    )

    question = "How long does a refund take?"

    result = run_rag(
        question,
        components,
        config,
        llm_manager
    )

    print()
    print("=" * 60)
    print("RESULT")
    print("=" * 60)

    print(f"Success: {result['success']}")
    print(f"Provider: {result['provider']}")
    print(f"Answer: {result['answer']}")

    print()
    print("Sources:")

    for source in result["sources"]:
        print(
            f"- {source['title']}: "
            f"{source['url']}"
        )

    print()
    print("=" * 60)
    print("RAG + LLM INTEGRATION COMPLETED")
    print("=" * 60)