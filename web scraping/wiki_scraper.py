import requests
from bs4 import BeautifulSoup
import csv
import time
from rich.console import Console
from rich.table import Table
console = Console()
table = Table()

BASE_URL = "https://bulbapedia.bulbagarden.net"
GENERATION1_URL = f"{BASE_URL}/wiki/List_of_Pok%C3%A9mon_by_Kanto_Pok%C3%A9dex_number"
GENERATION8_URL = f"{BASE_URL}/wiki/List_of_Pok%C3%A9mon_by_National_Pok%C3%A9dex_number"
HEADERS = {
    "User-Agent": "is310-course-scraper/1.0 (student project; fqs2@illinois.edu)"
}
REQUEST_DELAY = 5
RESULTS_OUTPUT = "web scraping/bulbapedia_results.csv"

def fetch_soup(url):
    if not url:
        console.print("[yellow]No URL was found for this page.[/yellow]")
        return None

    response = requests.get(url, headers=HEADERS, timeout=30)
    time.sleep(REQUEST_DELAY)

    if response.status_code != 200:
        console.print(f"[red]Could not download {url}: HTTP {response.status_code}[/red]")
        return None

    return BeautifulSoup(response.text, "html.parser")


def get_internal_links(content):
    if content is None:
        return []

    links = []
    for link in content.find_all("a", href=True):
        href = link["href"]
        if href.startswith("/wiki/") and "#" not in href:
            links.append(href)

    return links


def analyze_pokemon(pokemon):
    soup = fetch_soup(pokemon["pokemon_url"])
    record = pokemon.copy()
    record["generation"] = 1 if pokemon["kdex"] <= 151 else 8
    record["word_count"] = 0
    record["character_count"] = 0
    record["internal_link_count"] = 0
    record["unique_internal_link_count"] = 0

    if soup is None:
        return record

    content = soup.select_one("#mw-content-text .mw-parser-output")
    if content is None:
        return record

    article_text = content.get_text(" ", strip=True)
    internal_links = get_internal_links(content)
    unique_internal_links = []
    for href in internal_links:
        if href not in unique_internal_links:
            unique_internal_links.append(href)

    record["word_count"] = len(article_text.split())
    record["character_count"] = len(article_text)
    record["internal_link_count"] = len(internal_links)
    record["unique_internal_link_count"] = len(unique_internal_links)
    return record


def save_csv(records, output_path):
    if not records:
        console.print(f"[yellow]No records to save to {output_path}[/yellow]")
        return

    with open(output_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=records[0].keys())
        writer.writeheader()
        writer.writerows(records)


def print_results_table(records):
    table = Table(title="Generation 1 vs. Generation 8 Pokémon Pages")
    table.add_column("Pokémon", style="cyan")
    table.add_column("Gen", style="green")
    table.add_column("Words", justify="right")
    table.add_column("Characters", justify="right")
    table.add_column("All Links", justify="right")
    table.add_column("Unique Links", justify="right")

    for record in sorted(records, key=lambda record: record["word_count"], reverse=True):
        table.add_row(
            record["name"],
            str(record["generation"]),
            str(record["word_count"]),
            str(record["character_count"]),
            str(record["internal_link_count"]),
            str(record["unique_internal_link_count"]),
        )

    console.print(table)
    
def main():
    console.print("[cyan]Finding Generation 1 Pokemon...[/cyan]")
    generation1_page = fetch_soup(GENERATION1_URL)
    generation1_pokemon = scrape_pokemon(generation1_page, 1, 151
    )

    console.print("[cyan]Finding Generation 8 Pokemon...[/cyan]")
    generation8_page = fetch_soup(GENERATION8_URL)
    generation8_pokemon = scrape_pokemon(generation8_page, 810, 905
    )
    console.print(f"Gen 1: {len(generation1_pokemon)}, first {generation1_pokemon[0]['name']}, last {generation1_pokemon[-1]['name']}")
    console.print(f"Gen 8: {len(generation8_pokemon)}, first {generation8_pokemon[0]['name']}, last {generation8_pokemon[-1]['name']}")
    all_pokemon = generation1_pokemon + generation8_pokemon
    console.print(f"[green]Found {len(all_pokemon)} Pokemon.[/green]")

    results = []
    for number, pokemon in enumerate(all_pokemon, start=1):
        console.print(f"Processing {number}/{len(all_pokemon)}: {pokemon['name']}")
        results.append(analyze_pokemon(pokemon))

    print_results_table(results)
    save_csv(results, RESULTS_OUTPUT)
    console.print(f"[green]Saved {len(results)} analyzed Pokemon to {RESULTS_OUTPUT}[/green]")


def scrape_pokemon(list_page, first, last):
    pokemon_list = []
    seen = set()
    if list_page is None:
        return pokemon_list

    for row in list_page.find_all("tr"):
        cells = row.find_all("td")
        if not cells:
            continue  

        kdex_text = cells[0].get_text(strip=True)  
        try:
            kdex = int(kdex_text.lstrip("#"))
        except ValueError:
            continue  

        if kdex < first or kdex > last or kdex in seen:
            continue  

        
        link = None
        for a in row.find_all("a", href=True):
            if a["href"].endswith("_(Pok%C3%A9mon)") and a.get_text(strip=True):
                link = a
                break
        if link is None:
            continue

        seen.add(kdex)
        pokemon_list.append({
            "kdex": kdex,
            "name": link.get_text(strip=True),
            "pokemon_url": f"{BASE_URL}{link['href']}",
        })

    return pokemon_list

if __name__ == "__main__":
    main()