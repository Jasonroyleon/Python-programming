"""Command-line interface for the File Organizer."""

from __future__ import annotations

import argparse
import logging
import sys

from organizer.organizer import organize_directory, undo_last_run


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="file-organizer",
        description="Sort the files in a messy folder into tidy subfolders by type.",
    )
    parser.add_argument(
        "directory",
        help="Path to the folder you want to organize.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would happen without actually moving any files.",
    )
    parser.add_argument(
        "--undo",
        action="store_true",
        help="Undo the most recent organize run in this folder.",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Show detailed (DEBUG level) logging.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(message)s",
    )

    try:
        if args.undo:
            result = undo_last_run(args.directory)
            print(f"\nRestored {result.moved_count} file(s).")
        else:
            result = organize_directory(args.directory, dry_run=args.dry_run)
            verb = "Would move" if args.dry_run else "Moved"
            print(f"\n{verb} {result.moved_count} file(s). Skipped {len(result.skipped)} item(s).")
    except (NotADirectoryError, FileNotFoundError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
