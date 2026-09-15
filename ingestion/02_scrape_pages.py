import json
import time
from pathlib import Path

import httpx
from bs4 import BeautifulSoup


BASE_URL = "https://zyraluxe.in"
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
    "return_policy": "/return-policy/",
    "privacy_policy": "/privacy-policy/",
}


def clean_text(text: str | None) -> str:
    if not text:
        return ""

    return " ".join(text.split())


def extract_page_content(
    soup: BeautifulSoup
) -> tuple[str | None, str]:

    title_element = soup.find("h1")

    if not title_element:
        return None, ""

    title = clean_text(
        title_element.get_text(" ", strip=True)
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
        ".sidebar",
        ".widget",
        ".woocommerce-breadcrumb",
        ".comments-area",
        ".related",
    ]

    for selector in unwanted_selectors:
        for element in soup.select(selector):
            element.decompose()

    content_parts = []

    current = title_element.find_next()

    while current:

        if current.name in ["h1", "h2", "h3", "h4", "p", "li"]:

            text = clean_text(
                current.get_text(" ", strip=True)
            )

            if text:
                content_parts.append(text)

        current = current.find_next()

        if len(content_parts) >= 100:
            break

    content = " ".join(content_parts)

    footer_markers = [
        "Follow Us On",
        "More Info Track Order",
        "© 2026 Zyraluxe",
    ]

    for marker in footer_markers:
        if marker in content:
            content = content.split(marker)[0]

    content = clean_text(content)

    return title, content



def scrape_pages() -> list[dict]:

    pages = []

    with httpx.Client(
        headers=HEADERS,
        timeout=20.0,
        follow_redirects=True,
    ) as client:

        for page_type, page_path in KNOWLEDGE_PAGES.items():

            page_url = f"{BASE_URL}{page_path}"

            print()
            print("=" * 60)
            print(f"Scraping: {page_type}")
            print(page_url)
            print("=" * 60)

            try:
                response = client.get(page_url)

                print(
                    f"HTTP Status: {response.status_code}"
                )

                response.raise_for_status()

            except httpx.HTTPError as error:

                print(
                    f"Could not fetch page: {error}"
                )

                continue

            soup = BeautifulSoup(
                response.text,
                "html.parser"
            )

            title, content = extract_page_content(
                soup
            )

            if not content:
                print("WARNING: No useful content found.")
                continue

            page = {
                "page_type": page_type,
                "title": title,
                "url": page_url,
                "content": content,
            }

            pages.append(page)

            print(f"Title: {title}")
            print(
                f"Characters extracted: "
                f"{len(content)}"
            )

            print(
                f"Preview: "
                f"{content[:500]}..."
            )

            time.sleep(REQUEST_DELAY)

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
    print("PAGE SCRAPING COMPLETED")
    print("=" * 60)

    print(f"Pages saved: {len(pages)}")
    print(f"Output file: {OUTPUT_FILE}")


if __name__ == "__main__":

    pages = scrape_pages()

    save_pages(pages)