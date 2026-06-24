import sys
import unittest
from pathlib import Path


AI_SERVER_ROOT = Path(__file__).resolve().parents[1]
if str(AI_SERVER_ROOT) not in sys.path:
    sys.path.insert(0, str(AI_SERVER_ROOT))

from training.phm_model_input import build_model_input, feature_names_for_window


class PHMModelInputTest(unittest.TestCase):
    def test_build_model_input_returns_features_labels_and_row_identity(self):
        rows = [
            self._row(
                device_id=1,
                sampled_at="2026-01-01T12:00:00Z",
                label="true",
            ),
            self._row(
                device_id=2,
                sampled_at="2026-01-01T13:00:00Z",
                label="false",
                temperature=42.5,
            ),
        ]

        result = build_model_input(rows)

        self.assertEqual(len(result.x), 2)
        self.assertEqual(len(result.feature_names), 9)
        self.assertEqual(result.y, (1, 0))
        self.assertEqual(result.device_ids, (1, 2))
        self.assertEqual(
            result.sampled_at_values,
            ("2026-01-01T12:00:00Z", "2026-01-01T13:00:00Z"),
        )
        self.assertEqual(result.x[1][0], 42.5)

    def test_missing_feature_raises_error(self):
        row = self._row(device_id=1, sampled_at="2026-01-01T12:00:00Z")
        row["temperatureRollingStd12"] = None

        with self.assertRaisesRegex(ValueError, "temperatureRollingStd12"):
            build_model_input([row])

    def test_invalid_label_raises_error(self):
        row = self._row(
            device_id=1,
            sampled_at="2026-01-01T12:00:00Z",
            label="WARNING",
        )

        with self.assertRaisesRegex(ValueError, "failureWithinHorizon"):
            build_model_input([row])

    def test_empty_rows_raise_error(self):
        with self.assertRaisesRegex(ValueError, "At least one"):
            build_model_input([])

    def test_feature_names_follow_window_size(self):
        feature_names = feature_names_for_window(6)

        self.assertIn("temperatureRollingMean6", feature_names)
        self.assertIn("noiseRollingStd6", feature_names)
        self.assertNotIn("temperatureRollingMean12", feature_names)

    def _row(
        self,
        device_id: int,
        sampled_at: str,
        label: str = "false",
        temperature: float = 36.0,
    ) -> dict[str, str | float]:
        return {
            "deviceId": str(device_id),
            "sampledAt": sampled_at,
            "temperature": temperature,
            "vibration": 0.2,
            "noise": 50.0,
            "temperatureRollingMean12": 35.0,
            "temperatureRollingStd12": 1.2,
            "vibrationRollingMean12": 0.18,
            "vibrationRollingStd12": 0.03,
            "noiseRollingMean12": 48.0,
            "noiseRollingStd12": 2.4,
            "failureWithinHorizon": label,
        }


if __name__ == "__main__":
    unittest.main()
