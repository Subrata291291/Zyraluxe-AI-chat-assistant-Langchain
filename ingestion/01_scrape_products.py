# ============================================================
# ZYRA LUXE AI ASSISTANT
# FILE: 01_scrape_products.py
# ============================================================
#
# PURPOSE:
# -------
# This file collects product information from the Zyra Luxe
# website and saves that information into a JSON file.
#
# CURRENT PIPELINE:
#
# Zyra Luxe Website
#        ↓
# Shop Pages
#        ↓
# Product URLs
#        ↓
# Individual Product Pages
#        ↓
# BeautifulSoup
#        ↓
# Extract Product Information
#        ↓
# JSON
#        ↓
# data/raw/products_raw.json
#
#
# IMPORTANT:
# ----------
# This file DOES NOT:
#
# ❌ Create embeddings
# ❌ Use Pinecone
# ❌ Use Gemini
# ❌ Perform RAG
# ❌ Generate answers
#
# This file's only job is DATA INGESTION.
# ============================================================


# ------------------------------------------------------------
# IMPORTS
# ------------------------------------------------------------

# json
# ----
# Python-এর dictionary/list-কে JSON format-এ save করার জন্য
# ব্যবহার করব।
#
# আমাদের scraped products শেষ পর্যন্ত JSON file-এ থাকবে।
import json


# time
# ----
# Website-এ একটার পর একটা request পাঠানোর মধ্যে কিছু
# delay রাখার জন্য ব্যবহার করছি।
#
# এতে আমরা খুব দ্রুত website-এ অনেক request পাঠাব না।
import time


# Path
# ----
# File এবং folder path সুন্দরভাবে handle করার জন্য।
#
# যেমন:
# data/raw/products_raw.json
#
# Path object ব্যবহার করলে Windows/Linux path handling
# সহজ হয়।
from pathlib import Path


# httpx
# -----
# Website-এ HTTP request পাঠানোর জন্য ব্যবহার করছি।
#
# Python → HTTP GET request → Website → HTML response
#
# httpx হলো আমাদের HTTP client।
import httpx


# BeautifulSoup
# -------------
# Website থেকে পাওয়া HTML parse করার জন্য ব্যবহার করছি।
#
# HTML-এর ভিতরের:
#   title
#   price
#   SKU
#   category
#   description
# ইত্যাদি বের করতে BeautifulSoup ব্যবহার করব।
from bs4 import BeautifulSoup


# load_dotenv
# -----------
# .env file থেকে environment variables load করার জন্য।
#
# বর্তমানে এই scraper-এর জন্য API key দরকার নেই,
# কিন্তু project-এর configuration pattern consistent
# রাখার জন্য load_dotenv() ব্যবহার করছি।
from dotenv import load_dotenv


# ============================================================
# CONFIGURATION
# ============================================================

# .env file-এর variables environment-এ load করবে।
#
# Example:
#
# GOOGLE_API_KEY=...
# PINECONE_API_KEY=...
#
# এগুলো পরে project-এর অন্য files-এ প্রয়োজন হবে।
load_dotenv()


# ------------------------------------------------------------
# WEBSITE CONFIGURATION
# ------------------------------------------------------------

# Zyra Luxe website-এর মূল domain।
BASE_URL = "https://zyraluxe.in"


# Shop page-এর URL তৈরি করছি।
#
# f-string ব্যবহার করে:
#
# BASE_URL = https://zyraluxe.in
#
# এর সঙ্গে /shop/ যোগ হবে।
#
# Result:
#
# https://zyraluxe.in/shop/
SHOP_URL = f"{BASE_URL}/shop/"


# ------------------------------------------------------------
# SCRAPING LIMIT
# ------------------------------------------------------------

# প্রথম test-এর সময় আমরা শুধু 2টি shop page scrape করব।
#
# Production-এ পরে এই value বাড়ানো যাবে।
#
# 2 pages দিয়ে শুরু করার কারণ:
#
# প্রথমে আমরা verify করতে চাই:
#
# Website request কাজ করছে?
# Product URL পাওয়া যাচ্ছে?
# Product page কাজ করছে?
# Product fields পাওয়া যাচ্ছে?
# JSON ঠিকভাবে তৈরি হচ্ছে?
#
# সব ঠিক হলে পরে পুরো catalogue scrape করব।
MAX_PAGES = 2


# ------------------------------------------------------------
# REQUEST DELAY
# ------------------------------------------------------------

