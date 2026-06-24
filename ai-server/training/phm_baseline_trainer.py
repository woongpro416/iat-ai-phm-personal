import argparse
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path

from training.phm_dataset_splitter import PHMTimeSplitResult, split_training_csv
from training.phm_feature_engineering import (
    add_rolling_features,
    select_training_ready_rows,
)
from training.phm_model_input import (
    PHMModelInput,
    build_model_input,
    feature_names_for_window,
)
from training.phm_split_quality import (
    PHMSplitQualityReport,
    analyze_split_quality,
    ensure_training_ready,
)


DEFAULT_MODEL_VERSION = "phm-rf-baseline-v1"
DEFAULT_DECISION_THRESHOLD = 0.5


@dataclass(frozen=True)
class PHMEvaluationMetrics:
    precision: float
    recall: float
    f1: float
    roc_auc: float
    pr_auc: float
    false_alarm_rate: float
    true_negative: int
    false_positive: int
    false_negative: int
    true_positive: int


@dataclass(frozen=True)
class PHMBaselineTrainingResult:
    model_version: str
    artifact_path: str
    report_path: str
    feature_names: tuple[str, ...]
    train_row_count: int
    validation_row_count: int
    test_row_count: int
    validation_metrics: PHMEvaluationMetrics
    test_metrics: PHMEvaluationMetrics
    split_quality: PHMSplitQualityReport


def train_phm_random_forest_baseline(
    csv_path: str | Path,
    artifact_path: str | Path = "model_artifacts/phm/phm_rf_v1.joblib",
    report_path: str | Path = "../docs/phm-baseline-report.md",
    model_version: str = DEFAULT_MODEL_VERSION,
    window_size: int = 12,
    prediction_horizon_hours: int = 24,
    decision_threshold: float = DEFAULT_DECISION_THRESHOLD,
) -> PHMBaselineTrainingResult:
    _validate_decision_threshold(decision_threshold)

    split_result = split_training_csv(
        csv_path=csv_path,
        prediction_horizon=timedelta(hours=prediction_horizon_hours),
    )
    split_quality = analyze_split_quality(split_result)
    ensure_training_ready(split_quality)

    train_input = _prepare_model_input(split_result.train_rows, window_size)
    validation_input = _prepare_model_input(
        split_result.validation_rows,
        window_size,
    )
    test_input = _prepare_model_input(split_result.test_rows, window_size)

    model = _create_random_forest_classifier()
    model.fit(train_input.x, train_input.y)

    validation_probabilities = _positive_class_probabilities(
        model,
        validation_input,
    )
    test_probabilities = _positive_class_probabilities(model, test_input)

    validation_metrics = evaluate_binary_classifier(
        y_true=validation_input.y,
        y_probability=validation_probabilities,
        threshold=decision_threshold,
    )
    test_metrics = evaluate_binary_classifier(
        y_true=test_input.y,
        y_probability=test_probabilities,
        threshold=decision_threshold,
    )

    resolved_artifact_path = Path(artifact_path)
    resolved_report_path = Path(report_path)
    resolved_artifact_path.parent.mkdir(parents=True, exist_ok=True)
    resolved_report_path.parent.mkdir(parents=True, exist_ok=True)

    _save_model_artifact(
        artifact_path=resolved_artifact_path,
        model=model,
        model_version=model_version,
        feature_names=train_input.feature_names,
        window_size=window_size,
        prediction_horizon_hours=prediction_horizon_hours,
        decision_threshold=decision_threshold,
        validation_metrics=validation_metrics,
        test_metrics=test_metrics,
    )
    _write_training_report(
        report_path=resolved_report_path,
        csv_path=Path(csv_path),
        model_version=model_version,
        split_result=split_result,
        split_quality=split_quality,
        train_input=train_input,
        validation_input=validation_input,
        test_input=test_input,
        window_size=window_size,
        prediction_horizon_hours=prediction_horizon_hours,
        decision_threshold=decision_threshold,
        validation_metrics=validation_metrics,
        test_metrics=test_metrics,
        artifact_path=resolved_artifact_path,
    )

    return PHMBaselineTrainingResult(
        model_version=model_version,
        artifact_path=str(resolved_artifact_path),
        report_path=str(resolved_report_path),
        feature_names=train_input.feature_names,
        train_row_count=len(train_input.y),
        validation_row_count=len(validation_input.y),
        test_row_count=len(test_input.y),
        validation_metrics=validation_metrics,
        test_metrics=test_metrics,
        split_quality=split_quality,
    )


