from dataclasses import dataclass
from datetime import datetime

from training.phm_dataset_splitter import PHMTimeSplitResult


@dataclass(frozen=True)
class PHMSplitSummary:
    name: str
    row_count: int
    device_count: int
    sampled_at_start: datetime
    sampled_at_end: datetime
    positive_label_count: int
    negative_label_count: int
    positive_label_ratio: float


@dataclass(frozen=True)
class PHMSplitQualityReport:
    train: PHMSplitSummary
    validation: PHMSplitSummary
    test: PHMSplitSummary
    purged_row_count: int
    issues: tuple[str, ...]

    @property
    def is_training_ready(self) -> bool:
        return not self.issues


class PHMSplitQualityError(ValueError):
    """Raised when split data is not suitable for model training."""


def analyze_split_quality(
    split_result: PHMTimeSplitResult,
) -> PHMSplitQualityReport:
    train_summary = _summarize_split("train", split_result.train_rows)
    validation_summary = _summarize_split(
        "validation",
        split_result.validation_rows,
    )
    test_summary = _summarize_split("test", split_result.test_rows)

    issues = []
    for summary in (train_summary, validation_summary, test_summary):
        issues.extend(_find_label_issues(summary))

    issues.extend(
        _find_time_order_issues(
            train_summary=train_summary,
            validation_summary=validation_summary,
            test_summary=test_summary,
        )
    )

    return PHMSplitQualityReport(
        train=train_summary,
        validation=validation_summary,
        test=test_summary,
        purged_row_count=len(split_result.purged_rows),
        issues=tuple(issues),
    )


def ensure_training_ready(report: PHMSplitQualityReport) -> None:
    if report.is_training_ready:
        return

    raise PHMSplitQualityError(
        "PHM split quality validation failed: " + " | ".join(report.issues)
    )


def _summarize_split(
    split_name: str,
    rows: tuple[dict[str, str], ...],
) -> PHMSplitSummary:
    if not rows:
        raise PHMSplitQualityError(f"{split_name} split is empty.")

    device_ids = {int(row["deviceId"]) for row in rows}
    sampled_times = tuple(
        _parse_timestamp(row["sampledAt"])
        for row in rows
    )
    labels = tuple(
        _parse_label(row["failureWithinHorizon"])
        for row in rows
    )
    positive_label_count = sum(labels)
    negative_label_count = len(labels) - positive_label_count

    return PHMSplitSummary(
        name=split_name,
        row_count=len(rows),
        device_count=len(device_ids),
        sampled_at_start=min(sampled_times),
        sampled_at_end=max(sampled_times),
        positive_label_count=positive_label_count,
        negative_label_count=negative_label_count,
        positive_label_ratio=round(
            positive_label_count / len(labels),
            6,
        ),
    )


def _find_label_issues(summary: PHMSplitSummary) -> list[str]:
    issues = []

    if summary.positive_label_count == 0:
        issues.append(
            f"{summary.name} split has no positive failure labels."
        )

    if summary.negative_label_count == 0:
        issues.append(
            f"{summary.name} split has no negative normal labels."
        )

    return issues


def _find_time_order_issues(
    train_summary: PHMSplitSummary,
    validation_summary: PHMSplitSummary,
    test_summary: PHMSplitSummary,
) -> list[str]:
    issues = []

    if train_summary.sampled_at_end >= validation_summary.sampled_at_start:
        issues.append(
            "train and validation timestamps overlap or are out of order."
        )

    if validation_summary.sampled_at_end >= test_summary.sampled_at_start:
        issues.append(
            "validation and test timestamps overlap or are out of order."
        )

    return issues


def _parse_timestamp(value: str) -> datetime:
    return datetime.fromisoformat(value.strip().replace("Z", "+00:00"))


def _parse_label(value: str) -> bool:
    return value.strip().lower() in {"true", "1"}
