from collections import defaultdict, deque
from dataclasses import dataclass
from datetime import datetime
from statistics import fmean, stdev
from typing import TypeAlias


SENSOR_COLUMNS = ("temperature", "vibration", "noise")
FeatureValue: TypeAlias = str | float | None
FeatureRow: TypeAlias = dict[str, FeatureValue]


@dataclass(frozen=True)
class PHMFeatureExclusion:
    device_id: int
    sampled_at: str
    missing_columns: tuple[str, ...]


@dataclass(frozen=True)
class PHMFeaturePreparationResult:
    ready_rows: tuple[FeatureRow, ...]
    exclusions: tuple[PHMFeatureExclusion, ...]


def add_rolling_features(
    rows: tuple[dict[str, str], ...] | list[dict[str, str]],
    window_size: int = 12,
) -> tuple[FeatureRow, ...]:
    if window_size < 2:
        raise ValueError("window_size must be at least 2.")

    sorted_rows = sorted(
        rows,
        key=lambda row: (
            _parse_timestamp(row["sampledAt"]),
            int(row["deviceId"]),
        ),
    )
    histories = _create_device_histories(window_size)
    featured_rows = []

    for row in sorted_rows:
        device_id = int(row["deviceId"])
        featured_row: FeatureRow = dict(row)

        for sensor_name in SENSOR_COLUMNS:
            previous_values = histories[device_id][sensor_name]
            mean_column = f"{sensor_name}RollingMean{window_size}"
            std_column = f"{sensor_name}RollingStd{window_size}"

            featured_row[mean_column] = (
                fmean(previous_values) if previous_values else None
            )
            featured_row[std_column] = (
                stdev(previous_values)
                if len(previous_values) >= 2
                else None
            )

        for sensor_name in SENSOR_COLUMNS:
            histories[device_id][sensor_name].append(float(row[sensor_name]))

        featured_rows.append(featured_row)

    return tuple(featured_rows)


def select_training_ready_rows(
    featured_rows: tuple[FeatureRow, ...] | list[FeatureRow],
    window_size: int = 12,
) -> PHMFeaturePreparationResult:
    if window_size < 2:
        raise ValueError("window_size must be at least 2.")

    rolling_columns = _rolling_feature_columns(window_size)
    ready_rows = []
    exclusions = []

    for row in featured_rows:
        missing_columns = tuple(
            column_name
            for column_name in rolling_columns
            if row.get(column_name) is None
        )

        if missing_columns:
            exclusions.append(
                PHMFeatureExclusion(
                    device_id=int(row["deviceId"]),
                    sampled_at=str(row["sampledAt"]),
                    missing_columns=missing_columns,
                )
            )
            continue

        ready_rows.append(row)

    return PHMFeaturePreparationResult(
        ready_rows=tuple(ready_rows),
        exclusions=tuple(exclusions),
    )


def _rolling_feature_columns(window_size: int) -> tuple[str, ...]:
    return tuple(
        column_name
        for sensor_name in SENSOR_COLUMNS
        for column_name in (
            f"{sensor_name}RollingMean{window_size}",
            f"{sensor_name}RollingStd{window_size}",
        )
    )


def _create_device_histories(
    window_size: int,
) -> defaultdict[int, dict[str, deque[float]]]:
    return defaultdict(
        lambda: {
            sensor_name: deque(maxlen=window_size)
            for sensor_name in SENSOR_COLUMNS
        }
    )


def _parse_timestamp(value: str) -> datetime:
    return datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
