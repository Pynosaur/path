import os
import sys
import tempfile
import time
import unittest
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.core.finder import find, format_results, parse_size, format_size, build_tree


class TestParseSize(unittest.TestCase):
    def test_parse_plus_megabyte(self):
        direction, value = parse_size("+1M")
        self.assertEqual(direction, "gt")
        self.assertEqual(value, 1024 ** 2)

    def test_parse_minus_kilobyte(self):
        direction, value = parse_size("-100K")
        self.assertEqual(direction, "lt")
        self.assertEqual(value, 100 * 1024)

    def test_parse_bare_number(self):
        direction, value = parse_size("500")
        self.assertEqual(direction, "gt")
        self.assertEqual(value, 500)

    def test_parse_gigabyte(self):
        direction, value = parse_size("+2G")
        self.assertEqual(direction, "gt")
        self.assertEqual(value, 2 * 1024 ** 3)


class TestFormatSize(unittest.TestCase):
    def test_bytes(self):
        self.assertEqual(format_size(100), "100B")

    def test_kilobytes(self):
        self.assertEqual(format_size(2048), "2.0K")

    def test_megabytes(self):
        self.assertEqual(format_size(5 * 1024 ** 2), "5.0M")

    def test_gigabytes(self):
        self.assertEqual(format_size(3 * 1024 ** 3), "3.0G")


class TestFind(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        Path(self.tmpdir, "file1.py").write_text("hello")
        Path(self.tmpdir, "file2.txt").write_text("world")
        Path(self.tmpdir, "file3.py").write_text("x" * 2000)
        subdir = Path(self.tmpdir, "subdir")
        subdir.mkdir()
        Path(subdir, "nested.py").write_text("nested")
        deep = Path(subdir, "deep")
        deep.mkdir()
        Path(deep, "bottom.txt").write_text("bottom")
        Path(self.tmpdir, ".hidden").write_text("secret")
        hidden_dir = Path(self.tmpdir, ".hiddendir")
        hidden_dir.mkdir()
        Path(hidden_dir, "inside.txt").write_text("inside")

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmpdir)

    def test_find_all(self):
        results = find(self.tmpdir, {})
        names = [e.name for e, _ in results]
        self.assertIn("file1.py", names)
        self.assertIn("subdir", names)
        self.assertNotIn(".hidden", names)

    def test_find_files_only(self):
        results = find(self.tmpdir, {"files_only": True})
        for entry, _ in results:
            self.assertTrue(entry.is_file())

    def test_find_dirs_only(self):
        results = find(self.tmpdir, {"dirs_only": True})
        for entry, _ in results:
            self.assertTrue(entry.is_dir())

    def test_find_by_extension(self):
        results = find(self.tmpdir, {"ext": "py"})
        names = [e.name for e, _ in results]
        self.assertIn("file1.py", names)
        self.assertIn("file3.py", names)
        self.assertIn("nested.py", names)
        self.assertNotIn("file2.txt", names)

    def test_find_by_pattern(self):
        results = find(self.tmpdir, {"pattern": "*.txt"})
        names = [e.name for e, _ in results]
        self.assertIn("file2.txt", names)
        self.assertNotIn("file1.py", names)

    def test_find_by_name(self):
        results = find(self.tmpdir, {"name": "nested"})
        names = [e.name for e, _ in results]
        self.assertIn("nested.py", names)
        self.assertEqual(len(results), 1)

    def test_find_with_layers(self):
        results = find(self.tmpdir, {"layers": 1})
        names = [e.name for e, _ in results]
        self.assertIn("file1.py", names)
        self.assertIn("subdir", names)
        self.assertNotIn("nested.py", names)

    def test_find_with_layers_2(self):
        results = find(self.tmpdir, {"layers": 2})
        names = [e.name for e, _ in results]
        self.assertIn("nested.py", names)
        self.assertNotIn("bottom.txt", names)

    def test_find_hidden(self):
        results = find(self.tmpdir, {"hidden": True})
        names = [e.name for e, _ in results]
        self.assertIn(".hidden", names)
        self.assertIn(".hiddendir", names)

    def test_find_size_filter(self):
        results = find(self.tmpdir, {"files_only": True, "size": "+1K"})
        names = [e.name for e, _ in results]
        self.assertIn("file3.py", names)
        self.assertNotIn("file1.py", names)

    def test_find_nonexistent(self):
        results = find("/nonexistent/path/xyz", {})
        self.assertEqual(results, [])


class TestFormatResults(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        Path(self.tmpdir, "a.py").write_text("hello")
        Path(self.tmpdir, "b.txt").write_text("world")
        sub = Path(self.tmpdir, "sub")
        sub.mkdir()

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmpdir)

    def test_count_format(self):
        results = find(self.tmpdir, {})
        output = format_results(results, self.tmpdir, {"count": True})
        self.assertIn("file", output)
        self.assertIn("dir", output)

    def test_tree_format(self):
        results = find(self.tmpdir, {})
        output = format_results(results, self.tmpdir, {"tree": True})
        self.assertIn("├", output)

    def test_long_format(self):
        results = find(self.tmpdir, {"files_only": True})
        output = format_results(results, self.tmpdir, {"long": True})
        self.assertIn("B", output)


if __name__ == "__main__":
    unittest.main()
