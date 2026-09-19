"""
Core logic for the File Organizer project.

This module is intentionally kept simple and dependency-free (only the
Python standard library is used) so it's easy to read for beginners and
easy to run anywhere without installing anything.
"""

from __future__ import annotations

import json
import logging
import shutil
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

logger = logging.getLogger("file_organizer")

# Maps a "category" name to the list of file extensions that belong to it.
# Feel free to add more extensions or categories here.
CATEGORY_MAP: dict[str, list[str]] = {
    "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp", ".heic"],
    "Documents": [".pdf", ".doc", ".docx", ".txt", ".md", ".xlsx", ".csv", ".pptx"],
    "Videos": [".mp4", ".mov", ".avi", ".mkv", ".webm", ".flv"],
    "Audio": [".mp3", ".wav", ".flac", ".aac", ".m4a"],
    "Archives": [".zip", ".rar", ".7z", ".tar", ".gz"],
    "Code": [".py", ".js", ".html", ".css", ".java", ".cpp", ".c", ".json", ".sh"],
}

DEFAULT_CATEGORY = "Others"

# Name of the file we write after each run so `--undo` can reverse it.
LOG_FILE_NAME = ".file_organizer_log.json"


def get_category(extension: str, category_map: dict[str, list[str]] | None = None) -> str:
    """Return the category name for a given file extension.

    Args:
        extension: The file extension, e.g. ".jpg" (case-insensitive).
        category_map: Optional custom mapping to use instead of the default.

    Returns:
        The matching category name, or DEFAULT_CATEGORY if none match.
    """
    category_map = category_map or CATEGORY_MAP
    extension = extension.lower()
    for category, extensions in category_map.items():
        if extension in extensions:
            return category
    return DEFAULT_CATEGORY


@dataclass
class OrganizeResult:
    """Summary of what happened (or would happen) during an organize run."""

    moves: list[tuple[str, str]] = field(default_factory=list)  # (source, destination)
    skipped: list[str] = field(default_factory=list)

    @property
    def moved_count(self) -> int:
        return len(self.moves)


def organize_directory(
    source_dir: str | Path,
    dry_run: bool = False,
    category_map: dict[str, list[str]] | None = None,
) -> OrganizeResult:
    """Organize every file in `source_dir` into category subfolders.

    Args:
        source_dir: The folder to clean up.
        dry_run: If True, only report what *would* happen; don't move anything.
        category_map: Optional custom extension-to-category mapping.

    Returns:
        An OrganizeResult describing every move that happened (or would happen).
    """
    source_path = Path(source_dir).expanduser().resolve()
    if not source_path.is_dir():
        raise NotADirectoryError(f"{source_path} is not a valid directory")

    result = OrganizeResult()

    for item in sorted(source_path.iterdir()):
        # Skip subfolders, hidden files, and our own log file.
        if item.is_dir() or item.name.startswith(".") or item.name == LOG_FILE_NAME:
            result.skipped.append(str(item))
            continue

        category = get_category(item.suffix, category_map)
        destination_folder = source_path / category
        destination_path = destination_folder / item.name

        # Avoid overwriting a file that already exists at the destination.
        destination_path = _resolve_name_conflict(destination_path)

        result.moves.append((str(item), str(destination_path)))

        if not dry_run:
            destination_folder.mkdir(exist_ok=True)
            shutil.move(str(item), str(destination_path))
            logger.info("Moved %s -> %s", item.name, destination_path.relative_to(source_path))
        else:
            logger.info("[DRY RUN] Would move %s -> %s", item.name, destination_path.relative_to(source_path))

    if not dry_run and result.moves:
        _write_run_log(source_path, result.moves)

    return result


def _resolve_name_conflict(destination_path: Path) -> Path:
    """If destination_path already exists, append ' (1)', ' (2)', etc."""
    if not destination_path.exists():
        return destination_path

    stem, suffix, parent = destination_path.stem, destination_path.suffix, destination_path.parent
    counter = 1
    new_path = destination_path
    while new_path.exists():
        new_path = parent / f"{stem} ({counter}){suffix}"
        counter += 1
    return new_path


def _write_run_log(source_path: Path, moves: list[tuple[str, str]]) -> None:
    """Persist the moves made during a run so they can be undone later."""
    log_path = source_path / LOG_FILE_NAME
    existing: list[dict] = []
    if log_path.exists():
        try:
            existing = json.loads(log_path.read_text())
        except (json.JSONDecodeError, OSError):
            existing = []

    existing.append(
        {
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "moves": moves,
        }
    )
    log_path.write_text(json.dumps(existing, indent=2))


def undo_last_run(source_dir: str | Path) -> OrganizeResult:
    """Reverse the most recent organize run in `source_dir`.

    Returns:
        An OrganizeResult listing the files that were moved back.

    Raises:
        FileNotFoundError: If there is no run log to undo.
    """
    source_path = Path(source_dir).expanduser().resolve()
    log_path = source_path / LOG_FILE_NAME

    if not log_path.exists():
        raise FileNotFoundError("No previous run found to undo.")

    runs = json.loads(log_path.read_text())
    if not runs:
        raise FileNotFoundError("No previous run found to undo.")

    last_run = runs.pop()
    result = OrganizeResult()

    for original, moved_to in reversed(last_run["moves"]):
        moved_to_path = Path(moved_to)
        original_path = Path(original)
        if moved_to_path.exists():
            original_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(moved_to_path), str(original_path))
            result.moves.append((moved_to, original))
            logger.info("Restored %s", original_path.name)
        else:
            result.skipped.append(moved_to)

    # Save the log back with the undone run removed.
    log_path.write_text(json.dumps(runs, indent=2))

    return result
