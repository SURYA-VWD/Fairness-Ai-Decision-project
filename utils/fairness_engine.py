"""
utils/fairness_engine.py
Core fairness computation using fairlearn + scikit-learn.
"""

import numpy as np
import pandas as pd
from dataclasses import dataclass, field
from typing import Optional

from sklearn.metrics import (
    accuracy_score,
    precision_score, f1_score,
)

# fairlearn metric functions
from fairlearn.metrics import (
    demographic_parity_difference,
    demographic_parity_ratio,
    equalized_odds_difference,
    equal_opportunity_difference,
    MetricFrame,
    selection_rate,
    false_positive_rate,
    false_negative_rate,
    true_positive_rate,
)


# ── Result data classes ────────────────────────────────────────────────────────

@dataclass
class GroupStats:
    name: str
    n: int
    positive_rate: float
    tpr: float
    fpr: float
    fnr: float
    precision: float
    f1: float


@dataclass
class FairnessReport:
    # Core metrics
    demographic_parity_diff: float
    demographic_parity_ratio: float
    equalized_odds_diff: float
    equal_opportunity_diff: float
    disparate_impact_ratio: float

    # Per-group stats
    group_stats: list[GroupStats]

    # MetricFrame (raw fairlearn object)
    metric_frame: object

    # Proxy features
    proxy_features: list[dict]

    # Computed score 0-100 (100 = no bias)
    bias_score: float

    # Human-readable flags
    flags: list[dict]

    # Overall accuracy
    overall_accuracy: float
    overall_f1: float


# ── Main engine ────────────────────────────────────────────────────────────────

def compute_fairness(
    df: pd.DataFrame,
    target_col: str,
    sensitive_col: str,
    prediction_col: Optional[str] = None,
    model_type: str = "logistic",
    threshold: float = 0.80,
) -> FairnessReport:
    """
    Full fairness pipeline.

    If `prediction_col` is given we use those predictions directly.
    Otherwise we train a quick LogisticRegression on the remaining features.
    """
    from sklearn.pipeline import Pipeline
    from sklearn.preprocessing import StandardScaler, LabelEncoder
    from sklearn.linear_model import LogisticRegression
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.model_selection import train_test_split

    # ── Prepare labels ────────────────────────────────────────────────────────
    y = df[target_col].copy()
    sensitive = df[sensitive_col].copy()

    # Encode target if not binary int
    if y.dtype == object or str(y.dtype) == "category":
        le_y = LabelEncoder()
        y = pd.Series(le_y.fit_transform(y), index=df.index)

    # Cast sensitive to string for grouping
    sensitive = sensitive.astype(str)

    # ── Predictions ───────────────────────────────────────────────────────────
    if prediction_col and prediction_col in df.columns:
        y_pred = df[prediction_col].astype(int)
    else:
        feature_cols = [
            c for c in df.columns
            if c not in [target_col, sensitive_col, prediction_col]
        ]
        X = df[feature_cols].copy()

        # Drop columns with >50% missing
        X = X.dropna(axis=1, thresh=int(len(X) * 0.5))

        # Encode remaining categoricals
        for col in X.select_dtypes(include="object").columns:
            le = LabelEncoder()
            X[col] = le.fit_transform(X[col].astype(str))

        X = X.fillna(X.median(numeric_only=True))

        X_tr, X_te, y_tr, y_te, s_tr, s_te = train_test_split(
            X, y, sensitive, test_size=0.3, random_state=42, stratify=y
        )

        estimator = (
            RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
            if model_type == "random_forest"
            else LogisticRegression(max_iter=1000, random_state=42)
        )

        pipe = Pipeline([("scaler", StandardScaler()), ("clf", estimator)])
        pipe.fit(X_tr, y_tr)

        y_pred_full = pd.Series(pipe.predict(X), index=df.index)
        y      = y.loc[X_te.index]
        sensitive = sensitive.loc[X_te.index]
        y_pred = y_pred_full.loc[X_te.index]

    # ── fairlearn MetricFrame ─────────────────────────────────────────────────
    mf = MetricFrame(
        metrics={
            "selection_rate": selection_rate,
            "tpr": true_positive_rate,
            "fpr": false_positive_rate,
            "fnr": false_negative_rate,
        },
        y_true=y,
        y_pred=y_pred,
        sensitive_features=sensitive,
    )

    # ── Scalar fairness metrics ────────────────────────────────────────────────
    dp_diff  = demographic_parity_difference(y, y_pred, sensitive_features=sensitive)
    dp_ratio = demographic_parity_ratio(y, y_pred, sensitive_features=sensitive)
    eo_diff  = equalized_odds_difference(y, y_pred, sensitive_features=sensitive)
    eop_diff = equal_opportunity_difference(y, y_pred, sensitive_features=sensitive)

    # Disparate impact = min group selection rate / max group selection rate
    sr_by_group = mf.by_group["selection_rate"]
    di_ratio = float(sr_by_group.min() / sr_by_group.max()) if sr_by_group.max() > 0 else 0.0

    # ── Per-group stats ───────────────────────────────────────────────────────
    group_stats = []
    for grp in mf.by_group.index:
        mask = sensitive == grp
        y_g   = y[mask]
        yp_g  = y_pred[mask]
        if len(y_g) == 0:
            continue
        prec = precision_score(y_g, yp_g, zero_division=0)
        f1   = f1_score(y_g, yp_g, zero_division=0)
        row  = mf.by_group.loc[grp]
        group_stats.append(GroupStats(
            name=str(grp),
            n=int(mask.sum()),
            positive_rate=float(row["selection_rate"]),
            tpr=float(row["tpr"]),
            fpr=float(row["fpr"]),
            fnr=float(row["fnr"]),
            precision=prec,
            f1=f1,
        ))

    # ── Proxy feature detection ───────────────────────────────────────────────
    proxy_features = _detect_proxy_features(df, sensitive_col, target_col)

    # ── Bias score (0–100, higher = fairer) ───────────────────────────────────
    bias_score = _compute_bias_score(dp_ratio, di_ratio, abs(eo_diff), abs(eop_diff))

    # ── Flags ─────────────────────────────────────────────────────────────────
    flags = _generate_flags(
        dp_ratio, di_ratio, abs(eo_diff), abs(eop_diff),
        proxy_features, group_stats, threshold
    )

    # ── Overall metrics ───────────────────────────────────────────────────────
    overall_acc = accuracy_score(y, y_pred)
    overall_f1  = f1_score(y, y_pred, average="weighted", zero_division=0)

    return FairnessReport(
        demographic_parity_diff=float(dp_diff),
        demographic_parity_ratio=float(dp_ratio),
        equalized_odds_diff=float(eo_diff),
        equal_opportunity_diff=float(eop_diff),
        disparate_impact_ratio=float(di_ratio),
        group_stats=group_stats,
        metric_frame=mf,
        proxy_features=proxy_features,
        bias_score=bias_score,
        flags=flags,
        overall_accuracy=float(overall_acc),
        overall_f1=float(overall_f1),
    )


