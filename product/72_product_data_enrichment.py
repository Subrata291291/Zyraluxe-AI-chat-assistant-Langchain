import json
import importlib.util
import time
from pathlib import Path


INPUT_FILE = Path("data/products/products.json")
OUTPUT_FILE = Path("data/products/products_enriched.json")


def load_module(path, module_name):
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_products():
    with open(INPUT_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def save_products(products):
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        json.dump(products, file, ensure_ascii=False, indent=2)


def enrich_products():
    module = load_module(
        "product/71_product_image_resolver.py",
        "product_image_resolver"
    )

    resolver = module.ProductImageResolver()
    products = load_products()

    enriched = []

    for index, product in enumerate(products, start=1):
        url = product.get("url")

        image_url = None

        if url:
            try:
                image_url = resolver.get_image_url(url)
            except Exception as error:
                print(f"Image error: {product.get('name')}")
                print(error)

        enriched_product = product.copy()
        enriched_product["image"] = image_url

        enriched.append(enriched_product)

        print(
            f"{index}/{len(products)} - "
            f"{product.get('name')} -> {image_url}"
        )

        time.sleep(0.5)

    save_products(enriched)

    print("\nEnrichment completed.")
    print(f"Products: {len(enriched)}")
    print(f"Output: {OUTPUT_FILE}")


if __name__ == "__main__":
    enrich_products()