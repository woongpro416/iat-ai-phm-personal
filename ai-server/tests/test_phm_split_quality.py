import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path


AI_SERVER_ROOT = Path(__file__).resolve().parents[1]
if str(AI_SERVER_ROOT) not in sys.path:
    sys.path.insert(0, str(AI_SERVER_ROOT))

from training.phm_dataset_splitter import PHMTimeSplitResult
from training.phm_split_quality import (
    PHMSplitQualityError,
    analyze_split_quality,
    ensure_training_ready,
)


class PHMSplitQualityTest(unittest.TestCase):
    def test_quality_report_summarizes_each_split(self):
        split_result = self._split_result()

        report = analyze_split_quality(split_result)

        self.assertTrue(report.is_training_ready)
        self.assertEqual(report.train.row_count, 4)
        self.assertEqual(report.train.device_count, 2)
        self.assertEqual(report.train.positive_label_count, 2)
        self.assertEqual(report.train.negative_label_count, 2)
        self.assertEqual(report.train.positive_label_ratio, 0.5)
        self.assertEqual(report.purged_row_count, 1)

    def test_missing_positive_label_is_reported(self):
        split_result = self._split_result(
            validation_labels=(False, False),
        )

        report = analyze_split_quality(split_result)

        self.assertFalse(report.is_training_ready)
        self.assertIn(
            "validation split has no positive failure labels.",
            report.issues,
        )

    def test_quality_issue_blocks_training(self):
        split_result = self._split_result(
            test_labels=(True, True),
        )
        report = analyze_split_quality(split_result)

        with self.assertRaisesRegex(
            PHMSplitQualityError,
            "test split has no negative normal labels",
        ):
            ensure_training_ready(report)

    def test_timestamp_overlap_is_reported(self):
        split_result = PHMTimeSplitResult(
            train_rows=(
                self._row(1, "2026-01-01T00:00:00Z", False),
                self._row(1, "2026-01-03T00:00:00Z", True),
            ),
            validation_rows=(
                self._row(1, "2026-01-02T00:00:00Z", False),
                self._row(1, "2026-01-04T00:00:00Z", True),
            ),
            test_rows=(
                self._row(1, "2026-01-05T00:00:00Z", False),
                self._row(1, "2026-01-06T00:00:00Z", True),
            ),
            purged_rows=(),
            validation_start=datetime(2026, 1, 2, tzinfo=timezone.utc),
            test_start=datetime(2026, 1, 5, tzinfo=timezone.utc),
        )

        report = analyze_split_quality(split_result)

        self.assertIn(
            "train and validation timestamps overlap or are out of order.",
            report.issues,
        )

    def _split_result(
        self,
        validation_labels: tuple[bool, bool] = (False, True),
        test_labels: tuple[bool, bool] = (False, True),
    ) -> PHMTimeSplitResult:
        return PHMTimeSplitResult(
            train_rows=(
                self._row(1, "2026-01-01T00:00:00Z", False),
                self._row(2, "2026-01-01T00:00:00Z", True),
                self._row(1, "2026-01-02T00:00:00Z", False),
                self._row(2, "2026-01-02T00:00:00Z", True),
            ),
            validation_rows=(
                self._row(
                    1,
                    "2026-01-04T00:00:00Z",
                    validation_labels[0],
                ),
                self._row(
                    2,
                    "2026-01-04T00:00:00Z",
                    validation_labels[1],
                ),
            ),
            test_rows=(
                self._row(1, "2026-01-06T00:00:00Z", test_labels[0]),
                self._row(2, "2026-01-06T00:00:00Z", test_labels[1]),
            ),
            purged_rows=(
                self._row(1, "2026-01-03T00:00:00Z", False),
            ),
            validation_start=datetime(2026, 1, 4, tzinfo=timezone.utc),
            test_start=datetime(2026, 1, 6, tzinfo=timezone.utc),
        )

    def _row(
        self,
        device_id: int,
        sampled_at: str,
        label: bool,
    ) -> dict[str, str]:
        return {
            "deviceId": str(device_id),
            "sampledAt": sampled_at,
            "temperature": "40.0",
            "vibration": "0.2",
            "noise": "50.0",
            "failureWithinHorizon": str(label).lower(),
        }


if __name__ == "__main__":
    unittest.main()
