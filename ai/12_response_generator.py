import os

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI


load_dotenv()

MODEL_NAME = "gemini-3.5-flash"


def create_llm():
    return ChatGoogleGenerativeAI(
        model=MODEL_NAME,
        temperature=0
    )


def generate_answer(
    question: str,
    context: str,
    llm
) -> str:

    prompt = f"""
You are Zyra Luxe AI Assistant.

Answer the user's question using ONLY the provided context.

Rules:
- Do not invent information.
- Do not use outside knowledge.
- If the context does not contain enough information, say:
"I don't have enough information in the available Zyra Luxe knowledge base to answer that."
- Keep the answer concise and customer-friendly.

Context:
{context}

User question:
{question}

Answer:
"""

    response = llm.invoke(prompt)

    content = response.content

    if isinstance(content, list):
        return content[0]["text"].strip()

    return str(content).strip()


if __name__ == "__main__":

    print("=" * 60)
    print("ZYRA LUXE - RESPONSE GENERATOR")
    print("=" * 60)

    api_key = os.getenv("GOOGLE_API_KEY")

    if not api_key:
        raise ValueError(
            "GOOGLE_API_KEY not found in .env"
        )

    llm = create_llm()

    question = "How long does a refund take?"

    context = """
Refunds will be processed within 7–10 business days
after the returned product has been received and inspected.
"""

    try:

        answer = generate_answer(
            question,
            context,
            llm
        )

        print()
        print("Question:")
        print(question)

        print()
        print("Context:")
        print(context.strip())

        print()
        print("Generated Answer:")
        print(answer)

    except Exception as error:

        print()
        print("Response generation failed:")
        print(error)

    print()
    print("=" * 60)
    print("RESPONSE GENERATION COMPLETED")
    print("=" * 60)