# প্রতিটি request-এর মধ্যে 1 second delay রাখছি।
#
# Example:
#
# Request product 1
#       ↓
# Wait 1 second
#       ↓
# Request product 2
#       ↓
# Wait 1 second
#
# Real-world scraping-এ rate limiting এবং respectful
# request behaviour গুরুত্বপূর্ণ।
REQUEST_DELAY = 1.0


# ------------------------------------------------------------
# OUTPUT FILE
# ------------------------------------------------------------

# Scraped product data এই JSON file-এ save হবে।
#
# Path object ব্যবহার করছি।
#
# Final path:
#
# data/
#   raw/
#       products_raw.json
OUTPUT_FILE = Path("data/raw/products_raw.json")


# ============================================================
# HTTP HEADERS
# ============================================================

# Website-এ request পাঠানোর সময় User-Agent পাঠানো হচ্ছে।
#
# Browser সাধারণত request-এর সঙ্গে User-Agent পাঠায়।
#
# এখানে আমরা একটি normal browser-এর মতো User-Agent ব্যবহার করছি।
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/140.0.0.0 Safari/537.36"
    )
}


# ============================================================
# HELPER FUNCTION 1
# ============================================================

def clean_text(text: str | None) -> str:
    """
    Text থেকে unnecessary whitespace remove করে।

    Example:

    Input:
        "   Beautiful    Gold   Earrings   "

    Output:
        "Beautiful Gold Earrings"
    """

    # যদি text None বা empty হয়,
    # তাহলে empty string return করব।
    if not text:
        return ""


    # split() multiple spaces/newlines/tabs আলাদা করে।
    #
    # তারপর " ".join(...)
    # সবকিছু single space দিয়ে আবার join করে।
    #
    # Example:
    #
    # "Hello     World"
    #
    # becomes:
    #
    # "Hello World"
    return " ".join(text.split())


# ============================================================
# HELPER FUNCTION 2
# ============================================================
def get_price(product_soup: BeautifulSoup) -> dict:
    price_box = (
        product_soup.select_one(".summary .price")
        or product_soup.select_one(".product .price")
        or product_soup.select_one("p.price")
        or product_soup.select_one("span.price")
    )

    if not price_box:
        return {
            "price": None,
            "regular_price": None,
            "sale_price": None,
        }

    regular_element = price_box.select_one("del .amount")
    sale_element = price_box.select_one("ins .amount")

    regular = (
        clean_text(regular_element.get_text(" ", strip=True))
        if regular_element
        else None
    )

    sale = (
        clean_text(sale_element.get_text(" ", strip=True))
        if sale_element
        else None
    )

    amounts = price_box.select(".amount")

    if sale:
        displayed = sale
    elif amounts:
        displayed = clean_text(
            amounts[-1].get_text(" ", strip=True)
        )
    else:
        displayed = clean_text(
            price_box.get_text(" ", strip=True)
        )

    return {
        "price": displayed,
        "regular_price": regular,
        "sale_price": sale,
    }

# ============================================================
# HELPER FUNCTION 3
# ============================================================

def extract_product_links(shop_soup: BeautifulSoup) -> list[str]:
    """
    Shop page থেকে individual product URLs বের করে।

    আমরা /product/ URL pattern ব্যবহার করছি।
    """


    # set ব্যবহার করছি যাতে duplicate URL automatically
    # বাদ যায়।
    #
    # Example:
    #
    # একই product-এর link 3 বার থাকলেও
    # set-এ একবারই থাকবে।
    links = set()


    # Shop page-এর সমস্ত <a> element খুঁজছি
    # যাদের href-এর মধ্যে "/product/" আছে।
    #
    # CSS selector:
    #
    # a[href*="/product/"]
    #
    # এর অর্থ:
    #
    # <a> tag
    # যার href attribute-এর মধ্যে
    # "/product/" text আছে।
    for link in shop_soup.select(
        'a[href*="/product/"]'
    ):


        # <a> tag-এর href attribute বের করছি।
        href = link.get("href")


        # href না থাকলে এই link skip করব।
        if not href:
            continue


        # Extra whitespace remove করছি।
        href = href.strip()


        # যদি URL relative হয়:
        #
        # /product/example/
        #
        # তাহলে BASE_URL-এর সঙ্গে যোগ করে:
        #
        # https://zyraluxe.in/product/example/
        #
        # বানাব।
        if href.startswith("/product/"):

            href = f"{BASE_URL}{href}"


        # এখন নিশ্চিত করছি যে URL সত্যিই Zyra Luxe-এর
        # product URL।
        if href.startswith(
            f"{BASE_URL}/product/"
        ):

            # set-এ URL যোগ করছি।
            links.add(href)


    # set-কে sorted list-এ convert করে return করছি।
    return sorted(links)


