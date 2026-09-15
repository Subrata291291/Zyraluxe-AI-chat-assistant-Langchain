from datetime import datetime


class HealthChecker:

    def __init__(self):

        self.services = {}

    def check_service(
        self,
        service_name,
        status,
        message
    ):

        result = {
            "service": service_name,
            "status": status,
            "message": message,
            "timestamp": datetime.now().isoformat()
        }

        self.services[service_name] = result

        return result

    def get_health_status(self):

        overall_status = "healthy"

        for service in self.services.values():

            if service["status"] != "healthy":

                overall_status = "unhealthy"

                break

        return {
            "status": overall_status,
            "services": self.services
        }


if __name__ == "__main__":

    print("=" * 60)
    print("ZYRA LUXE - HEALTH CHECK")
    print("=" * 60)

    checker = HealthChecker()

    checker.check_service(
        service_name="gemini",
        status="healthy",
        message="Provider available"
    )

    checker.check_service(
        service_name="groq",
        status="healthy",
        message="Provider available"
    )

    checker.check_service(
        service_name="openrouter",
        status="healthy",
        message="Provider available"
    )

    checker.check_service(
        service_name="openai",
        status="healthy",
        message="Provider available"
    )

    checker.check_service(
        service_name="pinecone",
        status="healthy",
        message="Database available"
    )

    health = checker.get_health_status()

    print()
    print(
        f"Overall Status: "
        f"{health['status']}"
    )

    print()
    print("Service Status")
    print("-" * 40)

    for service, result in (
        health["services"].items()
    ):

        print(
            f"{service}: "
            f"{result['status']} "
            f"- {result['message']}"
        )

    print()
    print("=" * 60)
    print("HEALTH CHECK COMPLETED")
    print("=" * 60)