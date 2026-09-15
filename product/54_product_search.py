import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent

PRODUCT_FILE = (
    PROJECT_ROOT
    / "data"
    / "products"
    / "products.json"
)


class ProductSearch:

    def __init__(self, file_path=PRODUCT_FILE):

        self.file_path = file_path
        self.products = self.load_products()

    def load_products(self):

        with open(
            self.file_path,
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(file)

    def search(
        self,
        query=None,
        max_price=None,
        category=None,
        in_stock=None
    ):

        results = self.products

        if query:

            query = query.lower()

            results = [
                product
                for product in results
                if query in (product.get("name") or "").lower()
                or query in (product.get("description") or "").lower()
            ]

        if max_price is not None:

            results = [
                product
                for product in results
                if product.get("price") is not None
                and product["price"] <= max_price
            ]

        if category:

            category = category.lower()

            results = [
                product
                for product in results
                if any(
                    category in (item or "").lower()
                    for item in product.get("categories", [])
                )
            ]

        if in_stock is not None:

            results = [
                product
                for product in results
                if product.get("in_stock") == in_stock
            ]

        return results


if __name__ == "__main__":

    print("=" * 60)
    print("ZYRA LUXE - PRODUCT SEARCH")
    print("=" * 60)

    search = ProductSearch()

    tests = [
        {
            "name": "All Earrings",
            "params": {"category": "earrings"}
        },
        {
            "name": "Products Under ₹200",
            "params": {"max_price": 200}
        },
        {
            "name": "In-stock Products",
            "params": {"in_stock": True}
        },
        {
            "name": "Earrings Under ₹200 In Stock",
            "params": {
                "category": "earrings",
                "max_price": 200,
                "in_stock": True
            }
        }
    ]

    for test in tests:

        results = search.search(**test["params"])

        print()
        print("-" * 60)
        print(test["name"])
        print("-" * 60)
        print(f"Products Found: {len(results)}")

        for product in results[:5]:

            print(
                f"{product['name']} | "
                f"₹{product['price']} | "
                f"Stock: {product['in_stock']}"
            )

    print()
    print("=" * 60)
    print("PRODUCT SEARCH CHECK COMPLETED")
    print("=" * 60)