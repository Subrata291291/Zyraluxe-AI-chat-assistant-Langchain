import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent

PRODUCT_FILE = (
    PROJECT_ROOT
    / "data"
    / "products"
    / "products.json"
)

OUTPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "products"
    / "product_embedding_records.json"
)


class ProductEmbeddingPreparation:

    def __init__(self, product_file=PRODUCT_FILE):

        self.product_file = product_file
        self.products = self.load_products()

    def load_products(self):

        with open(
            self.product_file,
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(file)

    def create_search_text(self, product):

        categories = ", ".join(
            product.get("categories", [])
        )

        tags = ", ".join(
            product.get("tags", [])
        )

        parts = [
            f"Product name: {product.get('name') or ''}",
            f"Categories: {categories}",
            f"Tags: {tags}",
            f"Description: {product.get('description') or ''}"
        ]

        return "\n".join(parts)

    def prepare(self):

        records = []

        for product in self.products:

            search_text = self.create_search_text(
                product
            )

            records.append(
                {
                    "id": product["url"],
                    "text": search_text,
                    "metadata": {
                        "name": product["name"],
                        "url": product["url"],
                        "categories": product.get(
                            "categories",
                            []
                        ),
                        "tags": product.get(
                            "tags",
                            []
                        )
                    }
                }
            )

        return records

    def save(self, records):

        with open(
            OUTPUT_FILE,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                records,
                file,
                ensure_ascii=False,
                indent=2
            )


if __name__ == "__main__":

    print("=" * 60)
    print("ZYRA LUXE - PRODUCT EMBEDDING PREPARATION")
    print("=" * 60)

    preparation = ProductEmbeddingPreparation()

    records = preparation.prepare()

    preparation.save(records)

    print()
    print(f"Products Loaded: {len(preparation.products)}")
    print(f"Embedding Records: {len(records)}")

    print()
    print("-" * 60)
    print("SAMPLE SEARCH TEXT")
    print("-" * 60)

    if records:

        print(records[0]["text"])

    print()
    print("-" * 60)
    print(f"Output: {OUTPUT_FILE}")
    print("-" * 60)

    print()
    print("=" * 60)
    print("PRODUCT EMBEDDING PREPARATION COMPLETED")
    print("=" * 60)