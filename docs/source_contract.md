# ITviec source contract

Verified against public pages on 7 November 2026. TopDev is not integrated: the tested endpoint did not expose enough reliable public fields. A connector should not be advertised in configuration before its implementation is verified.

## Listing pages

- Base URL: `https://itviec.com/it-jobs`, paginated with `?page=N`.
- Card selector: `.job-card[data-job-key]`. The UUID in `data-job-key` is the source identity; the final four digits of a slug are not used as the key.
- Title: `h3 a`; company: `/companies/` link; skills: elements with `data-responsive-tag-list-target=tag`.
- Read only public salary content. When `.sign-in-view-salary` exists, preserve NULL and do not use authenticated salary data.
- Determine the last page from pagination. If the required page count exceeds the default 100-page safety limit, fail rather than publish a truncated snapshot. Repeated pages, empty pages, or collection below 90% of the advertised total are rejected. The 90% threshold tolerates listing changes during collection; it does not prove absolute coverage.

## Detail pages

- Each detail URL must expose `JobPosting` JSON-LD, including objects nested in `@graph`.
- Read publication dates from `datePosted`, not a relative-age label on a card.
- Read the company name from `hiringOrganization.name` and city values from `jobLocation[].address.addressRegion`.
- Preserve source skills; perform alias mapping and deduplication in Silver.
- Do not read applicant profiles, submit applications, sign in, or bypass blocked pages. HTTP 403 or source-contract changes fail the run.

HTTP uses 10-second connection and 45-second read timeouts, up to three retries for 429/5xx responses, Retry-After handling, and request spacing of at least 0.5 seconds (one second by default). A full snapshot can take more than ten minutes; the first listing page alone is not a complete extraction.

## Raw batch

`jobs.parquet` contains source identities/payloads, publication dates, skills/locations as JSON strings, parsed salary fields, FX observations, and collection metadata. `manifest.json` records schema_version, complete, run_id, snapshot_date, row_count, the Parquet checksum, collection timestamps, and source page counts.

Only batches with completed manifests and matching checksums may be uploaded or loaded into Bronze. Each run has a separate path. Replay preserves the original snapshot date; source failures never trigger synthetic-data generation.
