# Source rules

The ITviec adapter was checked on 7 November 2026. TopDev is not integrated.

## What the parser reads

| Field | Location |
|---|---|
| Source ID | `.job-card[data-job-key]` |
| Title | `h3 a` |
| Company ID | `/companies/` link |
| Skills | `data-responsive-tag-list-target=tag` |
| Publication date | `datePosted` in JobPosting JSON-LD |
| Company name | `hiringOrganization.name` |
| City | `jobLocation[].address.addressRegion`, with addressLocality as a fallback |

The listing URL is `https://itviec.com/it-jobs?page=N`. The adapter visits every page it finds, then reads each detail page. Salaries behind `.sign-in-view-salary` stay NULL.

## When collection fails

The run fails for missing cards/JobPosting data, repeated or empty pages, more pages than the limit (100 by default), or a collected count below 90% of the advertised total. This count check allows some listing changes during collection; it does not prove full coverage.

Requests check robots.txt and wait one second by default, with a 0.5-second minimum. Connection/read timeouts are 10/45 seconds. The client retries 429/5xx up to three times and respects Retry-After. It does not sign in or bypass blocked pages.

Only a completed manifest with a matching Parquet checksum can enter Bronze. Source failures do not create replacement data.
