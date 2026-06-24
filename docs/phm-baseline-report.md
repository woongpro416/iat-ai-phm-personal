# PHM Baseline Report

## Summary

- Model version: `phm-rf-baseline-v1`
- Model type: `RandomForestClassifier`
- Dataset path: `datasets/phm/sample_phm_training.csv`
- Prediction target: `failureWithinHorizon`
- Rolling window size: `12`
- Prediction horizon: `24` hours
- Decision threshold: `0.5`
- Artifact path: `model_artifacts/phm/phm_rf_v1.joblib`

## Feature Names

```text
temperature
vibration
noise
temperatureRollingMean12
temperatureRollingStd12
vibrationRollingMean12
vibrationRollingStd12
noiseRollingMean12
noiseRollingStd12
```

## Split Summary

| Split | Raw rows | Training-ready rows | Devices | Positive labels | Negative labels | Period |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| Train | 432 | 426 | 3 | 83 | 349 | 2026-01-01T00:00:00+00:00 ~ 2026-01-06T23:00:00+00:00 |
| Validation | 36 | 30 | 3 | 21 | 15 | 2026-01-08T00:00:00+00:00 ~ 2026-01-08T11:00:00+00:00 |
| Test | 108 | 102 | 3 | 59 | 49 | 2026-01-09T12:00:00+00:00 ~ 2026-01-10T23:00:00+00:00 |

- Purged rows: `144`
- Validation start: `2026-01-08T00:00:00+00:00`
- Test start: `2026-01-09T12:00:00+00:00`

## Validation Metrics

```json
{
  "precision": 1.0,
  "recall": 1.0,
  "f1": 1.0,
  "roc_auc": 1.0,
  "pr_auc": 1.0,
  "false_alarm_rate": 0.0,
  "true_negative": 13,
  "false_positive": 0,
  "false_negative": 0,
  "true_positive": 17
}
```

## Test Metrics

```json
{
  "precision": 1.0,
  "recall": 0.963636,
  "f1": 0.981481,
  "roc_auc": 0.98646,
  "pr_auc": 0.992724,
  "false_alarm_rate": 0.0,
  "true_negative": 47,
  "false_positive": 0,
  "false_negative": 2,
  "true_positive": 53
}
```

## Notes

- The current checked-in sample CSV is deterministic synthetic data for portfolio demonstration.
- Metrics from synthetic data should not be presented as real field performance.
- This model is a portfolio baseline and does not replace `phm-rule-baseline-v1` in the FastAPI runtime yet.
- Rolling features are calculated from previous rows only to reduce leakage risk.
- The test split should be used once for final evaluation after model and threshold selection.