# ============================================================
# HELPER FUNCTION 4
# ============================================================

def extract_product(
    product_soup: BeautifulSoup,
    url: str
) -> dict:
    """
    Individual product page থেকে product information
    extract করে একটি dictionary তৈরি করে।
    """


    # --------------------------------------------------------
    # PRODUCT TITLE
    # --------------------------------------------------------

    # Product title-এর element খুঁজছি।
    #
    # WooCommerce product page-এ সাধারণত:
    #
    # <h1 class="product_title">
    #
    # থাকে।
    title_element = product_soup.select_one(
        ".product_title"
    )


    # Element পাওয়া গেলে তার text বের করে clean করছি।
    #
    # না পাওয়া গেলে None।
    title = (
        clean_text(
            title_element.get_text(
                " ",
                strip=True
            )
        )
        if title_element
        else None
    )


    # --------------------------------------------------------
    # PRICE
    # --------------------------------------------------------

    # Price extraction-এর জন্য আমাদের আলাদা function call করছি।
    price_data = get_price(product_soup)


    # --------------------------------------------------------
    # SKU
    # --------------------------------------------------------

    # Product page-এর SKU element খুঁজছি।
    sku_element = product_soup.select_one(
        ".sku"
    )


    # SKU পাওয়া গেলে text clean করছি।
    sku = (
        clean_text(
            sku_element.get_text(
                " ",
                strip=True
            )
        )
        if sku_element
        else None
    )


    # --------------------------------------------------------
    # CATEGORIES
    # --------------------------------------------------------

    # Product metadata-এর posted_in section-এর
    # category links খুঁজছি।
    category_elements = product_soup.select(
        ".product_meta .posted_in a"
    )


    # সব category-এর text একটি list-এ রাখছি।
    #
    # Example:
    #
    # [
    #     "Earrings",
    #     "Oxidised Jhumka"
    # ]
    categories = [

        clean_text(
            category.get_text(
                " ",
                strip=True
            )
        )

        for category in category_elements
    ]


    # --------------------------------------------------------
    # TAGS
    # --------------------------------------------------------

    # Product tags খুঁজছি।
    tag_elements = product_soup.select(
        ".product_meta .tagged_as a"
    )


    # সব tags list-এ রাখছি।
    tags = [

        clean_text(
            tag.get_text(
                " ",
                strip=True
            )
        )

        for tag in tag_elements
    ]


    # --------------------------------------------------------
    # DESCRIPTION
    # --------------------------------------------------------

    # Product-এর short description খুঁজছি।
    description_element = product_soup.select_one(
        ".woocommerce-product-details__short-description"
    )


    # Description পাওয়া গেলে clean করছি।
    description = (
        clean_text(
            description_element.get_text(
                " ",
                strip=True
            )
        )
        if description_element
        else None
    )


    # --------------------------------------------------------
    # STOCK STATUS
    # --------------------------------------------------------

    # Product stock element খুঁজছি।
    #
    # Example:
    #
    # "In stock"
    #
    # অথবা:
    #
    # "Out of stock"
    stock_element = product_soup.select_one(
        ".stock"
    )


    # Stock status পাওয়া গেলে clean করছি।
    stock_status = (
        clean_text(
            stock_element.get_text(
                " ",
                strip=True
            )
        )
        if stock_element
        else None
    )


    # --------------------------------------------------------
    # PRODUCT IMAGE
    # --------------------------------------------------------

    # Main product image খুঁজছি।
    image_element = product_soup.select_one(
        ".woocommerce-product-gallery__image img"
    )


    # শুরুতে image_url None।
    image_url = None


    # Image পাওয়া গেলে:
    if image_element:

        # অনেক WooCommerce site-এ বড় image URL
        # data-large_image attribute-এ থাকে।
        #
        # সেটা না থাকলে src ব্যবহার করব।
        image_url = (
            image_element.get(
                "data-large_image"
            )
            or image_element.get(
                "src"
            )
        )


    # --------------------------------------------------------
    # FINAL PRODUCT OBJECT
    # --------------------------------------------------------

    # সব extracted information একটি dictionary হিসেবে
    # return করছি।
    #
    # এই dictionary পরে JSON-এ convert হবে।
    return {

        "name": title,

        "price": price_data["price"],

        "regular_price": price_data[
            "regular_price"
        ],

        "sale_price": price_data[
            "sale_price"
        ],

        "stock_status": stock_status,

        "sku": sku,

        "categories": categories,

        "tags": tags,

        "description": description,

        "url": url,

        "image_url": image_url,
    }


