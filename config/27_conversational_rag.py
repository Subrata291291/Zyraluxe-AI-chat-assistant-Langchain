import importlib.util
from pathlib import Path


BASE_DIR = Path(__file__).parent

CONFIG_FILE = BASE_DIR / "18_config.py"
FACTORY_FILE = BASE_DIR / "22_rag_service_factory.py"
SESSION_FILE = (
    BASE_DIR.parent
    / "chatbot"
    / "15_session_manager.py"
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
    question: str,
    components: dict,
    config
) -> list[dict]:

    embeddings = components["embeddings"]
    index = components["index"]

    query_vector = embeddings.embed_query(
        question
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


def format_history(
    history: list[dict]
) -> str:

    if not history:
        return "No previous conversation."

    lines = []

    for message in history:

        role = message.get(
            "role",
            "user"
        ).upper()

        content = message.get(
            "content",
            ""
        )

        lines.append(
            f"{role}: {content}"
        )

    return "\n".join(lines)


def generate_answer(
    question: str,
    history: list[dict],
    contexts: list[dict],
    llm
) -> str:

    if not contexts:

        return (
            "I don't have enough information in "
            "the available Zyra Luxe knowledge base "
            "to answer that."
        )

    history_text = format_history(
        history
    )

    context_text = "\n\n".join(
        context["text"]
        for context in contexts
    )

    prompt = f"""
You are Zyra Luxe AI Assistant.

Answer the user's current question using the
provided Zyra Luxe knowledge context and the
conversation history.

Rules:
- Use the conversation history to understand follow-up questions.
- Use the knowledge context for factual answers.
- Do not invent information.
- Do not use outside knowledge.
- Keep the answer concise and customer-friendly.
- If the knowledge context does not contain enough information, say:
"I don't have enough information in the available Zyra Luxe knowledge base to answer that."

Conversation History:
{history_text}

Knowledge Context:
{context_text}

Current User Question:
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


def create_sources(
    contexts: list[dict]
) -> list[dict]:

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

    return sources


def conversational_rag(
    session_id: str,
    question: str,
    session_manager,
    components: dict,
    config
) -> dict:

    history = session_manager.get_history(
        session_id
    )

    contexts = retrieve_context(
        question,
        components,
        config
    )

    answer = generate_answer(
        question,
        history,
        contexts,
        components["llm"]
    )

    session_manager.add_message(
        session_id,
        "user",
        question
    )

    session_manager.add_message(
        session_id,
        "assistant",
        answer
    )

    return {
        "session_id": session_id,
        "answer": answer,
        "sources": create_sources(contexts),
        "history": session_manager.get_history(
            session_id
        )
    }


if __name__ == "__main__":

    print("=" * 60)
    print("ZYRA LUXE - CONVERSATIONAL RAG")
    print("=" * 60)

    config = load_module(
        "zyra_config",
        CONFIG_FILE
    )

    factory = load_module(
        "zyra_factory",
        FACTORY_FILE
    )

    session_module = load_module(
        "zyra_session",
        SESSION_FILE
    )

    components = factory.create_components(
        config
    )

    session_manager = (
        session_module.SessionManager()
    )

    session_id = "user-001"

    print()
    print(f"Session ID: {session_id}")
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

            result = conversational_rag(
                session_id,
                question,
                session_manager,
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

        except Exception as error:

            print()
            print("Conversational RAG Error:")
            print(error)

    print()
    print("Conversational RAG stopped.")