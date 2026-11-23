import math

import pandas as pd
import pytest

from product_intelligence import (
    rank_initiatives,
    rice_score,
    suggest_themes,
    validate_feedback_upload,
)


def test_rice_formula():
    assert rice_score(1000, 3, 0.8, 2) == 1200.0


@pytest.mark.parametrize("values", [
    (100, 2, 0.8, 0),
    (-1, 2, 0.8, 2),
    (100, 2, 1.1, 2),
    (100, 2, 0.8, float("inf")),
    ("invalid", 2, 0.8, 2),
])
def test_invalid_rice(values):
    assert math.isnan(rice_score(*values))


def test_ordering_and_validation():
    frame = pd.DataFrame([
        {"feature": "A", "reach": 100, "impact": 2, "confidence": 1, "effort": 1},
        {"feature": "B", "reach": 100, "impact": 1, "confidence": 1, "effort": 2},
        {"feature": "C", "reach": 10, "impact": 1, "confidence": 1, "effort": 0},
    ])
    ranked = rank_initiatives(frame)
    assert ranked.feature.tolist() == ["A", "B"]


def test_theme_suggestions_are_transparent():
    result = suggest_themes(["payment fails during checkout", "export report as CSV"])
    assert result.suggested_theme.tolist() == ["Checkout", "Reporting"]
    assert all(0 <= value <= 1 for value in result.similarity)


def test_uncertain_text_is_flagged():
    result = suggest_themes(["unrelated gibberish xyz qqq"], min_similarity=0.4)
    assert result.iloc[0]["suggested_theme"] == "Needs review"


def test_upload_rejects_missing_columns():
    with pytest.raises(ValueError):
        validate_feedback_upload(pd.DataFrame({"message": ["Something broke"]}))


def test_upload_normalizes_and_resets_ids():
    frame = pd.DataFrame({
        "feedback": ["Checkout hangs", "  ", "Export needed"],
        "segment": ["Enterprise", "Unknown source", "SMB"],
        "urgent": ["yes", "0", "true"],
    })
    clean = validate_feedback_upload(frame)
    assert len(clean) == 2
    assert clean.id.tolist() == ["U00001", "U00002"]
    assert clean.urgent.tolist() == [1, 1]
    assert clean.theme.tolist() == ["Needs review", "Needs review"]
