import os

import httpx
from dotenv import load_dotenv


load_dotenv()


class WooCommerceOrderAPI:

    def __init__(self):

        self.base_url = "https://zyraluxe.in/wp-json/wc/v3"

        self.consumer_key = os.getenv(
            "WOOCOMMERCE_CONSUMER_KEY"
        )

        self.consumer_secret = os.getenv(
            "WOOCOMMERCE_CONSUMER_SECRET"
        )

        if not self.consumer_key:
            raise ValueError(
                "WOOCOMMERCE_CONSUMER_KEY is missing"
            )

        if not self.consumer_secret:
            raise ValueError(
                "WOOCOMMERCE_CONSUMER_SECRET is missing"
            )

    def get_order(self, order_id):

        url = f"{self.base_url}/orders/{order_id}"

        response = httpx.get(
            url,
            auth=(
                self.consumer_key,
                self.consumer_secret
            ),
            timeout=15
        )

        if response.status_code == 404:

            return {
                "success": False,
                "error": "Order not found"
            }

        response.raise_for_status()

        order = response.json()

        return {
            "success": True,
            "order": {
                "id": order.get("id"),
                "status": order.get("status"),
                "date_created": order.get("date_created"),
                "total": order.get("total"),
                "currency": order.get("currency"),
                "payment_method": order.get(
                    "payment_method_title"
                ),
            }
        }


if __name__ == "__main__":

    print("=" * 60)
    print("ZYRA LUXE - WOOCOMMERCE ORDER API")
    print("=" * 60)

    order_id = input(
        "\nEnter a test order ID: "
    ).strip()

    api = WooCommerceOrderAPI()

    result = api.get_order(order_id)

    print()
    print("RESULT:")
    print(result)

    print()
    print("=" * 60)
    print("ORDER API TEST COMPLETED")
    print("=" * 60)