# ── Helpers ────────────────────────────────────────────────────────────────────

def _detect_proxy_features(
    df: pd.DataFrame, sensitive_col: str, target_col: str
) -> list[dict]:
    """Identify numeric features highly correlated with the sensitive attribute."""
    from sklearn.preprocessing import LabelEncoder

    results = []
    s = df[sensitive_col].copy()
    if s.dtype == object or str(s.dtype) == "category":
        s = pd.Series(LabelEncoder().fit_transform(s.astype(str)), index=df.index)

    num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    skip = {sensitive_col, target_col}
    for col in num_cols:
        if col in skip:
            continue
        try:
            corr = abs(df[col].fillna(df[col].median()).corr(s))
            if corr > 0.35:
                risk = "High" if corr > 0.6 else "Medium"
                results.append({"feature": col, "correlation": round(corr, 3), "risk": risk})
        except Exception:
            pass

    results.sort(key=lambda x: x["correlation"], reverse=True)
    return results[:8]


def _compute_bias_score(
    dp_ratio: float, di_ratio: float, eo_diff: float, eop_diff: float
) -> float:
    """Aggregate fairness score 0–100. Higher = fairer."""
    dp_s  = max(0.0, min(1.0, dp_ratio))   * 35
    di_s  = max(0.0, min(1.0, di_ratio))   * 35
    eo_s  = max(0.0, 1 - eo_diff)          * 15
    eop_s = max(0.0, 1 - eop_diff)         * 15
    return round(dp_s + di_s + eo_s + eop_s, 1)


def _generate_flags(
    dp_ratio, di_ratio, eo_diff, eop_diff,
    proxy_features, group_stats, threshold
) -> list[dict]:
    flags = []

    if dp_ratio < threshold:
        flags.append({
            "severity": "High",
            "title": "Demographic parity violation",
            "detail": (
                f"Demographic parity ratio is {dp_ratio:.2f}, below the {threshold} threshold. "
                "The model selects candidates at significantly different rates across groups."
            ),
        })

    if di_ratio < 0.80:
        flags.append({
            "severity": "High",
            "title": "Disparate impact — 4/5 rule violation",
            "detail": (
                f"Disparate impact ratio is {di_ratio:.2f} (< 0.80). "
                "This violates the EEOC 4/5 rule, a standard legal benchmark for hiring fairness."
            ),
        })

    if eo_diff > 0.10:
        flags.append({
            "severity": "Medium",
            "title": "Equalized odds gap",
            "detail": (
                f"Equalized odds difference is {eo_diff:.2f}. "
                "True positive and false positive rates differ meaningfully between groups."
            ),
        })

    if eop_diff > 0.10:
        flags.append({
            "severity": "Medium",
            "title": "Equal opportunity gap",
            "detail": (
                f"Equal opportunity difference is {eop_diff:.2f}. "
                "Qualified candidates from some groups are less likely to receive positive predictions."
            ),
        })

    for pf in proxy_features:
        if pf["risk"] == "High":
            flags.append({
                "severity": "High",
                "title": f"Proxy feature detected: '{pf['feature']}'",
                "detail": (
                    f"'{pf['feature']}' has a {pf['correlation']:.2f} correlation with the sensitive attribute. "
                    "It may be encoding demographic information indirectly."
                ),
            })

    # Small group warning
    total = sum(g.n for g in group_stats)
    for g in group_stats:
        if g.n < max(100, total * 0.05):
            flags.append({
                "severity": "Low",
                "title": f"Small sample: group '{g.name}'",
                "detail": (
                    f"Group '{g.name}' has only {g.n} samples ({g.n/total*100:.1f}% of data). "
                    "Metrics for this group may be unreliable."
                ),
            })

    return flags