# ============================================================
# MAIN SCRAPER FUNCTION
# ============================================================

def scrape_products() -> list[dict]:
    """
    Main scraping function.

    কাজ:

    1. Shop pages visit করবে।
    2. Product URLs collect করবে।
    3. Individual product pages visit করবে।
    4. Product information extract করবে।
    5. সব products একটি list return করবে।
    """


    # এখানে final product objects রাখব।
    #
    # Example:
    #
    # [
    #     {"name": "...", "price": "..."},
    #     {"name": "...", "price": "..."}
    # ]
    products = []


    # Product URLs-এর জন্য set ব্যবহার করছি।
    #
    # Duplicate product URLs prevent করবে।
    product_urls = set()


    # --------------------------------------------------------
    # HTTP CLIENT
    # --------------------------------------------------------

    # httpx.Client() ব্যবহার করলে একই HTTP client-এর মাধ্যমে
    # multiple requests efficiently করা যায়।
    #
    # headers:
    # Browser-like User-Agent পাঠাবে।
    #
    # timeout:
    # কোনো request 20 seconds-এর বেশি আটকে থাকলে
    # timeout হবে।
    #
    # follow_redirects:
    # Website redirect করলে automatically follow করবে।
    with httpx.Client(

        headers=HEADERS,

        timeout=20.0,

        follow_redirects=True,

    ) as client:


        # ====================================================
        # STEP 1
        # COLLECT PRODUCT URLS
        # ====================================================

        # MAX_PAGES যত,
        # ততগুলো shop page visit করব।
        #
        # range(1, 3)
        #
        # gives:
        #
        # 1
        # 2
        for page_number in range(
            1,
            MAX_PAGES + 1
        ):


            # ------------------------------------------------
            # PAGE URL
            # ------------------------------------------------

            # First page-এর URL:
            #
            # https://zyraluxe.in/shop/
            if page_number == 1:

                page_url = SHOP_URL


            # Second page:
            #
            # https://zyraluxe.in/shop/page/2/
            #
            # Third:
            #
            # https://zyraluxe.in/shop/page/3/
            #
            # etc.
            else:

                page_url = (
                    f"{SHOP_URL}"
                    f"page/{page_number}/"
                )


            # ------------------------------------------------
            # LOGGING
            # ------------------------------------------------

            print()

            print(
                "=" * 60
            )

            print(
                f"Scraping shop page "
                f"{page_number}"
            )

            print(
                page_url
            )

            print(
                "=" * 60
            )


            # ------------------------------------------------
            # HTTP REQUEST
            # ------------------------------------------------

            try:

                # Website-এ GET request পাঠাচ্ছি।
                response = client.get(
                    page_url
                )


                # HTTP status দেখাচ্ছি।
                #
                # 200 = successful
                print(
                    f"HTTP Status: "
                    f"{response.status_code}"
                )


                # যদি HTTP error থাকে,
                # exception raise করবে।
                #
                # Example:
                #
                # 404
                # 500
                # etc.
                response.raise_for_status()


            # HTTP-related error ধরছি।
            except httpx.HTTPError as error:

                print(
                    f"Could not fetch "
                    f"shop page: {error}"
                )

                # এই page বাদ দিয়ে next page-এ যাব।
                continue


            # ------------------------------------------------
            # PARSE HTML
            # ------------------------------------------------

            # response.text হলো website থেকে পাওয়া
            # সম্পূর্ণ HTML text।
            #
            # BeautifulSoup সেটাকে parse করবে।
            shop_soup = BeautifulSoup(

                response.text,

                "html.parser"
            )


            # ------------------------------------------------
            # EXTRACT PRODUCT LINKS
            # ------------------------------------------------

            # Shop HTML থেকে product URLs বের করছি।
            links = extract_product_links(
                shop_soup
            )


            # কতগুলো product link পাওয়া গেছে।
            print(
                f"Products found on page: "
                f"{len(links)}"
            )


            # সব URLs master set-এ যোগ করছি।
            #
            # set duplicate automatically remove করবে।
            product_urls.update(
                links
            )


            # পরের request-এর আগে delay।
            time.sleep(
                REQUEST_DELAY
            )


        # ====================================================
        # PRODUCT URL SUMMARY
        # ====================================================

        print()

        print(
            "=" * 60
        )

        print(
            "Total unique product URLs: "
            f"{len(product_urls)}"
        )

        print(
            "=" * 60
        )


        # ====================================================
        # STEP 2
        # VISIT INDIVIDUAL PRODUCT PAGES
        # ====================================================

        # sorted(product_urls)
        #
        # URLs alphabetically sorted করবে।
        #
        # enumerate(..., start=1)
        #
        # প্রতিটি product-কে একটি number দেবে:
        #
        # [1/20]
        # [2/20]
        # [3/20]
        # ...
        for index, product_url in enumerate(

            sorted(product_urls),

            start=1
        ):


            print()

            print(
                f"[{index}/"
                f"{len(product_urls)}] "
                f"Scraping product"
            )

            print(
                product_url
            )


            # ------------------------------------------------
            # FETCH PRODUCT PAGE
            # ------------------------------------------------

            try:

                # Individual product page fetch করছি।
                response = client.get(
                    product_url
                )


                # HTTP error হলে exception হবে।
                response.raise_for_status()


            except httpx.HTTPError as error:

                print(
                    f"Could not fetch "
                    f"product: {error}"
                )

                # Problematic product skip করছি।
                continue


            # ------------------------------------------------
            # PARSE PRODUCT HTML
            # ------------------------------------------------

            # Product page-এর HTML BeautifulSoup দিয়ে parse।
            product_soup = BeautifulSoup(

                response.text,

                "html.parser"
            )


            # ------------------------------------------------
            # EXTRACT PRODUCT DATA
            # ------------------------------------------------

            # আমাদের extract_product() function:
            #
            # HTML
            #  ↓
            # Product dictionary
            #
            product = extract_product(

                product_soup,

                product_url
            )


            # Final products list-এ product যোগ করছি।
            products.append(
                product
            )


            # ------------------------------------------------
            # SHOW BASIC INFORMATION
            # ------------------------------------------------

            print(
                f"Product: "
                f"{product['name']}"
            )

            print(
                f"Price: "
                f"{product['price']}"
            )

            print(
                f"SKU: "
                f"{product['sku']}"
            )


            # পরের product request-এর আগে delay।
            time.sleep(
                REQUEST_DELAY
            )


    # সব scraped products return করছি।
    return products


