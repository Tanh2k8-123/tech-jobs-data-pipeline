import pytest

from sea_it_jobs.salary import parse_salary


@pytest.mark.parametrize(
    ("text", "low", "high", "kind"),
    [
        ("$1000 - $1800", 1000, 1800, "range"),
        ("Up to $3000", None, 3000, "upper_bound"),
        ("From $1500", 1500, None, "lower_bound"),
        ("$1,200", 1200, 1200, "fixed"),
        ("15 - 25 triệu", 15000000, 25000000, "range"),
        ("15,5 triệu", 15500000, 15500000, "fixed"),
        ("25.000.000 VNĐ", 25000000, 25000000, "fixed"),
    ],
)
def test_supported_salary_bounds(text, low, high, kind):
    result = parse_salary(text, "month")
    assert result["salary_min_native"] == low
    assert result["salary_max_native"] == high
    assert result["salary_type"] == kind
    assert result["salary_parse_status"] == "parsed"


@pytest.mark.parametrize("text", [None, "Thỏa thuận", "You'll love it", "Sign in to view salary"])
def test_hidden_salary_never_becomes_zero(text):
    result = parse_salary(text, "month")
    assert result["salary_min_native"] is None
    assert result["salary_max_native"] is None
    assert result["salary_parse_status"] == "undisclosed"


@pytest.mark.parametrize(
    "text",
    ["$3000 - $1000", "$1000 + bonus $500", "15 triệu USD", "Up to $1000 - $2000", "$1,23,456"],
)
def test_ambiguous_salary_is_not_guessed(text):
    result = parse_salary(text, "month")
    assert result["salary_parse_status"] == "unsupported"
    assert result["salary_min_native"] is None
    assert result["salary_max_native"] is None


def test_annual_salary_is_not_silently_treated_as_monthly():
    assert parse_salary("$30000 - $48000", "year")["salary_parse_status"] == "unsupported_period"


def test_missing_period_is_not_assumed_monthly():
    assert parse_salary("$1500", None)["salary_parse_status"] == "unsupported_period"
