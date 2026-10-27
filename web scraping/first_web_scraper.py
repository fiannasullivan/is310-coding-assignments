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
RESULTS_OUTPUT = "bulbapedia_results.csv"

console = Console()

HEADERS = {"User-Agent": "is310-course-scraper/1.0 (student project; fqs2@illinois.edu)"}

def main():
    console.print("[cyan]Finding Generation 1 Pokemon...[/cyan]")
    generation1_page = fetch_soup(GENERATION1_URL)
    generation1_pokemon = scrape_pokemon(
        generation1_page,
        GENERATION1_URL,
    )

    console.print("[cyan]Finding Generation 8 Pokemon...[/cyan]")
    generation8_page = fetch_soup(GENERATION8_URL)
    generation8_pokemon = scrape_pokemon(
        generation8_page,
        GENERATION8_URL,
    )

    all_pokemon = generation1_pokemon + generation8_pokemon
    console.print(f"[green]Found {len(all_pokemon)} Pokemon.[/green]")

    results = []
    for number, pokemon in enumerate(all_pokemon, start=1):
        console.print(f"Processing {number}/{len(all_pokemon)}: {pokemon['name']}")
        results.append(analyze_pokemon(pokemon))

    print_results_table(results)
    RESULTS_OUTPUT = "bulbapedia_results.csv"
    save_csv(results, RESULTS_OUTPUT)
    console.print(f"[green]Saved {len(results)} analyzed Pokemon to {RESULTS_OUTPUT}[/green]")


def scrape_pokemon(list_page):
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

        if kdex > 151 or kdex in seen:
            continue  

        
        link = cells[2].find("a", href=True)
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