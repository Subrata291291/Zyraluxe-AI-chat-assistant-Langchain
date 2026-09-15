def get_safe_error_message(
    error: Exception
) -> str:

    error_text = str(error).lower()

    if "429" in error_text:
        return (
            "I'm temporarily unable to process "
            "your request because the service limit "
            "has been reached. Please try again later."
        )

    if "503" in error_text:
        return (
            "I'm temporarily unable to process "
            "your request. Please try again in a moment."
        )

    if "timeout" in error_text:
        return (
            "The request took too long to complete. "
            "Please try again."
        )

    if "pinecone" in error_text:
        return (
            "I'm having trouble accessing the "
            "knowledge base. Please try again later."
        )

    return (
        "Sorry, something went wrong while "
        "processing your request. Please try again."
    )


def handle_error(
    error: Exception
) -> dict:

    return {
        "success": False,
        "message": get_safe_error_message(
            error
        )
    }


if __name__ == "__main__":

    print("=" * 60)
    print("ZYRA LUXE - ERROR HANDLER")
    print("=" * 60)

    test_errors = [
        Exception("429 RESOURCE_EXHAUSTED"),
        Exception("503 UNAVAILABLE"),
        Exception("Request timeout"),
        Exception("Pinecone connection failed"),
        Exception("Unknown application error"),
    ]

    for error in test_errors:

        result = handle_error(error)

        print()
        print(f"Original Error: {error}")
        print(
            f"Safe Message: "
            f"{result['message']}"
        )

    print()
    print("=" * 60)
    print("ERROR HANDLER CHECK COMPLETED")
    print("=" * 60)