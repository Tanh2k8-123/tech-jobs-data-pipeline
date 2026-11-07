import json
from types import SimpleNamespace

import pytest

from sea_it_jobs.sources.itviec import extract, parse_detail, parse_listing

LISTING = """
<meta name="description" content="1 top IT jobs for you">
<div class="job-card" data-job-key="uuid-1"
     data-search--job-selection-job-slug-value="data-engineer-company-1234">
  <h3><a>Data Engineer</a></h3><a href="/companies/company">Company</a>
  <div class="salary"><a class="sign-in-view-salary">Sign in to view salary</a></div>
  <a data-responsive-tag-list-target="tag">Python</a>
</div>
"""


def test_public_listing_identity_and_salary_visibility():
    cards, pages, count = parse_listing(LISTING)
    assert (pages, count) == (1, 1)
    assert cards[0]["source_job_id"] == "uuid-1"
    assert cards[0]["salary_text"] is None
    assert cards[0]["skills"] == ["Python"]


def test_detail_uses_exact_date_and_preserves_multiple_cities():
    card = parse_listing(LISTING)[0][0]
    posting = {
        "@type": "JobPosting",
        "datePosted": "2026-11-01",
        "hiringOrganization": {"name": "Company"},
        "jobLocation": [
            {"address": {"addressRegion": "Ha Noi"}},
            {"address": {"addressRegion": "Ho Chi Minh"}},
        ],
        "baseSalary": {"currency": "USD", "value": {"unitText": "MONTH"}},
    }
    html = '<script type="application/ld+json">' + json.dumps({"@graph": [posting]}) + "</script>"
    job = parse_detail(html, card, "2026-11-07")
    assert job["posted_date"] == "2026-11-01"
    assert job["locations"] == ["Ha Noi", "Ho Chi Minh"]
    assert job["salary_text"] is None
    assert job["salary_currency_hint"] is None


def test_changed_source_fails_instead_of_returning_sample_data():
    with pytest.raises(ValueError, match="No job cards"):
        parse_listing("<html>Access denied</html>")


def test_pagination_limit_never_publishes_a_partial_snapshot():
    class Client:
        def get(self, *args, **kwargs):
            return SimpleNamespace(text=LISTING + '<a href="/it-jobs?page=32">32</a>')

    with pytest.raises(ValueError, match="safety limit"):
        extract(Client(), "2026-11-07", max_pages=1)


def test_repeated_pagination_page_is_rejected():
    class Client:
        def get(self, *args, **kwargs):
            return SimpleNamespace(text=LISTING + '<a href="/it-jobs?page=2">2</a>')

    with pytest.raises(ValueError, match="Repeated pagination"):
        extract(Client(), "2026-11-07")
