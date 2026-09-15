import os
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent

sys.path.append(str(PROJECT_ROOT / "config"))

from dotenv import load_dotenv

load_dotenv(PROJECT_ROOT / ".env")


def check_gemini():

    try:

        from langchain_google_genai import ChatGoogleGenerativeAI

        llm = ChatGoogleGenerativeAI(
            model="gemini-3.5-flash",
            google_api_key=os.getenv("GOOGLE_API_KEY")
        )

        response = llm.invoke("Reply with OK.")

        return True, "API available"

    except Exception as error:

        return False, str(error)


def check_groq():

    try:

        from langchain_groq import ChatGroq

        llm = ChatGroq(
            model="openai/gpt-oss-20b",
            groq_api_key=os.getenv("GROQ_API_KEY")
        )

        response = llm.invoke("Reply with OK.")

        return True, "API available"

    except Exception as error:

        return False, str(error)


def check_openrouter():

    try:

        from langchain_openrouter import ChatOpenRouter

        llm = ChatOpenRouter(
            model="openai/gpt-oss-20b",
            api_key=os.getenv("OPENROUTER_API_KEY")
        )

        response = llm.invoke("Reply with OK.")

        return True, "API available"

    except Exception as error:

        return False, str(error)


def check_openai():

    try:

        from langchain_openai import ChatOpenAI

        llm = ChatOpenAI(
            model="gpt-5-nano",
            api_key=os.getenv("OPENAI_API_KEY")
        )

        response = llm.invoke("Reply with OK.")

        return True, "API available"

    except Exception as error:

        return False, str(error)


def check_pinecone():

    try:

        from pinecone import Pinecone

        api_key = os.getenv("PINECONE_API_KEY")

        pc = Pinecone(api_key=api_key)

        indexes = pc.list_indexes()

        return True, "Pinecone API available"

    except Exception as error:

        return False, str(error)


def run_health_checks():

    checks = {
        "gemini": check_gemini,
        "groq": check_groq,
        "openrouter": check_openrouter,
        "openai": check_openai,
        "pinecone": check_pinecone
    }

    results = {}

    for service, check in checks.items():

        healthy, message = check()

        results[service] = {
            "status": (
                "healthy"
                if healthy
                else "unhealthy"
            ),
            "message": message
        }

    return results


if __name__ == "__main__":

    print("=" * 60)
    print("ZYRA LUXE - REAL PROVIDER HEALTH CHECK")
    print("=" * 60)

    results = run_health_checks()

    print()

    for service, result in results.items():

        print(
            f"{service}: "
            f"{result['status']} - "
            f"{result['message']}"
        )

    print()
    print("=" * 60)
    print("REAL HEALTH CHECK COMPLETED")
    print("=" * 60)