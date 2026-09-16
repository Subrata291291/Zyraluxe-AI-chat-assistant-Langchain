import json
import time
from pathlib import Path

import httpx
from bs4 import BeautifulSoup


BASE_URL = "https://zyraluxe.in"
WP_API_URL = f"{BASE_URL}/wp-json/wp/v2/pages"

OUTPUT_FILE = Path("data/raw/pages_raw.json")
REQUEST_DELAY = 1.0

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/140.0.0.0 Safari/537.36"
    )
}

KNOWLEDGE_PAGES = {
    "return_policy": "return-policy",
    "privacy_policy": "privacy-policy",
}


def clean_text(text: str | None) -> str:
    if not text:
        return ""

    return " ".join(text.split())


def extract_content(html: str) -> str:
    soup = BeautifulSoup(
        html,
        "html.parser"
    )

    unwanted_selectors = [
        "script",
        "style",
        "nav",
        "header",
        "footer",
        "aside",
        "form",
        "button",
        "input",
        "select",
        "textarea",
        ".site-header",
        ".site-footer",
        ".navigation",
        ".menu",
        ".main-navigation",
        ".sidebar",
        ".widget",
        ".woocommerce-breadcrumb",
        ".comments-area",
        ".related",
        ".site-branding",
        ".top-bar",
        ".mobile-menu",
        ".offcanvas",
        ".account",
        ".wishlist",
        ".cart",
        ".woocommerce-products-header",
        ".products",
        ".product",
        ".shop-sidebar",
    ]

    for selector in unwanted_selectors:
        for element in soup.select(selector):
            element.decompose()

    content_container = (
        soup.select_one("main")
        or soup.select_one("article")
        or soup.select_one(".entry-content")
        or soup.select_one(".page-content")
        or soup.select_one(".content-area")
        or soup.select_one(".elementor-widget-theme-post-content")
        or soup.select_one(".elementor-location-single")
        or soup.body
    )

    if not content_container:
        return ""

    content_parts = []

    for element in content_container.find_all(
        ["h1", "h2", "h3", "h4", "p", "li"]
    ):
        text = clean_text(
            element.get_text(" ", strip=True)
        )

        if not text:
            continue

        navigation_text = [
            "shop",
            "login",
            "my account",
            "track order",
            "wishlist",
            "home",
            "bangles",
            "bracelets",
            "chokker",
            "combo",
            "earrings",
            "necklace",
            "oxidised jhumka",
            "pendents",
            "sitahar",
            "anklets",
        ]

        if text.lower() in navigation_text:
            continue

        content_parts.append(text)

    content = " ".join(content_parts)

    footer_markers = [
        "Follow Us On",
        "More Info Track Order",
        "© 2026 Zyraluxe",
        "© 2025 Zyraluxe",
    ]

    for marker in footer_markers:
        if marker in content:
            content = content.split(marker)[0]

    return clean_text(content)

def fetch_page(
    client: httpx.Client,
    page_type: str,
    slug: str
) -> dict | None:

    print()
    print("=" * 60)
    print(f"Fetching: {page_type}")
    print(f"Slug: {slug}")
    print("=" * 60)

    params = {
        "slug": slug,
        "status": "publish",
        "per_page": 1,
    }

    try:
        response = client.get(
            WP_API_URL,
            params=params
        )

        print(
            f"WordPress API Status: "
            f"{response.status_code}"
        )

        response.raise_for_status()

    except httpx.HTTPError as error:
        print(
            f"Could not fetch WordPress data: "
            f"{error}"
        )
        return None

    pages = response.json()

    if not pages:
        print("WARNING: Page not found.")
        return None

    wp_page = pages[0]

    title = clean_text(
        wp_page.get("title", {}).get("rendered")
    )

    page_url = wp_page.get("link")

    content_html = (
        wp_page.get("content", {})
        .get("rendered", "")
    )

    content = ""

    if content_html:
        content = extract_content(
            content_html
        )

        print(
            "Content source: "
            "WordPress REST API"
        )

    if not content and page_url:

        print(
            "REST API content empty."
        )

        print(
            "Falling back to actual page..."
        )

        try:
            page_response = client.get(
                page_url
            )

            print(
                f"Website Status: "
                f"{page_response.status_code}"
            )

            page_response.raise_for_status()

            content = extract_content(
                page_response.text
            )

            print(
                "Content source: "
                "Website HTML"
            )

        except httpx.HTTPError as error:

            print(
                f"Could not fetch website page: "
                f"{error}"
            )

            return None

    if not content:

        print(
            "WARNING: No useful content found."
        )

        return None

    page = {
        "page_id": wp_page.get("id"),
        "page_type": page_type,
        "slug": wp_page.get("slug"),
        "title": title,
        "url": page_url,
        "modified": wp_page.get("modified"),
        "modified_gmt": wp_page.get("modified_gmt"),
        "content": content,
    }

    print(
        f"Page ID: {page['page_id']}"
    )

    print(
        f"Title: {page['title']}"
    )

    print(
        f"URL: {page['url']}"
    )

    print(
        f"Modified: {page['modified']}"
    )

    print(
        f"Characters extracted: "
        f"{len(content)}"
    )

    print(
        f"Preview: "
        f"{content[:500]}..."
    )

    return page


def scrape_pages() -> list[dict]:

    pages = []

    with httpx.Client(
        headers=HEADERS,
        timeout=20.0,
        follow_redirects=True,
    ) as client:

        for page_type, slug in KNOWLEDGE_PAGES.items():

            page = fetch_page(
                client,
                page_type,
                slug
            )

            if page:
                pages.append(page)

            time.sleep(
                REQUEST_DELAY
            )

    return pages


def save_pages(
    pages: list[dict]
) -> None:

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with OUTPUT_FILE.open(
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            pages,
            file,
            indent=4,
            ensure_ascii=False
        )

    print()
    print("=" * 60)
    print("WORDPRESS PAGE SCRAPING COMPLETED")
    print("=" * 60)

    print(
        f"Pages saved: {len(pages)}"
    )

    print(
        f"Output file: {OUTPUT_FILE}"
    )


if __name__ == "__main__":

    pages = scrape_pages()

    save_pages(pages)