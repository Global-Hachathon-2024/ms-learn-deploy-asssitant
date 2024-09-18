import sys

import requests
from bs4 import BeautifulSoup


def scrape_web_content(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        main_content = soup.find("main", {"id": "main"})
        if not main_content:
            print("Error: Could not find the main content on the page.")
            return ""

        content_text = extract_text_with_structure(main_content)
        content_text = skip_until_first_h1(content_text)

        return content_text

    except requests.RequestException as e:
        print(f"Error fetching content from {url}: {e}")
        sys.exit(1)

    except Exception as e:
        print(f"Error parsing content from {url}: {e}")
        sys.exit(1)


def extract_text_with_structure(element, level=0):
    text = ""
    for child in element.children:
        if child.name in ["h1", "h2", "h3", "h4", "h5", "h6"]:
            text += "\n" + "#" * (int(child.name[1]) + level) + " " + child.get_text(strip=True) + "\n"
        elif child.name == "p":
            text += "\n" + child.get_text(strip=True) + "\n"
        elif child.name == "ul":
            text += extract_list_items(child, level + 1)
        elif child.name == "ol":
            text += extract_list_items(child, level + 1, ordered=True)
        elif child.name:
            text += extract_text_with_structure(child, level)
        elif isinstance(child, str):
            text += child.strip()
    return text


def extract_list_items(element, level=0, ordered=False):
    text = ""
    for i, li in enumerate(element.find_all("li", recursive=False)):
        prefix = f"{i+1}. " if ordered else "- "
        text += "\n" + " " * (level * 2) + prefix + li.get_text(strip=True) + "\n"
        text += extract_text_with_structure(li, level + 1)
    return text


def skip_until_first_h1(content_text):
    if "#" in content_text:
        parts = content_text.split("\n")
        for i, part in enumerate(parts):
            if part.startswith("# "):
                return "\n".join(parts[i:])
    return content_text
