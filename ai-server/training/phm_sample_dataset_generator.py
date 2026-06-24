import argparse
import csv
from datetime import datetime, timedelta, timezone
from pathlib import Path


DEFAULT_OUTPUT_PATH = "datasets/phm/sample_phm_training.csv"
DEVICE_IDS = (1, 2, 3)
HOUR_COUNT = 240
PREDICTION_HORIZON_HOURS = 24
SYNTHETIC_FAILURES = {
    1: (70, 176, 226),
    2: (118, 190, 232),
    3: (88, 160, 214),
}


def generate_sample_phm_training_csv(
    output_path: str | Path = DEFAULT_OUTPUT_PATH,
) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    start_at = datetime(2026, 1, 1, 0, 0, tzinfo=timezone.utc)

    with path.open("w", encoding="utf-8", newline="") as csv_file:
        writer = csv.DictWriter(
            csv_file,
            fieldnames=(
                "deviceId",
                "sampledAt",
                "temperature",
                "vibration",
                "noise",
                "failureWithinHorizon",
                "failureAt",
            ),
        )
        writer.writeheader()

        for hour in range(HOUR_COUNT):
            sampled_at = start_at + timedelta(hours=hour)
            for device_id in DEVICE_IDS:
                failure_at_hour = _next_failure_hour(device_id, hour)
                hours_to_failure = (
                    failure_at_hour - hour
                    if failure_at_hour is not None
                    else None
                )
                failure_within_horizon = (
                    hours_to_failure is not None
                    and 0 <= hours_to_failure <= PREDICTION_HORIZON_HOURS
                )

                writer.writerow(
                    {
                        "deviceId": device_id,
                        "sampledAt": sampled_at.isoformat(),
                        "temperature": f"{_temperature(device_id, hour, hours_to_failure):.2f}",
                        "vibration": f"{_vibration(device_id, hour, hours_to_failure):.3f}",
                        "noise": f"{_noise(device_id, hour, hours_to_failure):.2f}",
                        "failureWithinHorizon": str(failure_within_horizon).lower(),
                        "failureAt": _failure_at_text(
                            start_at,
                            failure_at_hour,
                            failure_within_horizon,
                        ),
                    }
                )

    return path


def _next_failure_hour(device_id: int, current_hour: int) -> int | None:
    for failure_hour in SYNTHETIC_FAILURES[device_id]:
        if current_hour <= failure_hour:
            return failure_hour

    return None


def _failure_pressure(hours_to_failure: int | None) -> float:
    if hours_to_failure is None:
        return 0.0

    if hours_to_failure < 0 or hours_to_failure > PREDICTION_HORIZON_HOURS:
        return 0.0

    return (PREDICTION_HORIZON_HOURS - hours_to_failure) / PREDICTION_HORIZON_HOURS


def _temperature(
    device_id: int,
    hour: int,
    hours_to_failure: int | None,
) -> float:
    baseline = 34.0 + device_id * 1.7 + (hour % 24) * 0.08
    pressure = _failure_pressure(hours_to_failure)
    return baseline + pressure * 28.0


def _vibration(
    device_id: int,
    hour: int,
    hours_to_failure: int | None,
) -> float:
    baseline = 0.16 + device_id * 0.035 + (hour % 12) * 0.004
    pressure = _failure_pressure(hours_to_failure)
    return baseline + pressure * 0.78


def _noise(
    device_id: int,
    hour: int,
    hours_to_failure: int | None,
) -> float:
    baseline = 46.0 + device_id * 1.5 + (hour % 18) * 0.12
    pressure = _failure_pressure(hours_to_failure)
    return baseline + pressure * 29.0


def _failure_at_text(
    start_at: datetime,
    failure_hour: int | None,
    failure_within_horizon: bool,
) -> str:
    if failure_hour is None or not failure_within_horizon:
        return ""

    return (start_at + timedelta(hours=failure_hour)).isoformat()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate a deterministic sample PHM training CSV.",
    )
    parser.add_argument(
        "--output-path",
        default=DEFAULT_OUTPUT_PATH,
        help="CSV path to write.",
    )
    args = parser.parse_args()

    output_path = generate_sample_phm_training_csv(args.output_path)
    print(f"Generated {output_path}")


if __name__ == "__main__":
    main()
