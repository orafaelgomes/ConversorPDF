import sys
import unittest
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from main import build_output_path


class BuildOutputPathTests(unittest.TestCase):
    def test_uses_same_directory_when_output_dir_is_not_provided(self) -> None:
        self.assertEqual(
            build_output_path("documents/sample.pdf"),
            Path("documents/sample_pdfa.pdf"),
        )

    def test_uses_selected_output_directory_when_provided(self) -> None:
        self.assertEqual(
            build_output_path("documents/sample.pdf", "output"),
            Path("output/sample_pdfa.pdf"),
        )


if __name__ == "__main__":
    unittest.main()
