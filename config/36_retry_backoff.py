import time


def retry_with_backoff(
    operation,
    max_retries=2,
    base_delay=2
):

    for attempt in range(max_retries + 1):

        try:

            return operation()

        except Exception as error:

            if attempt == max_retries:
                raise error

            delay = base_delay * (2 ** attempt)

            print()
            print(
                f"Attempt {attempt + 1} failed."
            )
            print(
                f"Retrying in {delay} seconds..."
            )

            time.sleep(delay)


def test_operation():

    test_operation.counter += 1

    print(
        f"Running operation "
        f"attempt {test_operation.counter}"
    )

    if test_operation.counter < 3:
        raise Exception(
            "503 Service Unavailable"
        )

    return "Operation succeeded."


test_operation.counter = 0


if __name__ == "__main__":

    print("=" * 60)
    print("ZYRA LUXE - RETRY BACKOFF")
    print("=" * 60)

    try:

        result = retry_with_backoff(
            test_operation,
            max_retries=2,
            base_delay=2
        )

        print()
        print(f"Result: {result}")

    except Exception as error:

        print()
        print(f"Final Error: {error}")

    print()
    print("=" * 60)
    print("RETRY BACKOFF CHECK COMPLETED")
    print("=" * 60)