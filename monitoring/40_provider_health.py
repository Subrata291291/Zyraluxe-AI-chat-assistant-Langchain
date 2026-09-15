class ProviderHealth:

    def __init__(self, providers):

        self.stats = {
            provider: {
                "success": 0,
                "failures": 0,
                "fallbacks": 0
            }
            for provider in providers
        }

    def record_success(self, provider):

        self.stats[provider]["success"] += 1

    def record_failure(self, provider):

        self.stats[provider]["failures"] += 1

    def record_fallback(self, provider):

        self.stats[provider]["fallbacks"] += 1

    def get_stats(self):

        return self.stats

    def display(self):

        print()
        print("=" * 60)
        print("LLM PROVIDER HEALTH")
        print("=" * 60)

        for provider, stats in self.stats.items():

            print()
            print(f"Provider: {provider}")
            print(
                f"  Successes: "
                f"{stats['success']}"
            )
            print(
                f"  Failures: "
                f"{stats['failures']}"
            )
            print(
                f"  Fallbacks: "
                f"{stats['fallbacks']}"
            )


if __name__ == "__main__":

    print("=" * 60)
    print("ZYRA LUXE - PROVIDER HEALTH TRACKING")
    print("=" * 60)

    providers = [
        "gemini",
        "groq",
        "openrouter",
        "openai"
    ]

    health = ProviderHealth(providers)

    health.record_success("gemini")

    health.record_failure("gemini")
    health.record_fallback("gemini")

    health.record_success("groq")

    health.record_failure("groq")
    health.record_fallback("groq")

    health.record_success("openrouter")

    health.display()

    print()
    print("=" * 60)
    print("PROVIDER HEALTH CHECK COMPLETED")
    print("=" * 60)