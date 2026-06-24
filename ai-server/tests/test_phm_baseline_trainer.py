import sys
import unittest
from pathlib import Path


AI_SERVER_ROOT = Path(__file__).resolve().parents[1]
if str(AI_SERVER_ROOT) not in sys.path:
    sys.path.insert(0, str(AI_SERVER_ROOT))

from training.phm_baseline_trainer import evaluate_binary_classifier


class PHMBaselineTrainerTest(unittest.TestCase):
    def test_evaluate_binary_classifier_returns_expected_metrics(self):
        metrics = evaluate_binary_classifier(
            y_true=(0, 0, 1, 1),
            y_probability=(0.1, 0.7, 0.8, 0.4),
            threshold=0.5,
        )

        self.assertEqual(metrics.true_negative, 1)
        self.assertEqual(metrics.false_positive, 1)
        self.assertEqual(metrics.false_negative, 1)
        self.assertEqual(metrics.true_positive, 1)
        self.assertEqual(metrics.precision, 0.5)
        self.assertEqual(metrics.recall, 0.5)
        self.assertEqual(metrics.f1, 0.5)
        self.assertEqual(metrics.false_alarm_rate, 0.5)

    def test_invalid_threshold_raises_error(self):
        with self.assertRaisesRegex(ValueError, "decision_threshold"):
            evaluate_binary_classifier(
                y_true=(0, 1),
                y_probability=(0.1, 0.9),
                threshold=1.0,
            )


if __name__ == "__main__":
    unittest.main()
