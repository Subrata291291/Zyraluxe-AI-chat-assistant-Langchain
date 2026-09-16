import os

import httpx
from dotenv import load_dotenv


load_dotenv()


class WooCommerceProductAPI:

    def __init__(self):

        self.base_url = (
            "https://zyraluxe.in/wp-json/wc/v3"
        )

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

    def get_products(
        self,
        page=1,
        per_page=100,
        status="publish"
    ):

        url = (
            f"{self.base_url}/products"
        )

        params = {
            "page": page,
            "per_page": per_page,
            "status": status
        }

        response = httpx.get(
            url,
            params=params,
            auth=(
                self.consumer_key,
                self.consumer_secret
            ),
            timeout=30
        )

        response.raise_for_status()

        products = response.json()

        return {
            "success": True,
            "products": products,
            "count": len(products),
            "page": page,
            "per_page": per_page,
            "total_products": int(
                response.headers.get(
                    "X-WP-Total",
                    0
                )
            )
        }


if __name__ == "__main__":

    print("=" * 60)
    print(
        "ZYRA LUXE - WOOCOMMERCE PRODUCT API"
    )
    print("=" * 60)

    api = WooCommerceProductAPI()

    result = api.get_products(
        page=1,
        per_page=100
    )

    print()
    print(
        f"Products returned: "
        f"{result['count']}"
    )

    print(
        f"Total WooCommerce products: "
        f"{result['total_products']}"
    )

    print()

    for product in result["products"]:

        print("-" * 60)

        print(
            f"ID: "
            f"{product.get('id')}"
        )

        print(
            f"Name: "
            f"{product.get('name')}"
        )

        print(
            f"Price: "
            f"{product.get('price')}"
        )

        print(
            f"Stock: "
            f"{product.get('stock_status')}"
        )

        print(
            f"URL: "
            f"{product.get('permalink')}"
        )

        images = product.get(
            "images",
            []
        )

        if images:

            print(
                f"Image: "
                f"{images[0].get('src')}"
            )

    print()
    print("=" * 60)
    print(
        "WOOCOMMERCE PRODUCT API TEST COMPLETED"
    )
    print("=" * 60)