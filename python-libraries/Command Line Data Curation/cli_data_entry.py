"""Collect and save a small, curated album dataset in the terminal."""
# Import required Python modules.
import json
from pathlib import Path
# Import Rich modules for terminal output.
from rich.console import Console
from rich.table import Table

# Create a Rich console for output and define the output file path.
console = Console()
output_file = Path("curated_albums.json")

# These records give the user examples of the fields and the level of detail expected before they enter another album.
albums = [
    {
        "title": "Kind of Blue",
        "artist": "Miles Davis",
        "album_year": 1959,
        "curator_note": "Built on scales instead of fast chord changes, which gave soloists more room to improvise.",
    },
    {
        "title": "A Love Supreme",
        "artist": "John Coltrane",
        "album_year": 1965,
        "curator_note": "A four-part suite Coltrane framed as a personal statement of faith and gratitude.",
    },
]


def display_albums(album_records):
    """Display the current album records as a Rich table."""
    # Create a Rich table with columns for title, artist, year, genre, and curator note.
    table = Table(title="Curated Albums")
    table.add_column("Title", style="magenta")
    table.add_column("Year", style="cyan")
    table.add_column("artist", style="green")
    table.add_column("Curator Note")
    # Add each album record to the table.
    for album in album_records:
        table.add_row(
            album["title"],
            str(album["album_year"]),
            album["artist"],
            album["curator_note"],
        )

    console.print(table)


def collect_album():
    """Collect and return one album record."""

    # Ask the user to enter a value for each field in the album record.
    title = console.input("[bold]Album title:[/bold] ").strip()
    album_year = console.input("[bold]Album year:[/bold] ").strip()
    artist = console.input("[bold]Artist:[/bold] ").strip()
    curator_note = console.input(
        "[bold]What makes this album culturally interesting?[/bold] "
    ).strip()

    album = {
        "title": title,
        "album_year": int(album_year),
        "artist": artist,
        "curator_note": curator_note,
    }

    return album


def review_album(album):
    """Display one album and return whether the user confirms it."""
	# Display the album record and ask the user to confirm it.
    console.print("\n[bold cyan]Please review your entry:[/bold cyan]")
    display_albums([album])
    confirmation = console.input("Is this correct? Enter yes or no: ").strip().lower()
    return confirmation in ["yes", "y"]


console.print("[bold cyan]Current example data:[/bold cyan]")
display_albums(albums)

# A for loop lets the user enter two records. The user can confirm or reject each entry, and they have one chance to replace an incorrect entry.
for entry_number in range(2):
    console.print(f"\n[bold cyan]Add album {entry_number + 1} of 2[/bold cyan]")
    new_album = collect_album()
    confirmed = review_album(new_album)

    # If the first entry is incorrect, give the user one chance to replace it.
    if confirmed is False:
        console.print("[yellow]Let's enter the album again.[/yellow]\n")
        new_album = collect_album()
        confirmed = review_album(new_album)

    # Only add a record to the dataset after the user confirms it.
    if confirmed:
        albums.append(new_album)
        console.print("[green]Album added.[/green]")
    else:
        console.print("[yellow]This album will not be saved.[/yellow]")

# json.dumps() turns the list of dictionaries into formatted JSON text.
output_file.write_text(json.dumps(albums, indent=4), encoding="utf-8")

console.print("\n[bold green]Your album data has been saved.[/bold green]")
# Provide a clickable link to the saved file in the terminal.
console.print(f"File saved at {output_file.resolve()}")