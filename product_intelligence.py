"""Explainable, local machine-learning helpers for ProductPulse AI.

TF-IDF learns vocabulary from example customer language and scores incoming
feedback against theme prototypes. This is similarity-based classification,
not an LLM, and all output is advisory until a PM reviews it.
"""
from __future__ import annotations

import math
from typing import Mapping

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

THEME_EXAMPLES: Mapping[str, tuple[str, ...]] = {
    "Checkout": (
        "checkout freezes when applying a coupon",
        "payment fails during checkout",
        "cannot pay after entering a discount code",
        "purchase transaction crashes on mobile",
        "card payment checkout error",
    ),
    "Appearance": (
        "please add a dark mode theme",
        "dark theme for nighttime use",
        "change the color of the dashboard",
        "customize appearance and interface colors",
    ),
    "Reporting": (
        "export report as a CSV file",
        "download analytics reports to Excel",
        "schedule downloadable finance reports",
        "data export and spreadsheet reporting",
    ),
    "Search": (
        "search cannot find saved projects",
        "search results are not relevant",
        "find projects with advanced filters",
        "improve search relevance for project names",
    ),
    "Collaboration": (
        "invite teammates with access permissions",
        "role based access control for teams",
        "share workspace with colleagues",
        "assign admin editor and viewer roles",
    ),
    "Performance": (
        "mobile dashboard loads slowly",
        "pages have long loading times",
        "improve app speed and response time",
        "dashboard lags on my phone",
    ),
}

REQUIRED_COLUMNS = {"feedback", "segment"}
VALID_SEGMENTS = {"Enterprise", "SMB", "Startup"}


def validate_feedback_upload(frame: pd.DataFrame) -> pd.DataFrame:
    """Normalize a user CSV without trusting its schema or classification."""
    frame = frame.copy()
    frame.columns = [str(c).strip().lower() for c in frame.columns]
    missing = REQUIRED_COLUMNS - set(frame.columns)
    if missing:
        raise ValueError("CSV must contain feedback and segment columns.")
    if len(frame) > 10000:
        raise ValueError("Upload at most 10,000 feedback rows.")
    frame = frame.dropna(subset=["feedback"])
    frame["feedback"] = frame["feedback"].astype(str).str.strip()
    frame = frame[frame["feedback"].str.len().between(3, 2000)]
    if frame.empty:
        raise ValueError("No valid feedback text found.")
    frame["segment"] = frame["segment"].fillna("Unknown").astype(str).str.strip()
    frame.loc[~frame["segment"].isin(VALID_SEGMENTS), "segment"] = "Unknown"
    if "urgent" not in frame:
        frame["urgent"] = 0
    frame["urgent"] = frame["urgent"].astype(str).str.lower().isin(
        {"1", "true", "yes", "urgent"}
    ).astype(int)
    frame = frame.reset_index(drop=True)
    frame["id"] = [f"U{i:05d}" for i in range(1, len(frame) + 1)]
    frame["theme"] = "Needs review"
    return frame[["id", "feedback", "theme", "segment", "urgent"]]


def suggest_themes(texts: list[str], min_similarity: float = 0.18) -> pd.DataFrame:
    """Return top theme, similarity and review state for each text.

    Scores represent cosine similarity to a theme's training examples, *not*
    calibrated probabilities or evidence of real-world classifier accuracy.
    """
    if not 0 <= min_similarity <= 1:
        raise ValueError("min_similarity must be within 0 and 1")
    if not texts:
        return pd.DataFrame(columns=["suggested_theme", "similarity", "review"])
    theme_names = list(THEME_EXAMPLES)
    examples = [(theme, example) for theme, group in THEME_EXAMPLES.items() for example in group]
    corpus = [example for _, example in examples] + [str(t) for t in texts]
    vectorizer = TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True, strip_accents="unicode")
    vectors = vectorizer.fit_transform(corpus)
    exemplar_vectors = vectors[: len(examples)]
    incoming_vectors = vectors[len(examples):]
    sims = cosine_similarity(incoming_vectors, exemplar_vectors)
    result = []
    for row in sims:
        theme_scores = {
            name: float(max(score for score, (theme, _) in zip(row, examples) if theme == name))
            for name in theme_names
        }
        winner = max(theme_scores, key=theme_scores.get)
        similarity = theme_scores[winner]
        result.append({
            "suggested_theme": winner if similarity >= min_similarity else "Needs review",
            "similarity": round(similarity, 3),
            "review": "Suggested — verify" if similarity >= min_similarity else "Uncertain — manual review",
        })
    return pd.DataFrame(result)


def rice_score(reach: float, impact: float, confidence: float, effort: float) -> float:
    """Pure RICE calculation; returns NaN for invalid estimates."""
    inputs = [reach, impact, confidence, effort]
    try:
        values = [float(value) for value in inputs]
    except (ValueError, TypeError):
        return math.nan
    r, i, c, e = values
    if not all(math.isfinite(v) for v in values) or r < 0 or i < 0 or not 0 <= c <= 1 or e <= 0:
        return math.nan
    return round(r * i * c / e, 1)


def rank_initiatives(frame: pd.DataFrame) -> pd.DataFrame:
    """Rank well-formed initiatives while dropping invalid estimates."""
    result = frame.copy()
    for field in ["reach", "impact", "confidence", "effort"]:
        result[field] = pd.to_numeric(result[field], errors="coerce")
    result["RICE"] = [
        rice_score(r, i, c, e)
        for r, i, c, e in zip(
            result["reach"], result["impact"], result["confidence"], result["effort"]
        )
    ]
    return result.dropna(subset=["RICE"]).sort_values("RICE", ascending=False)
