import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
PRODUCT_FILE = PROJECT_ROOT / "data" / "products" / "products.json"


class ProductRanking:

    def __init__(self, file_path=PRODUCT_FILE):
        self.file_path = file_path
        self.products = self.load_products()

    def load_products(self):

        with open(self.file_path, "r", encoding="utf-8") as file:
            return json.load(file)

    def rank(self, products):

        def ranking_score(product):

            score = 0

            if product["in_stock"] is True:
                score += 100

            if product["price"] is not None:
                score += max(0, 1000 - product["price"])

            return score

        return sorted(
            products,
            key=ranking_score,
            reverse=True
        )


if __name__ == "__main__":

    print("=" * 60)
    print("ZYRA LUXE - PRODUCT RANKING")
    print("=" * 60)

    ranking = ProductRanking()

    sample_products = ranking.products[:10]

    results = ranking.rank(sample_products)

    print()
    print(f"Products Ranked: {len(results)}")

    for index, product in enumerate(results, start=1):

        print("-" * 60)

        print(f"Rank: {index}")
        print(f"Name: {product['name']}")
        print(f"Price: ₹{product['price']}")
        print(f"Stock: {product['in_stock']}")

    print()
    print("=" * 60)
    print("PRODUCT RANKING CHECK COMPLETED")
    print("=" * 60)