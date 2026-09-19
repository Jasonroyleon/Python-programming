"""Unit tests for organizer/organizer.py.

Run with:  python -m unittest discover tests
"""

import shutil
import tempfile
import unittest
from pathlib import Path

from organizer.organizer import (
    get_category,
    organize_directory,
    undo_last_run,
)


class TestGetCategory(unittest.TestCase):
    def test_known_extensions(self):
        self.assertEqual(get_category(".jpg"), "Images")
        self.assertEqual(get_category(".PDF"), "Documents")  # case-insensitive
        self.assertEqual(get_category(".mp3"), "Audio")
        self.assertEqual(get_category(".py"), "Code")

    def test_unknown_extension_falls_back_to_others(self):
        self.assertEqual(get_category(".xyz123"), "Others")


class TestOrganizeDirectory(unittest.TestCase):
    def setUp(self):
        # Create a fresh temporary "messy" folder before every test.
        self.tmp_dir = tempfile.mkdtemp()
        self.tmp_path = Path(self.tmp_dir)
        for name in ["photo.jpg", "notes.txt", "song.mp3", "script.py", "mystery.xyz"]:
            (self.tmp_path / name).write_text("dummy content")

    def tearDown(self):
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_dry_run_does_not_move_files(self):
        result = organize_directory(self.tmp_path, dry_run=True)
        self.assertEqual(result.moved_count, 5)
        # Nothing should have actually moved on disk.
        self.assertTrue((self.tmp_path / "photo.jpg").exists())
        self.assertFalse((self.tmp_path / "Images").exists())

    def test_real_run_moves_files_into_categories(self):
        result = organize_directory(self.tmp_path, dry_run=False)
        self.assertEqual(result.moved_count, 5)
        self.assertTrue((self.tmp_path / "Images" / "photo.jpg").exists())
        self.assertTrue((self.tmp_path / "Documents" / "notes.txt").exists())
        self.assertTrue((self.tmp_path / "Audio" / "song.mp3").exists())
        self.assertTrue((self.tmp_path / "Code" / "script.py").exists())
        self.assertTrue((self.tmp_path / "Others" / "mystery.xyz").exists())
        # Original files should be gone from the root.
        self.assertFalse((self.tmp_path / "photo.jpg").exists())

    def test_name_conflict_is_resolved(self):
        # Pre-create a colliding file in the destination.
        (self.tmp_path / "Images").mkdir()
        (self.tmp_path / "Images" / "photo.jpg").write_text("already here")

        organize_directory(self.tmp_path, dry_run=False)

        self.assertTrue((self.tmp_path / "Images" / "photo.jpg").exists())
        self.assertTrue((self.tmp_path / "Images" / "photo (1).jpg").exists())

    def test_undo_restores_original_layout(self):
        organize_directory(self.tmp_path, dry_run=False)
        undo_last_run(self.tmp_path)

        self.assertTrue((self.tmp_path / "photo.jpg").exists())
        self.assertTrue((self.tmp_path / "notes.txt").exists())
        self.assertTrue((self.tmp_path / "song.mp3").exists())

    def test_undo_without_prior_run_raises(self):
        with self.assertRaises(FileNotFoundError):
            undo_last_run(self.tmp_path)

    def test_invalid_directory_raises(self):
        with self.assertRaises(NotADirectoryError):
            organize_directory(self.tmp_path / "does_not_exist")


if __name__ == "__main__":
    unittest.main()
