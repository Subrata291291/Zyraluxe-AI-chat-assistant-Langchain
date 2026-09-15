import importlib.util
from pathlib import Path

import httpx
from bs4 import BeautifulSoup


PROJECT_ROOT = Path(__file__).resolve().parent.parent

CARD_FILE = (
    PROJECT_ROOT / "product" / "70_product_card_response.py"
)


def load_module(name, file_path):
    spec = importlib.util.spec_from_file_location(name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


card_module = load_module(
    "product_card_response",
    CARD_FILE
)


class ProductImageResolver:

    def __init__(self, timeout=15):
        self.card_response = card_module.ProductCardResponse(
            top_k=5
        )
        self.timeout = timeout

    def get_image_url(self, product_url):

        try:
            response = httpx.get(
                product_url,
                timeout=self.timeout,
                follow_redirects=True
            )

            response.raise_for_status()

            soup = BeautifulSoup(
                response.text,
                "html.parser"
            )

            image = soup.select_one(
                ".woocommerce-product-gallery__image img"
            )

            if image and image.get("src"):
                return image["src"]

            image = soup.select_one(
                "meta[property='og:image']"
            )

            if image and image.get("content"):
                return image["content"]

            return None

        except Exception as error:

            print(
                f"Image error for {product_url}: {error}"
            )

            return None

    def search(self, customer_query):

        result = self.card_response.search(
            customer_query
        )

        for product in result["products"]:

            product["image"] = self.get_image_url(
                product["url"]
            )

        return result


if __name__ == "__main__":

    print("=" * 60)
    print("ZYRA LUXE - PRODUCT IMAGE RESOLVER")
    print("=" * 60)

    resolver = ProductImageResolver()

    query = "I want oxidized jewellery"

    result = resolver.search(query)

    print()
    print(f"Customer Query: {result['query']}")
    print()
    print(f"Product Cards: {len(result['products'])}")

    for index, product in enumerate(
        result["products"],
        start=1
    ):

        print()
        print(f"Card {index}")
        print(f"Name: {product['name']}")
        print(f"Price: ₹{product['price']}")
        print(f"Stock: {product['stock_label']}")
        print(f"Image: {product['image']}")
        print(f"URL: {product['url']}")

    print()
    print("=" * 60)
    print("PRODUCT IMAGE RESOLUTION COMPLETED")
    print("=" * 60)