#!/usr/bin/env python3
"""
Manga Tracker CLI - try image display
"""

import click
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
import requests
import json
import os
from datetime import datetime
from PIL import Image
import io
import subprocess
import platform
import webbrowser

console = Console()

class MangaTracker:
    def __init__(self):
        self.base_url = "https://api.mangadex.org"
        self.data_file = "manga_data.json"
        self.load_data()

    def can_display_images(self):
        """Check if we can display images natively"""
        try:
            import matplotlib.pyplot as plt
            return True
        except ImportError:
            return False

    def display_image_native(self, image_data, page_num):
        """Display image using matplotlib (highest quality)"""
        try:
            import matplotlib.pyplot as plt
            from io import BytesIO

            plt.figure(figsize=(12, 16))
            plt.imshow(image_data)
            plt.axis('off')
            plt.title(f"Page {page_num}")
            plt.tight_layout()
            plt.show()
            return True
        except Exception as e:
            console.print(f"[yellow]Native display failed: {e}[/yellow]")
            return False

    def display_image_terminal(self, image_path):
        """Display image in terminal using system capabilities"""
        system = platform.system()
        try:
            if system == "Darwin":  # mac
                subprocess.run(["open", image_path], check=True)
            elif system == "Windows":
                os.startfile(image_path)
            elif system == "Linux":
                for viewer in ["xdg-open", "feh", "display", "eog"]:
                    try:
                        subprocess.run([viewer, image_path], check=True)
                        return True
                    except (subprocess.CalledProcessError, FileNotFoundError):
                        continue
            return True
        except Exception as e:
            console.print(f"[yellow]Terminal display failed: {e}[/yellow]")
            return False

    def display_image_browser(self, image_url):
        """Open image in web browser"""
        try:
            webbrowser.open(image_url)
            return True
        except Exception as e:
            console.print(f"[yellow]Browser display failed: {e}[/yellow]")
            return False

    def load_data(self):
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r') as f:
                self.data = json.load(f)
        else:
            self.data = {"tracked_manga": {}, "last_check": None}

    def save_data(self):
        with open(self.data_file, 'w') as f:
            json.dump(self.data, f, indent=2)

    def search_manga(self, query, limit=10):
        url = f"{self.base_url}/manga"
        params = {"title": query, "limit": limit, "includes[]": ["cover_art", "author", "artist"]}
        try:
            resp = requests.get(url, params=params, timeout=10)
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as e:
            console.print(f"[red]Error searching manga: {e}[/red]")
            return None

    def get_manga_details(self, manga_id):
        url = f"{self.base_url}/manga/{manga_id}"
        params = {"includes[]": ["cover_art", "author", "artist"]}
        try:
            resp = requests.get(url, params=params, timeout=10)
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as e:
            console.print(f"[red]Error getting manga details: {e}[/red]")
            return None

    def get_chapters(self, manga_id, limit=100):
        url = f"{self.base_url}/manga/{manga_id}/feed"
        params = {"translatedLanguage[]": ["en"], "order[chapter]": "asc", "limit": limit}
        try:
            resp = requests.get(url, params=params, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            if not data.get('data'):
                params.pop("translatedLanguage[]")
                resp = requests.get(url, params=params, timeout=10)
                resp.raise_for_status()
                data = resp.json()
            return data
        except requests.RequestException as e:
            console.print(f"[red]Error fetching chapters: {e}[/red]")
            return None

    def get_chapter_pages(self, chapter_id):
        url = f"{self.base_url}/at-home/server/{chapter_id}"
        try:
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            base_url = data['baseUrl']
            chapter_hash = data['chapter']['hash']
            return [f"{base_url}/data/{chapter_hash}/{f}" for f in data['chapter']['data']]
        except requests.RequestException as e:
            console.print(f"[red]Error getting chapter pages: {e}[/red]")
            return None

    def image_to_ascii_enhanced(self, image, width=120):
        """Enhanced ASCII conversion with better character mapping"""
        try:
            import shutil
            terminal_width = shutil.get_terminal_size().columns
            width = min(int(terminal_width * 0.9), width)
        except:
            pass

        aspect_ratio = image.height / image.width
        new_height = int(width * aspect_ratio * 0.5)

        max_height = 80
        if new_height > max_height:
            new_height = max_height
            width = int(new_height / aspect_ratio / 0.5)

        image = image.resize((width, new_height), Image.Resampling.LANCZOS)
        image = image.convert('L')

        ascii_chars = ' .\'`^",:;Il!i~+?_][}{1)(|\\/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$'

        pixels = list(image.getdata())
        ascii_str = ''

        for i, pixel in enumerate(pixels):
            if i % width == 0 and i != 0:
                ascii_str += '\n'
            char_index = int(pixel / 255 * (len(ascii_chars) - 1))
            ascii_str += ascii_chars[char_index] * 2 

        return ascii_str

    def read_chapter_enhanced(self, manga_id, chapter_number, max_pages=5):
        """Enhanced reading with multiple display options"""
        chapters_data = self.get_chapters(manga_id)
        if not chapters_data or not chapters_data.get('data'):
            console.print("[red]No chapters found[/red]")
            return False

        target_chapter = None
        for ch in chapters_data['data']:
            if ch['attributes']['chapter'] and str(float(ch['attributes']['chapter'])) == str(chapter_number):
                target_chapter = ch
                break
        if not target_chapter:
            target_chapter = chapters_data['data'][0]

        pages = self.get_chapter_pages(target_chapter['id'])
        if not pages:
            console.print("[red]No pages available[/red]")
            return False

        console.print(f"[green]Reading chapter {chapter_number}[/green]")
        console.print("\n[yellow]Choose display method:[/yellow]")
        console.print("1. Native image display (requires matplotlib)")
        console.print("2. System image viewer")
        console.print("3. Web browser")
        console.print("4. ASCII art (fallback)")

        try:
            display_choice = input("Choose [1-4] (default: 1): ").strip() or "1"
        except (EOFError, KeyboardInterrupt):
            return False

        i = 0
        while i < min(max_pages, len(pages)):
            console.print(f"[yellow]Loading page {i+1}/{min(max_pages,len(pages))}...[/yellow]")

            try:
                resp = requests.get(pages[i], timeout=10)
                resp.raise_for_status()
                image_data = resp.content
                image = Image.open(io.BytesIO(image_data))

                display_success = False

                if display_choice == "1":
                    display_success = self.display_image_native(image, i+1)
                    if not display_success:
                        console.print("[yellow]Falling back to ASCII...[/yellow]")
                        display_choice = "4"

                if display_choice == "2":
                    temp_path = f"temp_page_{i+1}.png"
                    image.save(temp_path)
                    display_success = self.display_image_terminal(temp_path)
                    if display_success:
                        console.print(f"[green]Opened in system viewer. Close to continue...[/green]")
                    else:
                        console.print("[yellow]Falling back to ASCII...[/yellow]")
                        display_choice = "4"

                if display_choice == "3":
                    display_success = self.display_image_browser(pages[i])
                    if display_success:
                        console.print(f"[green]Opened in browser. Close tab to continue...[/green]")
                    else:
                        console.print("[yellow]Falling back to ASCII...[/yellow]")
                        display_choice = "4"

                if display_choice == "4" or not display_success:
                    ascii_art = self.image_to_ascii_enhanced(image, width=120)
                    console.clear()
                    console.print(Panel(Text(ascii_art, no_wrap=True), border_style="blue", title=f"Page {i+1}"))

                console.print("\n[yellow]Commands: [Enter] next, [b] back, [q] quit[/yellow]")
                user_input = input().strip().lower()
                if user_input == 'q':
                    break
                elif user_input == 'b' and i > 0:
                    i -= 1
                    continue
                else:
                    i += 1

            except Exception as e:
                console.print(f"[red]Failed to load page {i+1}: {e}[/red]")
                break

        # clean
        for j in range(len(pages)):
            temp_path = f"temp_page_{j+1}.png"
            if os.path.exists(temp_path):
                os.remove(temp_path)

        return True

    def track_manga(self, manga_id, title):
        if manga_id not in self.data['tracked_manga']:
            self.data['tracked_manga'][manga_id] = {"title": title, "read_chapters": [], "last_read": None, "total_chapters": 0}
            self.save_data()
            console.print(f"[green]Now tracking {title}[/green]")
        else:
            console.print(f"[yellow]Already tracking {title}[/yellow]")

    def mark_chapter_read(self, manga_id, chapter_number):
        if manga_id in self.data['tracked_manga']:
            if chapter_number not in self.data['tracked_manga'][manga_id]['read_chapters']:
                self.data['tracked_manga'][manga_id]['read_chapters'].append(chapter_number)
                self.data['tracked_manga'][manga_id]['last_read'] = datetime.now().isoformat()
                self.save_data()

@click.group()
def cli():
    pass

@cli.command()
@click.argument('query')
@click.option('--limit', default=10)
def search(query, limit):
    tracker = MangaTracker()
    results = tracker.search_manga(query, limit)
    if not results or not results.get('data'):
        console.print("[red]No results found[/red]")
        return
    for idx, m in enumerate(results['data'], 1):
        title = m['attributes']['title'].get('en','Unknown')
        tags = ", ".join([t['attributes']['name']['en'] for t in m['attributes']['tags'][:3]])
        console.print(f"{idx}. {title} Tags: {tags}")
    while True:
        choice = input("Pick manga (number, q to quit): ").strip()
        if choice.lower() == 'q': return
        if not choice.isdigit() or not (1 <= int(choice) <= len(results['data'])):
            console.print("[yellow]Invalid choice[/yellow]"); continue
        break
    idx = int(choice)-1
    selected = results['data'][idx]
    manga_id = selected['id']
    title = selected['attributes']['title'].get('en','Unknown')
    track = input("Track manga? (y/n): ").strip().lower() == 'y'
    if track: tracker.track_manga(manga_id, title)
    read_now = input("Start reading from first chapter? (y/n): ").strip().lower() == 'y'
    if not read_now: return
    chapters_data = tracker.get_chapters(manga_id)
    if not chapters_data or not chapters_data.get('data'): return
    first_chapter = chapters_data['data'][0]['attributes']['chapter'] or 1
    tracker.read_chapter_enhanced(manga_id, first_chapter, max_pages=5)
    tracker.mark_chapter_read(manga_id, first_chapter)

if __name__ == '__main__':
    cli()

