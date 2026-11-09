import time

import requests
from bs4 import BeautifulSoup
from rich.console import Console

console = Console()

HEADERS = {
    "User-Agent": "is310-course/1.0 (https://fiannasullivan.github.io; fqs2@illinois.edu)"
}

FANDOM_API_URL = "https://harrypotter.fandom.com/api.php"

response = requests.get(FANDOM_API_URL, params={
    "action": "query",
    "list": "categorymembers",
    "cmtitle": "Category:Gryffindors",
    "cmtype": "page",
    "cmlimit": "max",
    "format": "json",
}, headers=HEADERS, timeout=15)

console.print(response.status_code)
if response.status_code == 200:
    data = response.json()
    if "error" in data:
        console.print(f"API error: {data['error']['info']}")
    else:
        for page in data["query"]["categorymembers"]:
            console.print(page["title"])


import json
from urllib.parse import unquote

POTTERDB_URL = "https://api.potterdb.com/v1/characters"
SEARCHES = ["Hermione", "Ginny", "Neville", "Harry Potter"]

saved_characters = []

for search in SEARCHES:
    time.sleep(1)
    response = requests.get(POTTERDB_URL, params={"filter[name_cont]": search},
                            headers=HEADERS, timeout=15)
    if response.status_code != 200:
        console.print(f"PotterDB failed for {search}: {response.status_code}")
        continue

    matches = response.json()["data"]
    console.print(f"\n[bold]{search}[/bold]: {len(matches)} match(es) in PotterDB")
    if not matches:
        continue

    attributes = matches[0]["attributes"]
    wiki_url = attributes.get("wiki")
    if not wiki_url:
        console.print("No wiki link in PotterDB record")
        continue

    # Look up the same character on the Fandom wiki
    wiki_title = unquote(wiki_url.split("/wiki/")[1])
    time.sleep(1)
    wiki_response = requests.get(FANDOM_API_URL, params={
        "action": "parse",
        "page": wiki_title,
        "prop": "langlinks|categories",
        "format": "json",
    }, headers=HEADERS, timeout=15)

    if wiki_response.status_code != 200:
        console.print(f"Fandom failed for {wiki_title}: {wiki_response.status_code}")
        continue
    wiki_data = wiki_response.json()
    if "error" in wiki_data:
        console.print(f"Fandom error for {wiki_title}: {wiki_data['error']['info']}")
        continue

    langlinks = wiki_data["parse"].get("langlinks", [])
    categories = [c["*"] for c in wiki_data["parse"].get("categories", [])]

    console.print("PotterDB name:", attributes["name"], "| house:", attributes.get("house"))
    console.print("Wiki title:", wiki_data["parse"]["title"])
    console.print("Language links:", len(langlinks))
    console.print("Gryffindor-related categories:", [c for c in categories if "Gryffindor" in c])

    saved_characters.append({
        "search": search,
        "potterdb_name": attributes["name"],
        "house": attributes.get("house"),
        "wiki_url": wiki_url,
        "wiki_title": wiki_data["parse"]["title"],
        "language_link_count": len(langlinks),
        "languages": [link["lang"] for link in langlinks],
    })

# ---- Save only the item data ----
with open("potterdb_characters.json", "w", encoding="utf-8") as f:
    json.dump(saved_characters, f, indent=2, ensure_ascii=False)
console.print(f"\nSaved {len(saved_characters)} characters to potterdb_characters.json")