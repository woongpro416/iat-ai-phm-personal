import csv
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path

from training.phm_dataset_validator import validate_training_csv


@dataclass(frozen=True)
class PHMTimeSplitResult:
    train_rows: tuple[dict[str, str], ...]
    validation_rows: tuple[dict[str, str], ...]
    test_rows: tuple[dict[str, str], ...]
    purged_rows: tuple[dict[str, str], ...]
    validation_start: datetime
    test_start: datetime


def split_training_csv(
    csv_path: str | Path,
    train_ratio: float = 0.70,
    validation_ratio: float = 0.15,
    prediction_horizon: timedelta = timedelta(hours=24),
) -> PHMTimeSplitResult:
    _validate_split_options(
        train_ratio=train_ratio,
        validation_ratio=validation_ratio,
        prediction_horizon=prediction_horizon,
    )
    validate_training_csv(csv_path)

    rows = _load_timestamped_rows(csv_path)
    unique_timestamps = sorted({sampled_at for sampled_at, _ in rows})
    if len(unique_timestamps) < 3:
        raise ValueError(
            "At least three unique sampledAt values are required for "
            "train/validation/test splits."
        )

    validation_index = max(1, int(len(unique_timestamps) * train_ratio))
    test_index = max(
        validation_index + 1,
        int(len(unique_timestamps) * (train_ratio + validation_ratio)),
    )
    test_index = min(test_index, len(unique_timestamps) - 1)

    validation_start = unique_timestamps[validation_index]
    test_start = unique_timestamps[test_index]
    train_purge_start = validation_start - prediction_horizon
    validation_purge_start = test_start - prediction_horizon

    train_rows = []
    validation_rows = []
    test_rows = []
    purged_rows = []

    for sampled_at, row in rows:
        if sampled_at < train_purge_start:
            train_rows.append(row)
        elif sampled_at < validation_start:
            purged_rows.append(row)
        elif sampled_at < validation_purge_start:
            validation_rows.append(row)
        elif sampled_at < test_start:
            purged_rows.append(row)
        else:
            test_rows.append(row)

    _validate_non_empty_splits(
        train_rows=train_rows,
        validation_rows=validation_rows,
        test_rows=test_rows,
        prediction_horizon=prediction_horizon,
    )

    return PHMTimeSplitResult(
        train_rows=tuple(train_rows),
        validation_rows=tuple(validation_rows),
        test_rows=tuple(test_rows),
        purged_rows=tuple(purged_rows),
        validation_start=validation_start,
        test_start=test_start,
    )


def _validate_split_options(
    train_ratio: float,
    validation_ratio: float,
    prediction_horizon: timedelta,
) -> None:
    if train_ratio <= 0 or validation_ratio <= 0:
        raise ValueError("train_ratio and validation_ratio must be positive.")

    if train_ratio + validation_ratio >= 1:
        raise ValueError(
            "train_ratio + validation_ratio must be less than 1."
        )

    if prediction_horizon <= timedelta(0):
        raise ValueError("prediction_horizon must be positive.")


def _load_timestamped_rows(
    csv_path: str | Path,
) -> list[tuple[datetime, dict[str, str]]]:
    path = Path(csv_path)
    timestamped_rows = []

    with path.open("r", encoding="utf-8-sig", newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            sampled_at = datetime.fromisoformat(
                row["sampledAt"].strip().replace("Z", "+00:00")
            )
            timestamped_rows.append((sampled_at, row))

    return sorted(timestamped_rows, key=lambda item: item[0])


def _validate_non_empty_splits(
    train_rows: list[dict[str, str]],
    validation_rows: list[dict[str, str]],
    test_rows: list[dict[str, str]],
    prediction_horizon: timedelta,
) -> None:
    empty_split_names = [
        split_name
        for split_name, split_rows in (
            ("train", train_rows),
            ("validation", validation_rows),
            ("test", test_rows),
        )
        if not split_rows
    ]
    if empty_split_names:
        raise ValueError(
            "Empty split after applying "
            f"{prediction_horizon} purge: {', '.join(empty_split_names)}. "
            "Use a longer dataset or a shorter prediction horizon."
        )
