# 🗂️ File Organizer

A simple Python command-line tool that automatically tidies up a messy
folder (like your Downloads folder!) by sorting files into subfolders
based on their type — Images, Documents, Videos, Audio, Archives, Code,
and Others.

Built with **zero external dependencies** — just the Python standard
library — so it's easy to read, run, and learn from.

## Features

- 📁 Sorts files into category subfolders automatically
- 👀 `--dry-run` mode to preview changes before anything moves
- ↩️ `--undo` to instantly reverse the last run
- ⚠️ Automatically renames files instead of overwriting on conflicts
- ✅ Fully unit tested

## Demo

```
$ python main.py ~/Downloads --dry-run
[DRY RUN] Would move photo.jpg -> Images/photo.jpg
[DRY RUN] Would move resume.pdf -> Documents/resume.pdf
[DRY RUN] Would move song.mp3 -> Audio/song.mp3

Would move 3 file(s). Skipped 0 item(s).

$ python main.py ~/Downloads
Moved photo.jpg -> Images/photo.jpg
Moved resume.pdf -> Documents/resume.pdf
Moved song.mp3 -> Audio/song.mp3

Moved 3 file(s). Skipped 0 item(s).
```

## Installation

No dependencies to install — just clone the repo:

```bash
git clone https://github.com/<your-username>/file-organizer.git
cd file-organizer
```

Requires **Python 3.10+**.

## Usage

```bash
# Preview what would happen (recommended first step!)
python main.py /path/to/folder --dry-run

# Actually organize the folder
python main.py /path/to/folder

# Undo the most recent organize run
python main.py /path/to/folder --undo

# See detailed logging
python main.py /path/to/folder --verbose
```

## Project Structure

```
file-organizer/
├── main.py                    # Entry point (python main.py <folder>)
├── organizer/
│   ├── __init__.py
│   ├── organizer.py           # Core logic: categorizing, moving, undo
│   └── cli.py                 # Command-line argument handling
├── tests/
│   └── test_organizer.py      # Unit tests (unittest + tempfile)
├── requirements.txt
├── LICENSE
└── README.md
```

## Running Tests

```bash
python -m unittest discover tests -v
```

## How It Works

1. `organizer.py` maps file extensions to categories (see `CATEGORY_MAP`).
2. `organize_directory()` walks through the top-level files in a folder,
   figures out each file's category, and moves it into a matching
   subfolder (creating the subfolder if needed).
3. Every real run writes a small `.file_organizer_log.json` file
   recording what moved where, so `--undo` can put everything back.

## Customization

Want to add your own categories or extensions? Just edit the
`CATEGORY_MAP` dictionary at the top of `organizer/organizer.py`:

```python
CATEGORY_MAP = {
    "Images": [".jpg", ".jpeg", ".png", ...],
    "Design": [".psd", ".ai", ".sketch"],  # add your own!
    ...
}
```

## Ideas for Extending This Project

- Add a config file (YAML/JSON) so category rules don't require editing code
- Add a `--watch` mode that organizes a folder continuously in the background
- Build a small GUI with `tkinter`
- Sort by file date instead of (or in addition to) type

## License

MIT License — see [LICENSE](LICENSE) for details.
