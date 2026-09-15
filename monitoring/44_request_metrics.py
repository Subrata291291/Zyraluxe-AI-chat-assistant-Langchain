from collections import Counter


class RequestMetrics:

    def __init__(self, requests):

        self.requests = requests

    def total_requests(self):

        return len(self.requests)

    def successful_requests(self):

        return sum(
            1
            for request in self.requests
            if request["success"]
        )

    def failed_requests(self):

        return sum(
            1
            for request in self.requests
            if not request["success"]
        )

    def average_response_time(self):

        if not self.requests:
            return 0

        total_time = sum(
            request["response_time"]
            for request in self.requests
        )

        return round(
            total_time / len(self.requests),
            3
        )

    def provider_usage(self):

        return Counter(
            request["provider"]
            for request in self.requests
        )

    def success_rate(self):

        if not self.requests:
            return 0

        success_count = (
            self.successful_requests()
        )

        return round(
            (success_count / len(self.requests)) * 100,
            2
        )

    def summary(self):

        return {
            "total_requests": self.total_requests(),
            "successful_requests": self.successful_requests(),
            "failed_requests": self.failed_requests(),
            "success_rate": self.success_rate(),
            "average_response_time": self.average_response_time(),
            "provider_usage": dict(
                self.provider_usage()
            )
        }


if __name__ == "__main__":

    requests = [
        {
            "request_id": "req-001",
            "provider": "gemini",
            "model": "gemini-3.5-flash",
            "success": True,
            "response_time": 1.2
        },
        {
            "request_id": "req-002",
            "provider": "groq",
            "model": "openai/gpt-oss-20b",
            "success": True,
            "response_time": 0.8
        },
        {
            "request_id": "req-003",
            "provider": "gemini",
            "model": "gemini-3.5-flash",
            "success": False,
            "response_time": 2.1
        },
        {
            "request_id": "req-004",
            "provider": "groq",
            "model": "openai/gpt-oss-20b",
            "success": True,
            "response_time": 0.9
        }
    ]

    metrics = RequestMetrics(requests)

    summary = metrics.summary()

    print("=" * 60)
    print("ZYRA LUXE - REQUEST METRICS")
    print("=" * 60)

    print()
    print(f"Total Requests: {summary['total_requests']}")
    print(
        f"Successful Requests: "
        f"{summary['successful_requests']}"
    )
    print(
        f"Failed Requests: "
        f"{summary['failed_requests']}"
    )
    print(
        f"Success Rate: "
        f"{summary['success_rate']}%"
    )
    print(
        f"Average Response Time: "
        f"{summary['average_response_time']} sec"
    )

    print()
    print("Provider Usage")
    print("-" * 40)

    for provider, count in summary["provider_usage"].items():

        print(
            f"{provider}: {count}"
        )

    print()
    print("=" * 60)
    print("REQUEST METRICS CHECK COMPLETED")
    print("=" * 60)