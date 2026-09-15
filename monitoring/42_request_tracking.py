import time
import uuid


class RequestTracker:

    def __init__(self):

        self.requests = []

    def start_request(self):

        request_id = str(uuid.uuid4())

        start_time = time.perf_counter()

        return request_id, start_time

    def finish_request(
        self,
        request_id,
        start_time,
        provider,
        success
    ):

        response_time = (
            time.perf_counter()
            - start_time
        )

        request_data = {
            "request_id": request_id,
            "provider": provider,
            "success": success,
            "response_time": round(
                response_time,
                3
            )
        }

        self.requests.append(
            request_data
        )

        return request_data

    def get_requests(self):

        return self.requests


if __name__ == "__main__":

    print("=" * 60)
    print("ZYRA LUXE - REQUEST TRACKING")
    print("=" * 60)

    tracker = RequestTracker()

    request_id, start_time = (
        tracker.start_request()
    )

    print()
    print(f"Request ID: {request_id}")

    time.sleep(1)

    result = tracker.finish_request(
        request_id=request_id,
        start_time=start_time,
        provider="groq",
        success=True
    )

    print()
    print("Request Result")
    print("-" * 40)

    print(
        f"Request ID: "
        f"{result['request_id']}"
    )

    print(
        f"Provider: "
        f"{result['provider']}"
    )

    print(
        f"Success: "
        f"{result['success']}"
    )

    print(
        f"Response Time: "
        f"{result['response_time']} sec"
    )

    print()
    print("=" * 60)
    print("REQUEST TRACKING CHECK COMPLETED")
    print("=" * 60)