def evaluate_binary_classifier(
    y_true: tuple[int, ...],
    y_probability: tuple[float, ...],
    threshold: float = DEFAULT_DECISION_THRESHOLD,
) -> PHMEvaluationMetrics:
    _validate_decision_threshold(threshold)
    if len(y_true) != len(y_probability):
        raise ValueError("y_true and y_probability must have the same length.")
    if not y_true:
        raise ValueError("At least one evaluation row is required.")

    from sklearn.metrics import (
        average_precision_score,
        confusion_matrix,
        f1_score,
        precision_score,
        recall_score,
        roc_auc_score,
    )

    y_predicted = tuple(1 if probability >= threshold else 0 for probability in y_probability)
    true_negative, false_positive, false_negative, true_positive = (
        confusion_matrix(y_true, y_predicted, labels=[0, 1]).ravel()
    )
    normal_count = true_negative + false_positive
    false_alarm_rate = (
        false_positive / normal_count
        if normal_count
        else 0.0
    )

    return PHMEvaluationMetrics(
        precision=round(
            precision_score(y_true, y_predicted, zero_division=0),
            6,
        ),
        recall=round(recall_score(y_true, y_predicted, zero_division=0), 6),
        f1=round(f1_score(y_true, y_predicted, zero_division=0), 6),
        roc_auc=round(roc_auc_score(y_true, y_probability), 6),
        pr_auc=round(average_precision_score(y_true, y_probability), 6),
        false_alarm_rate=round(float(false_alarm_rate), 6),
        true_negative=int(true_negative),
        false_positive=int(false_positive),
        false_negative=int(false_negative),
        true_positive=int(true_positive),
    )


def _prepare_model_input(
    rows: tuple[dict[str, str], ...],
    window_size: int,
) -> PHMModelInput:
    featured_rows = add_rolling_features(rows, window_size=window_size)
    preparation_result = select_training_ready_rows(
        featured_rows,
        window_size=window_size,
    )
    if not preparation_result.ready_rows:
        raise ValueError(
            "No training-ready rows after rolling feature preparation. "
            "Use a longer dataset or a smaller window_size."
        )

    return build_model_input(
        preparation_result.ready_rows,
        feature_names=feature_names_for_window(window_size),
    )


def _create_random_forest_classifier():
    from sklearn.ensemble import RandomForestClassifier

    return RandomForestClassifier(
        n_estimators=200,
        max_depth=8,
        min_samples_leaf=3,
        class_weight="balanced",
        random_state=42,
    )


def _positive_class_probabilities(
    model,
    model_input: PHMModelInput,
) -> tuple[float, ...]:
    probabilities = model.predict_proba(model_input.x)
    class_to_index = {
        int(class_value): index
        for index, class_value in enumerate(model.classes_)
    }
    positive_class_index = class_to_index.get(1)
    if positive_class_index is None:
        raise ValueError("Trained model does not include the positive class.")

    return tuple(
        float(row_probabilities[positive_class_index])
        for row_probabilities in probabilities
    )


def _save_model_artifact(
    artifact_path: Path,
    model,
    model_version: str,
    feature_names: tuple[str, ...],
    window_size: int,
    prediction_horizon_hours: int,
    decision_threshold: float,
    validation_metrics: PHMEvaluationMetrics,
    test_metrics: PHMEvaluationMetrics,
) -> None:
    import joblib

    artifact = {
        "model": model,
        "modelVersion": model_version,
        "trainedAt": datetime.now(timezone.utc).isoformat(),
        "featureNames": feature_names,
        "windowSize": window_size,
        "predictionHorizonHours": prediction_horizon_hours,
        "decisionThreshold": decision_threshold,
        "validationMetrics": asdict(validation_metrics),
        "testMetrics": asdict(test_metrics),
    }
    joblib.dump(artifact, artifact_path)


