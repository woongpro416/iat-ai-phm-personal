import csv
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


REQUIRED_COLUMNS = {
    "deviceId",
    "sampledAt",
    "temperature",
    "vibration",
    "noise",
    "failureWithinHorizon",
}
OPTIONAL_COLUMNS = {"failureAt"}
TRUE_VALUES = {"true", "1"}
FALSE_VALUES = {"false", "0"}


class PHMDatasetValidationError(ValueError):
    """Raised when a PHM training CSV violates the data contract."""


@dataclass(frozen=True)
class PHMDatasetValidationResult:
    row_count: int
    device_count: int
    sampled_at_start: datetime
    sampled_at_end: datetime
    positive_label_count: int
    negative_label_count: int


def validate_training_csv(csv_path: str | Path) -> PHMDatasetValidationResult:
    path = Path(csv_path)
    if not path.is_file():
        raise PHMDatasetValidationError(f"CSV file does not exist: {path}")

    with path.open("r", encoding="utf-8-sig", newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        _validate_columns(reader.fieldnames)

        device_ids = set()
        sampled_times = []
        unique_grains = set()
        positive_label_count = 0
        negative_label_count = 0

        for row_number, row in enumerate(reader, start=2):
            _validate_required_values(row, row_number)

            device_id = _parse_positive_device_id(row["deviceId"], row_number)
            sampled_at = _parse_timestamp(
                row["sampledAt"],
                row_number,
                "sampledAt",
                required=True,
            )
            _parse_number(
                row["temperature"],
                row_number,
                "temperature",
            )
            _parse_non_negative_number(
                row["vibration"],
                row_number,
                "vibration",
            )
            _parse_non_negative_number(row["noise"], row_number, "noise")
            label = _parse_boolean_label(
                row["failureWithinHorizon"],
                row_number,
            )

            failure_at_value = row.get("failureAt", "")
            failure_at = _parse_timestamp(
                failure_at_value,
                row_number,
                "failureAt",
                required=False,
            )
            if failure_at is not None and failure_at < sampled_at:
                raise PHMDatasetValidationError(
                    f"Row {row_number}: failureAt cannot be earlier than sampledAt."
                )

            grain = (device_id, sampled_at)
            if grain in unique_grains:
                raise PHMDatasetValidationError(
                    "Row "
                    f"{row_number}: duplicate deviceId + sampledAt grain: {grain}."
                )

            unique_grains.add(grain)
            device_ids.add(device_id)
            sampled_times.append(sampled_at)
            if label:
                positive_label_count += 1
            else:
                negative_label_count += 1

    if not sampled_times:
        raise PHMDatasetValidationError("CSV must contain at least one data row.")

    return PHMDatasetValidationResult(
        row_count=len(sampled_times),
        device_count=len(device_ids),
        sampled_at_start=min(sampled_times),
        sampled_at_end=max(sampled_times),
        positive_label_count=positive_label_count,
        negative_label_count=negative_label_count,
    )


def _validate_columns(fieldnames: list[str] | None) -> None:
    if not fieldnames:
        raise PHMDatasetValidationError("CSV header is missing.")

    stripped_fieldnames = [column.strip() for column in fieldnames]
    normalized_columns = set(stripped_fieldnames)
    missing_columns = sorted(REQUIRED_COLUMNS - normalized_columns)
    if missing_columns:
        raise PHMDatasetValidationError(
            "Missing required columns: " + ", ".join(missing_columns)
        )

    duplicate_columns = {
        column
        for column in normalized_columns
        if stripped_fieldnames.count(column) > 1
    }
    if duplicate_columns:
        raise PHMDatasetValidationError(
            "Duplicate columns: " + ", ".join(sorted(duplicate_columns))
        )


def _validate_required_values(row: dict[str, str], row_number: int) -> None:
    missing_values = [
        column
        for column in REQUIRED_COLUMNS
        if row.get(column) is None or not row[column].strip()
    ]
    if missing_values:
        raise PHMDatasetValidationError(
            f"Row {row_number}: missing required values: "
            + ", ".join(sorted(missing_values))
        )


def _parse_positive_device_id(value: str, row_number: int) -> int:
    try:
        device_id = int(value)
    except ValueError as error:
        raise PHMDatasetValidationError(
            f"Row {row_number}: deviceId must be an integer."
        ) from error

    if device_id <= 0:
        raise PHMDatasetValidationError(
            f"Row {row_number}: deviceId must be positive."
        )

    return device_id


def _parse_timestamp(
    value: str,
    row_number: int,
    column_name: str,
    required: bool,
) -> datetime | None:
    normalized_value = value.strip()
    if not normalized_value:
        if required:
            raise PHMDatasetValidationError(
                f"Row {row_number}: {column_name} is required."
            )
        return None

    try:
        parsed_timestamp = datetime.fromisoformat(
            normalized_value.replace("Z", "+00:00")
        )
    except ValueError as error:
        raise PHMDatasetValidationError(
            f"Row {row_number}: {column_name} must be an ISO-8601 timestamp."
        ) from error

    if parsed_timestamp.tzinfo is None:
        raise PHMDatasetValidationError(
            f"Row {row_number}: {column_name} must include a timezone."
        )

    return parsed_timestamp


def _parse_non_negative_number(
    value: str,
    row_number: int,
    column_name: str,
) -> float:
    number = _parse_number(value, row_number, column_name)

    if number < 0:
        raise PHMDatasetValidationError(
            f"Row {row_number}: {column_name} cannot be negative."
        )

    return number


def _parse_number(
    value: str,
    row_number: int,
    column_name: str,
) -> float:
    try:
        number = float(value)
    except ValueError as error:
        raise PHMDatasetValidationError(
            f"Row {row_number}: {column_name} must be numeric."
        ) from error

    return number


def _parse_boolean_label(value: str, row_number: int) -> bool:
    normalized_value = value.strip().lower()
    if normalized_value in TRUE_VALUES:
        return True
    if normalized_value in FALSE_VALUES:
        return False

    raise PHMDatasetValidationError(
        f"Row {row_number}: failureWithinHorizon must be true/false or 1/0."
    )
