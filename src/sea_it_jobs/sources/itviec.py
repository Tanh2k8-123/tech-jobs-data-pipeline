import json
import logging
import math
import re
from datetime import date
from urllib.parse import parse_qs, urlparse

from bs4 import BeautifulSoup

from sea_it_jobs.http import HttpClient

LOG = logging.getLogger(__name__)
BASE_URL = "https://itviec.com"


def parse_listing(html: str):
    soup = BeautifulSoup(html, "html.parser")
    cards = []
    for node in soup.select(".job-card[data-job-key]"):
        title = node.select_one("h3 a")
        company = node.select_one("a[href^='/companies/']")
        if title is None or company is None:
            raise ValueError("ITviec card contract changed: missing title/company")
        slug = node.get("data-search--job-selection-job-slug-value")
        if not slug:
            raise ValueError("ITviec card contract changed: missing detail slug")
        salary = node.select_one(".salary")
        hidden = salary is None or salary.select_one(".sign-in-view-salary") is not None
        cards.append(
            {
                "source_job_id": node["data-job-key"],
                "title": title.get_text(" ", strip=True),
                "company_id": urlparse(company["href"]).path.removeprefix("/companies/"),
                "url": f"{BASE_URL}/it-jobs/{slug}",
                "salary_text": None if hidden else salary.get_text(" ", strip=True),
                "salary_hidden": hidden,
                "skills": [
                    tag.get_text(" ", strip=True)
                    for tag in node.select("[data-responsive-tag-list-target='tag']")
                ],
            }
        )
    if not cards:
        raise ValueError("No job cards: source unavailable or HTML contract changed")
    pages = [1]
    for link in soup.select("a[href]"):
        query = parse_qs(urlparse(link["href"]).query)
        if "page" in query and query["page"][0].isdigit():
            pages.append(int(query["page"][0]))
    description = soup.select_one("meta[name='description']")
    match = (
        re.match(r"([\d,]+) top IT jobs", description.get("content", "")) if description else None
    )
    advertised_total = int(match[1].replace(",", "")) if match else None
    return cards, max(pages), advertised_total


def job_posting_json(html: str) -> dict:
    soup = BeautifulSoup(html, "html.parser")

    def search(value):
        if isinstance(value, dict):
            types = value.get("@type", [])
            if types == "JobPosting" or isinstance(types, list) and "JobPosting" in types:
                return value
            for child in value.values():
                found = search(child)
                if found:
                    return found
        elif isinstance(value, list):
            for child in value:
                found = search(child)
                if found:
                    return found
        return None

    for node in soup.select("script[type='application/ld+json']"):
        try:
            found = search(json.loads(node.get_text()))
        except json.JSONDecodeError:
            continue
        if found:
            return found
    raise ValueError("Missing public JobPosting JSON-LD; source contract changed")


def parse_detail(html: str, card: dict, snapshot_date: str) -> dict:
    posting = job_posting_json(html)
    organization = posting.get("hiringOrganization", {})
    company_name = organization.get("name")
    if not company_name:
        raise ValueError("Missing hiringOrganization.name")
    posted_date = posting.get("datePosted")
    if posted_date:
        posted_date = date.fromisoformat(posted_date[:10]).isoformat()
        if posted_date > snapshot_date:
            raise ValueError("Source datePosted is in the future")
    places = posting.get("jobLocation", [])
    if isinstance(places, dict):
        places = [places]
    locations = []
    for place in places:
        address = place.get("address", {})
        city = address.get("addressRegion") or address.get("addressLocality")
        if city and city != "Not Available":
            locations.append(city)
    salary = posting.get("baseSalary") or {}
    salary_value = salary.get("value") or {}
    if not isinstance(salary_value, dict):
        salary_value = {}
    period = {"MONTH": "month", "YEAR": "year", "HOUR": "hour"}.get(
        str(salary_value.get("unitText", "")).upper()
    )
    return {
        "source": "itviec",
        "source_job_id": card["source_job_id"],
        "job_url": card["url"],
        "company_id": card["company_id"],
        "company_name": company_name,
        "title": card["title"],
        "salary_text": card["salary_text"],
        "salary_period": period,
        "salary_basis": "unknown",
        "salary_currency_hint": salary.get("currency") if not card["salary_hidden"] else None,
        "locations": sorted(set(locations)) or ["Unknown"],
        "skills": card["skills"],
        "posted_date": posted_date,
        "valid_through": posting.get("validThrough"),
        "source_payload": {"listing": card, "job_posting": posting},
    }


def extract(client: HttpClient, snapshot_date: str, max_pages: int = 100):
    first = client.get(BASE_URL + "/it-jobs", check_robots=True)
    first_cards, page_count, advertised_total = parse_listing(first.text)
    if page_count > max_pages:
        raise ValueError("Pagination exceeds safety limit; extraction was not published")
    cards_by_id = {card["source_job_id"]: card for card in first_cards}
    fingerprints = {tuple(sorted(cards_by_id))}
    for page in range(2, page_count + 1):
        response = client.get(f"{BASE_URL}/it-jobs?page={page}", check_robots=True)
        cards, _, _ = parse_listing(response.text)
        fingerprint = tuple(sorted(card["source_job_id"] for card in cards))
        if fingerprint in fingerprints:
            raise ValueError("Repeated pagination page; refusing a truncated snapshot")
        fingerprints.add(fingerprint)
        cards_by_id.update((card["source_job_id"], card) for card in cards)
        LOG.info(
            "listing_page_complete page=%s total_pages=%s unique_jobs=%s",
            page,
            page_count,
            len(cards_by_id),
        )
    if advertised_total and len(cards_by_id) < math.ceil(advertised_total * 0.9):
        raise ValueError("Collected fewer than 90% of advertised jobs; investigate pagination")
    jobs = []
    for index, card in enumerate(cards_by_id.values(), 1):
        response = client.get(card["url"], check_robots=True)
        jobs.append(parse_detail(response.text, card, snapshot_date))
        if index % 20 == 0:
            LOG.info("details_complete count=%s total=%s", index, len(cards_by_id))
    return jobs, {
        "listing_pages": page_count,
        "advertised_total": advertised_total,
        "collected_jobs": len(jobs),
        "source": "itviec",
    }
