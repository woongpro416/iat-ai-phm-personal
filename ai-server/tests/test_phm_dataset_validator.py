import sys
import tempfile
import unittest
from pathlib import Path


AI_SERVER_ROOT = Path(__file__).resolve().parents[1]
if str(AI_SERVER_ROOT) not in sys.path:
    sys.path.insert(0, str(AI_SERVER_ROOT))

from training.phm_dataset_validator import (
    PHMDatasetValidationError,
    validate_training_csv,
)


class PHMDatasetValidatorTest(unittest.TestCase):
    def test_valid_csv_returns_dataset_summary(self):
        csv_content = (
            "deviceId,sampledAt,temperature,vibration,noise,"
            "failureWithinHorizon,failureAt\n"
            "1,2026-06-01T09:00:00+09:00,38.2,0.21,49.3,false,\n"
            "2,2026-06-01T10:00:00+09:00,62.7,0.93,77.1,true,"
            "2026-06-01T18:00:00+09:00\n"
        )

        result = self._validate(csv_content)

        self.assertEqual(result.row_count, 2)
        self.assertEqual(result.device_count, 2)
        self.assertEqual(result.positive_label_count, 1)
        self.assertEqual(result.negative_label_count, 1)

    def test_missing_required_column_raises_error(self):
        csv_content = (
            "deviceId,sampledAt,temperature,vibration,noise\n"
            "1,2026-06-01T09:00:00+09:00,38.2,0.21,49.3\n"
        )

        with self.assertRaisesRegex(
            PHMDatasetValidationError,
            "failureWithinHorizon",
        ):
            self._validate(csv_content)

    def test_duplicate_device_and_sampled_at_raises_error(self):
        csv_content = (
            "deviceId,sampledAt,temperature,vibration,noise,"
            "failureWithinHorizon\n"
            "1,2026-06-01T09:00:00+09:00,38.2,0.21,49.3,false\n"
            "1,2026-06-01T09:00:00+09:00,39.0,0.25,50.0,true\n"
        )

        with self.assertRaisesRegex(
            PHMDatasetValidationError,
            "duplicate deviceId",
        ):
            self._validate(csv_content)

    def test_timestamp_without_timezone_raises_error(self):
        csv_content = (
            "deviceId,sampledAt,temperature,vibration,noise,"
            "failureWithinHorizon\n"
            "1,2026-06-01T09:00:00,38.2,0.21,49.3,false\n"
        )

        with self.assertRaisesRegex(
            PHMDatasetValidationError,
            "must include a timezone",
        ):
            self._validate(csv_content)

    def test_negative_temperature_is_allowed(self):
        csv_content = (
            "deviceId,sampledAt,temperature,vibration,noise,"
            "failureWithinHorizon\n"
            "1,2026-06-01T09:00:00+09:00,-3.5,0.21,49.3,false\n"
        )

        result = self._validate(csv_content)

        self.assertEqual(result.row_count, 1)

    def _validate(self, csv_content: str):
        with tempfile.TemporaryDirectory() as temporary_directory:
            csv_path = Path(temporary_directory) / "phm-training.csv"
            csv_path.write_text(csv_content, encoding="utf-8")
            return validate_training_csv(csv_path)


if __name__ == "__main__":
    unittest.main()