def _write_training_report(
    report_path: Path,
    csv_path: Path,
    model_version: str,
    split_result: PHMTimeSplitResult,
    split_quality: PHMSplitQualityReport,
    train_input: PHMModelInput,
    validation_input: PHMModelInput,
    test_input: PHMModelInput,
    window_size: int,
    prediction_horizon_hours: int,
    decision_threshold: float,
    validation_metrics: PHMEvaluationMetrics,
    test_metrics: PHMEvaluationMetrics,
    artifact_path: Path,
) -> None:
    report = f"""# PHM Baseline Report

## Summary

- Model version: `{model_version}`
- Model type: `RandomForestClassifier`
- Dataset path: `{csv_path.as_posix()}`
- Prediction target: `failureWithinHorizon`
- Rolling window size: `{window_size}`
- Prediction horizon: `{prediction_horizon_hours}` hours
- Decision threshold: `{decision_threshold}`
- Artifact path: `{artifact_path.as_posix()}`

## Feature Names

```text
{chr(10).join(train_input.feature_names)}
```

## Split Summary

| Split | Raw rows | Training-ready rows | Devices | Positive labels | Negative labels | Period |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| Train | {split_quality.train.row_count} | {len(train_input.y)} | {split_quality.train.device_count} | {split_quality.train.positive_label_count} | {split_quality.train.negative_label_count} | {split_quality.train.sampled_at_start.isoformat()} ~ {split_quality.train.sampled_at_end.isoformat()} |
| Validation | {split_quality.validation.row_count} | {len(validation_input.y)} | {split_quality.validation.device_count} | {split_quality.validation.positive_label_count} | {split_quality.validation.negative_label_count} | {split_quality.validation.sampled_at_start.isoformat()} ~ {split_quality.validation.sampled_at_end.isoformat()} |
| Test | {split_quality.test.row_count} | {len(test_input.y)} | {split_quality.test.device_count} | {split_quality.test.positive_label_count} | {split_quality.test.negative_label_count} | {split_quality.test.sampled_at_start.isoformat()} ~ {split_quality.test.sampled_at_end.isoformat()} |

- Purged rows: `{split_quality.purged_row_count}`
- Validation start: `{split_result.validation_start.isoformat()}`
- Test start: `{split_result.test_start.isoformat()}`

## Validation Metrics

```json
{json.dumps(asdict(validation_metrics), ensure_ascii=False, indent=2)}
```

## Test Metrics

```json
{json.dumps(asdict(test_metrics), ensure_ascii=False, indent=2)}
```

## Notes

- The current checked-in sample CSV is deterministic synthetic data for portfolio demonstration.
- Metrics from synthetic data should not be presented as real field performance.
- This model is a portfolio baseline and does not replace `phm-rule-baseline-v1` in the FastAPI runtime yet.
- Rolling features are calculated from previous rows only to reduce leakage risk.
- The test split should be used once for final evaluation after model and threshold selection.
"""
    report_path.write_text(report, encoding="utf-8")


def _validate_decision_threshold(decision_threshold: float) -> None:
    if decision_threshold <= 0 or decision_threshold >= 1:
        raise ValueError("decision_threshold must be between 0 and 1.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Train a PHM RandomForest baseline from a contracted CSV.",
    )
    parser.add_argument("csv_path", help="Path to PHM training CSV.")
    parser.add_argument(
        "--artifact-path",
        default="model_artifacts/phm/phm_rf_v1.joblib",
        help="Path where the joblib artifact will be saved.",
    )
    parser.add_argument(
        "--report-path",
        default="../docs/phm-baseline-report.md",
        help="Path where the Markdown report will be saved.",
    )
    parser.add_argument(
        "--window-size",
        type=int,
        default=12,
        help="Rolling feature window size.",
    )
    parser.add_argument(
        "--prediction-horizon-hours",
        type=int,
        default=24,
        help="Prediction horizon used for split purge.",
    )
    parser.add_argument(
        "--decision-threshold",
        type=float,
        default=DEFAULT_DECISION_THRESHOLD,
        help="Probability threshold used for binary classification metrics.",
    )

    args = parser.parse_args()
    result = train_phm_random_forest_baseline(
        csv_path=args.csv_path,
        artifact_path=args.artifact_path,
        report_path=args.report_path,
        window_size=args.window_size,
        prediction_horizon_hours=args.prediction_horizon_hours,
        decision_threshold=args.decision_threshold,
    )

    print(
        json.dumps(
            {
                "modelVersion": result.model_version,
                "artifactPath": result.artifact_path,
                "reportPath": result.report_path,
                "testMetrics": asdict(result.test_metrics),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
