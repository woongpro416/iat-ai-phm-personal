from dataclasses import dataclass

from training.phm_feature_engineering import FeatureRow


DEFAULT_FEATURE_NAMES = (
    "temperature",
    "vibration",
    "noise",
    "temperatureRollingMean12",
    "temperatureRollingStd12",
    "vibrationRollingMean12",
    "vibrationRollingStd12",
    "noiseRollingMean12",
    "noiseRollingStd12",
)


@dataclass(frozen=True)
class PHMModelInput:
    feature_names: tuple[str, ...]
    x: tuple[tuple[float, ...], ...]
    y: tuple[int, ...]
    device_ids: tuple[int, ...]
    sampled_at_values: tuple[str, ...]


def build_model_input(
    rows: tuple[FeatureRow, ...] | list[FeatureRow],
    feature_names: tuple[str, ...] = DEFAULT_FEATURE_NAMES,
) -> PHMModelInput:
    if not rows:
        raise ValueError("At least one training row is required.")

    x_rows = []
    y_values = []
    device_ids = []
    sampled_at_values = []

    for row_index, row in enumerate(rows, start=1):
        x_rows.append(
            tuple(
                _parse_float(row, feature_name, row_index)
                for feature_name in feature_names
            )
        )
        y_values.append(_parse_label(row, row_index))
        device_ids.append(_parse_device_id(row, row_index))
        sampled_at_values.append(_parse_required_text(row, "sampledAt", row_index))

    return PHMModelInput(
        feature_names=feature_names,
        x=tuple(x_rows),
        y=tuple(y_values),
        device_ids=tuple(device_ids),
        sampled_at_values=tuple(sampled_at_values),
    )


def feature_names_for_window(window_size: int) -> tuple[str, ...]:
    if window_size < 2:
        raise ValueError("window_size must be at least 2.")

    return (
        "temperature",
        "vibration",
        "noise",
        f"temperatureRollingMean{window_size}",
        f"temperatureRollingStd{window_size}",
        f"vibrationRollingMean{window_size}",
        f"vibrationRollingStd{window_size}",
        f"noiseRollingMean{window_size}",
        f"noiseRollingStd{window_size}",
    )


def _parse_float(row: FeatureRow, column_name: str, row_index: int) -> float:
    value = row.get(column_name)
    if value is None or value == "":
        raise ValueError(f"Row {row_index}: {column_name} is required.")

    try:
        return float(value)
    except (TypeError, ValueError) as error:
        raise ValueError(
            f"Row {row_index}: {column_name} must be numeric."
        ) from error


def _parse_label(row: FeatureRow, row_index: int) -> int:
    value = _parse_required_text(row, "failureWithinHorizon", row_index)
    normalized_value = value.lower()
    if normalized_value in {"true", "1"}:
        return 1
    if normalized_value in {"false", "0"}:
        return 0

    raise ValueError(
        f"Row {row_index}: failureWithinHorizon must be true/false or 1/0."
    )


def _parse_device_id(row: FeatureRow, row_index: int) -> int:
    value = _parse_required_text(row, "deviceId", row_index)
    try:
        return int(value)
    except ValueError as error:
        raise ValueError(f"Row {row_index}: deviceId must be an integer.") from error


def _parse_required_text(
    row: FeatureRow,
    column_name: str,
    row_index: int,
) -> str:
    value = row.get(column_name)
    if value is None:
        raise ValueError(f"Row {row_index}: {column_name} is required.")

    text = str(value).strip()
    if not text:
        raise ValueError(f"Row {row_index}: {column_name} is required.")

    return text
