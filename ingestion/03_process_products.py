import json
import re
from pathlib import Path


# ------------------------------------------------------------
# FILE PATHS
# ------------------------------------------------------------

INPUT_FILE = Path("data/raw/products_raw.json")
OUTPUT_FILE = Path("data/products/products.json")


# ------------------------------------------------------------
# HELPER FUNCTIONS
# ------------------------------------------------------------

def clean_text(value: str | None) -> str | None:
    """Remove unnecessary whitespace."""

    if not value:
        return None

    return " ".join(value.split())


def normalize_list(values: list | None) -> list[str]:
    """Clean list values and remove duplicates."""

    if not values:
        return []

    cleaned = []

    for value in values:

        value = clean_text(str(value))

        if value and value not in cleaned:
            cleaned.append(value)

    return cleaned


def normalize_price(value: str | None) -> float | None:
    """Convert price text into a numeric value."""

    if not value:
        return None

    # Keep only digits and decimal point.
    cleaned = re.sub(r"[^\d.]", "", value)

    if not cleaned:
        return None

    try:
        return float(cleaned)
    except ValueError:
        return None


def normalize_stock(value: str | None) -> bool | None:
    """Convert stock text into True/False."""

    if not value:
        return None

    value = value.lower()

    if "out of stock" in value:
        return False

    if "in stock" in value:
        return True

    return None


def clean_product(product: dict) -> dict:
    """Clean and normalize one product."""

    return {
        "name": clean_text(product.get("name")),

        "price": normalize_price(
            product.get("price")
        ),

        "regular_price": normalize_price(
            product.get("regular_price")
        ),

        "sale_price": normalize_price(
            product.get("sale_price")
        ),

        "stock_status": clean_text(
            product.get("stock_status")
        ),

        "in_stock": normalize_stock(
            product.get("stock_status")
        ),

        "sku": clean_text(
            product.get("sku")
        ),

        "categories": normalize_list(
            product.get("categories")
        ),

        "tags": normalize_list(
            product.get("tags")
        ),

        "description": clean_text(
            product.get("description")
        ),

        "url": clean_text(
            product.get("url")
        ),

        "image_url": clean_text(
            product.get("image_url")
        ),
    }


def is_valid_product(product: dict) -> bool:
    """Check whether minimum product information exists."""

    # Product name and URL are required.
    return bool(
        product.get("name")
        and product.get("url")
    )


def remove_duplicates(products: list[dict]) -> list[dict]:
    """Remove duplicate products using URL."""

    unique_products = {}
    
    for product in products:

        url = product.get("url")

        if url:
            unique_products[url] = product

    return list(unique_products.values())


# ------------------------------------------------------------
# LOAD RAW PRODUCTS
# ------------------------------------------------------------

def load_products() -> list[dict]:
    """Read raw product JSON."""

    if not INPUT_FILE.exists():

        raise FileNotFoundError(
            f"Input file not found: {INPUT_FILE}"
        )

    with INPUT_FILE.open(
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


# ------------------------------------------------------------
# PROCESS PRODUCTS
# ------------------------------------------------------------

def process_products(
    raw_products: list[dict]
) -> list[dict]:

    clean_products = []

    for product in raw_products:

        cleaned = clean_product(product)

        if is_valid_product(cleaned):

            clean_products.append(cleaned)

    # Remove duplicate products.
    clean_products = remove_duplicates(
        clean_products
    )

    return clean_products


# ------------------------------------------------------------
# SAVE CLEAN PRODUCTS
# ------------------------------------------------------------

def save_products(
    products: list[dict]
) -> None:

    # Create output directory if necessary.
    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with OUTPUT_FILE.open(
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            products,
            file,
            indent=4,
            ensure_ascii=False
        )


# ------------------------------------------------------------
# MAIN
# ------------------------------------------------------------

if __name__ == "__main__":

    print("=" * 60)
    print("ZYRA LUXE PRODUCT PROCESSING")
    print("=" * 60)

    # Load raw data.
    raw_products = load_products()

    print(
        f"Raw products: {len(raw_products)}"
    )

    # Clean and normalize data.
    clean_products = process_products(
        raw_products
    )

    print(
        f"Clean products: {len(clean_products)}"
    )

    # Save processed data.
    save_products(
        clean_products
    )

    print()
    print("=" * 60)
    print("PROCESSING COMPLETED")
    print("=" * 60)

    print(
        f"Output file: {OUTPUT_FILE}"
    )