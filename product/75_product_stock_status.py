import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent

INPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "products"
    / "products_enriched.json"
)

OUTPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "products"
    / "products_stock_normalized.json"
)


def load_products():
    with open(INPUT_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def save_products(products):
    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        json.dump(
            products,
            file,
            ensure_ascii=False,
            indent=2
        )


def normalize_stock_status(in_stock):

    if in_stock is True:
        return "In Stock"

    if in_stock is False:
        return "Out of Stock"

    return "Stock Unknown"


def normalize_products():

    products = load_products()

    normalized_products = []

    for product in products:

        normalized_product = product.copy()

        normalized_product["stock_label"] = (
            normalize_stock_status(
                product.get("in_stock")
            )
        )

        normalized_products.append(
            normalized_product
        )

    save_products(normalized_products)

    return normalized_products


if __name__ == "__main__":

    products = normalize_products()

    print("=" * 60)
    print("ZYRA LUXE - STOCK STATUS NORMALIZATION")
    print("=" * 60)

    in_stock = 0
    out_of_stock = 0
    unknown = 0

    for product in products:

        status = product["stock_label"]

        if status == "In Stock":
            in_stock += 1
        elif status == "Out of Stock":
            out_of_stock += 1
        else:
            unknown += 1

    print()
    print(f"Total Products: {len(products)}")
    print(f"In Stock: {in_stock}")
    print(f"Out of Stock: {out_of_stock}")
    print(f"Stock Unknown: {unknown}")

    print()
    print("Unknown Stock Products:")

    for product in products:

        if product["stock_label"] == "Stock Unknown":
            print(
                f"- {product['name']}"
            )

    print()
    print(f"Output: {OUTPUT_FILE}")