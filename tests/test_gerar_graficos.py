import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from gerar_graficos import load_data, smells_per_thousand_lines, totals_by_provider


class AnalysisDataTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = load_data()

    def test_totals_use_individual_smells_and_exclude_project_base(self):
        self.assertEqual(
            totals_by_provider(self.rows),
            {"Gratuita": 87, "Paga": 193},
        )

    def test_density_uses_supplied_lines(self):
        free_cart = next(row for row in self.rows if row["label"] == "Carrinho Gratuito")
        self.assertAlmostEqual(smells_per_thousand_lines(free_cart), 7 * 1000 / 667)

    def test_project_base_has_no_density_without_line_count(self):
        baseline = next(row for row in self.rows if row["provider"] == "Base")
        self.assertIsNone(smells_per_thousand_lines(baseline))


if __name__ == "__main__":
    unittest.main()
