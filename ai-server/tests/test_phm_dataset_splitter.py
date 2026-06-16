import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path


AI_SERVER_ROOT = Path(__file__).resolve().parents[1]
if str(AI_SERVER_ROOT) not in sys.path:
    sys.path.insert(0, str(AI_SERVER_ROOT))

from training.phm_dataset_splitter import split_training_csv


class PHMDatasetSplitterTest(unittest.TestCase):
    def test_split_preserves_time_order_and_purges_boundaries(self):
        csv_content = self._create_hourly_csv(hour_count=100)

        result = self._split(
            csv_content,
            prediction_horizon=timedelta(hours=2),
        )

        train_times = self._sampled_times(result.train_rows)
        validation_times = self._sampled_times(result.validation_rows)
        test_times = self._sampled_times(result.test_rows)
        purged_times = self._sampled_times(result.purged_rows)

        self.assertLess(max(train_times), min(validation_times))
        self.assertLess(max(validation_times), min(test_times))
        self.assertEqual(result.validation_start, self._at_hour(70))
        self.assertEqual(result.test_start, self._at_hour(85))
        self.assertEqual(
            purged_times,
            [
                self._at_hour(68),
                self._at_hour(69),
                self._at_hour(83),
                self._at_hour(84),
            ],
        )

    def test_same_timestamp_rows_stay_in_the_same_split(self):
        csv_content = self._create_hourly_csv(
            hour_count=100,
            device_ids=(1, 2),
        )

        result = self._split(
            csv_content,
            prediction_horizon=timedelta(hours=2),
        )

        split_by_timestamp = {}
        for split_name, rows in (
            ("train", result.train_rows),
            ("validation", result.validation_rows),
            ("test", result.test_rows),
            ("purged", result.purged_rows),
        ):
            for sampled_at in self._sampled_times(rows):
                split_by_timestamp.setdefault(sampled_at, set()).add(split_name)

        self.assertTrue(
            all(len(split_names) == 1 for split_names in split_by_timestamp.values())
        )

    def test_long_purge_that_empties_split_raises_error(self):
        csv_content = self._create_hourly_csv(hour_count=10)

        with self.assertRaisesRegex(ValueError, "Empty split"):
            self._split(
                csv_content,
                prediction_horizon=timedelta(hours=24),
            )

    def _split(self, csv_content: str, prediction_horizon: timedelta):
        with tempfile.TemporaryDirectory() as temporary_directory:
            csv_path = Path(temporary_directory) / "phm-training.csv"
            csv_path.write_text(csv_content, encoding="utf-8")
            return split_training_csv(
                csv_path,
                prediction_horizon=prediction_horizon,
            )

    def _create_hourly_csv(
        self,
        hour_count: int,
        device_ids: tuple[int, ...] = (1,),
    ) -> str:
        lines = [
            "deviceId,sampledAt,temperature,vibration,noise,"
            "failureWithinHorizon"
        ]
        for hour in range(hour_count):
            for device_id in device_ids:
                lines.append(
                    f"{device_id},{self._at_hour(hour).isoformat()},"
                    f"{30 + hour * 0.1:.1f},0.2,45.0,false"
                )

        return "\n".join(lines) + "\n"

    def _sampled_times(
        self,
        rows: tuple[dict[str, str], ...],
    ) -> list[datetime]:
        return [
            datetime.fromisoformat(row["sampledAt"].replace("Z", "+00:00"))
            for row in rows
        ]

    def _at_hour(self, hour: int) -> datetime:
        return datetime(2026, 1, 1, tzinfo=timezone.utc) + timedelta(hours=hour)


if __name__ == "__main__":
    unittest.main()
