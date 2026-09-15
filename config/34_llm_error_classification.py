def classify_error(error: Exception) -> str:

    error_text = str(error).lower()

    if "429" in error_text:
        return "rate_limit"

    if "503" in error_text:
        return "service_unavailable"

    if "timeout" in error_text:
        return "timeout"

    if "401" in error_text or "403" in error_text:
        return "authentication"

    if "404" in error_text:
        return "model_not_found"

    if "connection" in error_text:
        return "connection"

    return "unknown"


def should_fallback(error_type: str) -> bool:

    fallback_errors = {
        "rate_limit",
        "service_unavailable",
        "timeout",
        "connection"
    }

    return error_type in fallback_errors


def analyze_error(error: Exception) -> dict:

    error_type = classify_error(error)

    return {
        "error_type": error_type,
        "should_fallback": should_fallback(
            error_type
        )
    }


if __name__ == "__main__":

    print("=" * 60)
    print("ZYRA LUXE - LLM ERROR CLASSIFICATION")
    print("=" * 60)

    test_errors = [
        Exception("429 RESOURCE_EXHAUSTED"),
        Exception("503 UNAVAILABLE"),
        Exception("Request timeout"),
        Exception("401 Unauthorized"),
        Exception("403 Forbidden"),
        Exception("404 model_not_found"),
        Exception("Connection failed"),
        Exception("Unknown application error")
    ]

    for error in test_errors:

        result = analyze_error(error)

        print()
        print(f"Error: {error}")
        print(
            f"Type: "
            f"{result['error_type']}"
        )
        print(
            f"Fallback: "
            f"{result['should_fallback']}"
        )

    print()
    print("=" * 60)
    print("ERROR CLASSIFICATION CHECK COMPLETED")
    print("=" * 60)