# ============================================================
# SAVE PRODUCTS FUNCTION
# ============================================================

def save_products(
    products: list[dict]
) -> None:
    """
    Scraped products JSON file-এ save করে।
    """


    # --------------------------------------------------------
    # CREATE OUTPUT DIRECTORY
    # --------------------------------------------------------

    # data/raw/ folder না থাকলে automatically create করবে।
    #
    # parents=True:
    # প্রয়োজন হলে parent directories-ও তৈরি করবে।
    #
    # exist_ok=True:
    # folder already থাকলেও error দেবে না।
    OUTPUT_FILE.parent.mkdir(

        parents=True,

        exist_ok=True
    )


    # --------------------------------------------------------
    # OPEN JSON FILE
    # --------------------------------------------------------

    # File write mode-এ open করছি।
    #
    # encoding="utf-8"
    # Bengali, emoji, special characters ইত্যাদি
    # correctly save করার জন্য।
    with OUTPUT_FILE.open(

        "w",

        encoding="utf-8"

    ) as file:


        # ----------------------------------------------------
        # CONVERT PYTHON DATA → JSON
        # ----------------------------------------------------

        json.dump(

            products,

            file,

            # JSON সুন্দরভাবে readable করার জন্য।
            indent=4,

            # Non-English characters escape না করে
            # সরাসরি রাখবে।
            ensure_ascii=False
        )


    # --------------------------------------------------------
    # FINAL LOG
    # --------------------------------------------------------

    print()

    print(
        "=" * 60
    )

    print(
        "SCRAPING COMPLETED"
    )

    print(
        "=" * 60
    )

    print(
        f"Products saved: "
        f"{len(products)}"
    )

    print(
        f"Output file: "
        f"{OUTPUT_FILE}"
    )


# ============================================================
# ENTRY POINT
# ============================================================

# Python file directly run করলে:
#
# __name__ == "__main__"
#
# True হবে।
#
# তখন নিচের code execute হবে।
#
# অন্য কোনো Python file থেকে এই file import করলে
# এই অংশ automatically execute হবে না।
if __name__ == "__main__":


    # --------------------------------------------------------
    # STEP 1
    # SCRAPE PRODUCTS
    # --------------------------------------------------------

    products = scrape_products()


    # --------------------------------------------------------
    # STEP 2
    # SAVE PRODUCTS
    # --------------------------------------------------------

    save_products(
        products
    )