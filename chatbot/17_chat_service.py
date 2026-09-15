from dataclasses import dataclass


@dataclass
class ChatResult:
    answer: str
    sources: list[dict]


class ChatService:

    def __init__(
        self,
        chatbot_function
    ):
        self.chatbot_function = chatbot_function

    def process_message(
        self,
        question: str,
        embeddings,
        index,
        llm
    ) -> ChatResult:

        answer, contexts = self.chatbot_function(
            question,
            embeddings,
            index,
            llm
        )

        sources = []

        for context in contexts:

            source = {
                "title": context.get("title"),
                "url": context.get("url"),
                "score": context.get("score"),
            }

            if source not in sources:
                sources.append(source)

        return ChatResult(
            answer=answer,
            sources=sources
        )


if __name__ == "__main__":

    print("=" * 60)
    print("ZYRA LUXE - CHAT SERVICE")
    print("=" * 60)

    def demo_chatbot(
        question,
        embeddings,
        index,
        llm
    ):

        return (
            "Refunds are processed within 7–10 business days.",
            [
                {
                    "title": "Return Policy",
                    "url": "https://zyraluxe.in/return-policy/",
                    "score": 0.72,
                }
            ]
        )

    service = ChatService(
        demo_chatbot
    )

    result = service.process_message(
        "How long does a refund take?",
        None,
        None,
        None
    )

    print()
    print("Answer:")
    print(result.answer)

    print()
    print("Sources:")

    for source in result.sources:

        print(
            f"- {source['title']} "
            f"({source['url']})"
        )

    print()
    print("=" * 60)
    print("CHAT SERVICE COMPLETED")
    print("=" * 60)