import sys
import unittest
from pathlib import Path


AI_SERVER_ROOT = Path(__file__).resolve().parents[1]
if str(AI_SERVER_ROOT) not in sys.path:
    sys.path.insert(0, str(AI_SERVER_ROOT))

from training.phm_feature_engineering import (
    add_rolling_features,
    select_training_ready_rows,
)


class PHMFeatureEngineeringTest(unittest.TestCase):
    def test_rolling_features_use_only_previous_rows(self):
        rows = [
            self._row(1, "2026-01-01T00:00:00Z", 10.0, 0.1, 40.0),
            self._row(1, "2026-01-01T01:00:00Z", 20.0, 0.2, 50.0),
            self._row(1, "2026-01-01T02:00:00Z", 30.0, 0.3, 60.0),
        ]

        featured_rows = add_rolling_features(rows, window_size=2)

        self.assertIsNone(featured_rows[0]["temperatureRollingMean2"])
        self.assertEqual(featured_rows[1]["temperatureRollingMean2"], 10.0)
        self.assertEqual(featured_rows[2]["temperatureRollingMean2"], 15.0)
        self.assertAlmostEqual(
            featured_rows[2]["temperatureRollingStd2"],
            7.0710678118654755,
        )

    def test_each_device_has_an_independent_history(self):
        rows = [
            self._row(1, "2026-01-01T00:00:00Z", 10.0, 0.1, 40.0),
            self._row(2, "2026-01-01T00:00:00Z", 100.0, 1.0, 80.0),
            self._row(1, "2026-01-01T01:00:00Z", 20.0, 0.2, 50.0),
            self._row(2, "2026-01-01T01:00:00Z", 200.0, 2.0, 90.0),
        ]

        featured_rows = add_rolling_features(rows, window_size=2)

        self.assertEqual(featured_rows[2]["temperatureRollingMean2"], 10.0)
        self.assertEqual(featured_rows[3]["temperatureRollingMean2"], 100.0)

    def test_window_keeps_only_the_latest_previous_values(self):
        rows = [
            self._row(1, "2026-01-01T00:00:00Z", 10.0, 0.1, 40.0),
            self._row(1, "2026-01-01T01:00:00Z", 20.0, 0.2, 50.0),
            self._row(1, "2026-01-01T02:00:00Z", 30.0, 0.3, 60.0),
            self._row(1, "2026-01-01T03:00:00Z", 40.0, 0.4, 70.0),
        ]

        featured_rows = add_rolling_features(rows, window_size=2)

        self.assertEqual(featured_rows[3]["temperatureRollingMean2"], 25.0)

    def test_invalid_window_size_raises_error(self):
        with self.assertRaisesRegex(ValueError, "at least 2"):
            add_rolling_features([], window_size=1)

    def test_only_rows_with_complete_rolling_features_are_selected(self):
        rows = [
            self._row(1, "2026-01-01T00:00:00Z", 10.0, 0.1, 40.0),
            self._row(1, "2026-01-01T01:00:00Z", 20.0, 0.2, 50.0),
            self._row(1, "2026-01-01T02:00:00Z", 30.0, 0.3, 60.0),
        ]
        featured_rows = add_rolling_features(rows, window_size=2)

        result = select_training_ready_rows(
            featured_rows,
            window_size=2,
        )

        self.assertEqual(len(result.ready_rows), 1)
        self.assertEqual(result.ready_rows[0]["sampledAt"], rows[2]["sampledAt"])
        self.assertEqual(len(result.exclusions), 2)

    def test_exclusion_records_missing_feature_columns(self):
        rows = [
            self._row(1, "2026-01-01T00:00:00Z", 10.0, 0.1, 40.0),
        ]
        featured_rows = add_rolling_features(rows, window_size=2)

        result = select_training_ready_rows(
            featured_rows,
            window_size=2,
        )

        self.assertEqual(
            result.exclusions[0].missing_columns,
            (
                "temperatureRollingMean2",
                "temperatureRollingStd2",
                "vibrationRollingMean2",
                "vibrationRollingStd2",
                "noiseRollingMean2",
                "noiseRollingStd2",
            ),
        )

    def test_each_device_has_its_own_warmup_rows(self):
        rows = [
            self._row(1, "2026-01-01T00:00:00Z", 10.0, 0.1, 40.0),
            self._row(2, "2026-01-01T00:00:00Z", 100.0, 1.0, 80.0),
            self._row(1, "2026-01-01T01:00:00Z", 20.0, 0.2, 50.0),
            self._row(2, "2026-01-01T01:00:00Z", 200.0, 2.0, 90.0),
            self._row(1, "2026-01-01T02:00:00Z", 30.0, 0.3, 60.0),
            self._row(2, "2026-01-01T02:00:00Z", 300.0, 3.0, 100.0),
        ]
        featured_rows = add_rolling_features(rows, window_size=2)

        result = select_training_ready_rows(
            featured_rows,
            window_size=2,
        )

        self.assertEqual(len(result.ready_rows), 2)
        self.assertEqual(len(result.exclusions), 4)
        self.assertEqual(
            {int(row["deviceId"]) for row in result.ready_rows},
            {1, 2},
        )

    def _row(
        self,
        device_id: int,
        sampled_at: str,
        temperature: float,
        vibration: float,
        noise: float,
    ) -> dict[str, str]:
        return {
            "deviceId": str(device_id),
            "sampledAt": sampled_at,
            "temperature": str(temperature),
            "vibration": str(vibration),
            "noise": str(noise),
            "failureWithinHorizon": "false",
        }


if __name__ == "__main__":
    unittest.main()
