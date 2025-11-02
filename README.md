# Manga Tracker CLI
 (no, im not going to properly markdown my markdown. cry)
A simple, non stable, and user-friendly command-line manga viewer for MangaDex!

Search, track, and read manga directly in your terminal
images can save locally, view them later!
Read chapters as ASCII art if you prefer.

Works on Windows, Linux, anything that runs Python..

Automatically tracks your reading progress (thanks mangadex..)

Features

Search manga: type a query, select from numbered results

Track manga: keep track of which chapters you’ve read

Read manga in terminal: ASCII art panels, easy navigation (Enter next, b back, q quit)

Stable for Windows CMD: medium-detail ASCII, no broken images

Auto-mark chapters as read after reading

Make sure you have Python 3.9+ and pip installed

Install dependencies:

pip install -r requirements.txt

Usage
Search and read manga
python main.py search "anime name"


Choose the manga by number

Track it if you want (y/n)

Start reading from the first chapter (y/n)

Read navigation
Enter → next page
b → previous page
q → quit reading

Track manga

When you search and select a manga, choose to track it. This saves your read chapters to manga_data.json.

Notes
- Works best in terminals with 80+ columns
- Some chapters may be region-restricted on MangaDex
- ASCII rendering uses grayscale, medium-detail for CMD stability

Optional todo
- High-detail ASCII or colored CMD rendering (experimental)
- Add list_tracked, updates, or chapters commands
- Support reading from the latest chapter automatically

License
MIT License – feel free to use and modify <3
