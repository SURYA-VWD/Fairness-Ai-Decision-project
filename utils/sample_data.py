"""
utils/sample_data.py
Generate realistic synthetic datasets for demo purposes.
"""

import numpy as np
import pandas as pd


def generate_hiring_dataset(n: int = 5000, seed: int = 42) -> pd.DataFrame:
    """Synthetic hiring dataset with gender bias baked in."""
    rng = np.random.default_rng(seed)

    gender = rng.choice(["Male", "Female", "Non-binary"], p=[0.52, 0.44, 0.04], size=n)
    age    = rng.integers(22, 60, size=n)

    experience = rng.integers(0, 20, size=n)
    education  = rng.choice(["Bachelor's", "Master's", "PhD", "High School"],
                            p=[0.45, 0.30, 0.10, 0.15], size=n)

    # Career gap — correlated with gender (proxy feature)
    career_gap = np.where(
        gender == "Female",
        rng.integers(0, 5, size=n),
        rng.integers(0, 2, size=n),
    )

    test_score = rng.integers(40, 100, size=n)
    gpa        = np.round(rng.uniform(2.0, 4.0, size=n), 2)

    # True merit-based probability
    merit = (
        0.30 * (experience / 20)
        + 0.25 * (test_score / 100)
        + 0.20 * ((gpa - 2.0) / 2.0)
        + 0.15 * (education == "Master's").astype(float)
        + 0.10 * (education == "PhD").astype(float)
    )

    # Inject gender bias: female/non-binary get a penalty
    bias_penalty = np.where(gender == "Female", 0.15, 0.0)
    bias_penalty = np.where(gender == "Non-binary", 0.20, bias_penalty)

    prob = np.clip(merit - bias_penalty + rng.normal(0, 0.05, n), 0.05, 0.95)
    hired = (rng.random(n) < prob).astype(int)

    return pd.DataFrame({
        "gender": gender,
        "age": age,
        "years_experience": experience,
        "education": education,
        "career_gap_years": career_gap,
        "test_score": test_score,
        "gpa": gpa,
        "hired": hired,
    })


def generate_loan_dataset(n: int = 4000, seed: int = 7) -> pd.DataFrame:
    """Synthetic loan approval dataset with race-based bias."""
    rng = np.random.default_rng(seed)

    race = rng.choice(
        ["White", "Black", "Hispanic", "Asian", "Other"],
        p=[0.52, 0.18, 0.16, 0.10, 0.04], size=n
    )

    income       = rng.integers(20000, 150000, size=n)
    credit_score = rng.integers(400, 850, size=n)
    loan_amount  = rng.integers(5000, 500000, size=n)
    dti_ratio    = np.round(rng.uniform(0.10, 0.60, size=n), 2)
    employment   = rng.choice(["Employed", "Self-employed", "Unemployed"],
                              p=[0.70, 0.20, 0.10], size=n)
    zip_risk     = rng.choice(["Low", "Medium", "High"], size=n)

    merit = (
        0.35 * ((credit_score - 400) / 450)
        + 0.30 * (income / 150000)
        + 0.20 * (1 - dti_ratio)
        + 0.10 * (employment == "Employed").astype(float)
        + 0.05 * (zip_risk == "Low").astype(float)
    )

    bias_penalty = np.where(race == "Black",    0.12, 0.0)
    bias_penalty = np.where(race == "Hispanic", 0.08, bias_penalty)

    prob = np.clip(merit - bias_penalty + rng.normal(0, 0.04, n), 0.05, 0.95)
    approved = (rng.random(n) < prob).astype(int)

    return pd.DataFrame({
        "race": race,
        "income": income,
        "credit_score": credit_score,
        "loan_amount": loan_amount,
        "debt_to_income": dti_ratio,
        "employment_status": employment,
        "zip_risk_category": zip_risk,
        "loan_approved": approved,
    })


def generate_recidivism_dataset(n: int = 3000, seed: int = 99) -> pd.DataFrame:
    """Synthetic criminal justice dataset inspired by COMPAS-style data."""
    rng = np.random.default_rng(seed)

    race = rng.choice(["White", "Black", "Hispanic"], p=[0.40, 0.40, 0.20], size=n)
    age  = rng.integers(18, 65, size=n)

    prior_counts  = rng.integers(0, 10, size=n)
    charge_degree = rng.choice(["Felony", "Misdemeanor"], p=[0.35, 0.65], size=n)
    days_in_jail  = rng.integers(0, 365, size=n)

    merit = (
        0.40 * (prior_counts / 10)
        + 0.30 * (charge_degree == "Felony").astype(float)
        + 0.20 * (days_in_jail / 365)
        + 0.10 * ((65 - age) / 47)
    )

    bias_penalty = np.where(race == "Black", 0.10, 0.0)

    prob = np.clip(merit + bias_penalty + rng.normal(0, 0.05, n), 0.05, 0.95)
    recidivated = (rng.random(n) < prob).astype(int)

    return pd.DataFrame({
        "race": race,
        "age": age,
        "prior_convictions": prior_counts,
        "charge_degree": charge_degree,
        "days_in_jail": days_in_jail,
        "two_year_recid": recidivated,
    })


SAMPLE_DATASETS = {
    "🏢 Hiring (Gender bias)": {
        "generator": generate_hiring_dataset,
        "target": "hired",
        "sensitive": "gender",
        "description": "Resume screening model with gender-based disparities in hiring rates.",
    },
    "🏦 Loan Approval (Race bias)": {
        "generator": generate_loan_dataset,
        "target": "loan_approved",
        "sensitive": "race",
        "description": "Loan approval model with racial disparities in approval rates.",
    },
    "⚖️ Recidivism (Race bias)": {
        "generator": generate_recidivism_dataset,
        "target": "two_year_recid",
        "sensitive": "race",
        "description": "Criminal justice risk assessment with racial disparities (COMPAS-inspired).",
    },
}
