"""Build the versioned Lakeview template; Terraform substitutes catalog and prefix."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def build():
    skills_sql = (
        "SELECT skill_name, job_count, avg_salary_usd, salary_sample_count, salary_coverage "
        "FROM ${catalog}.${prefix}_gold.mart_skill_demand "
        "ORDER BY job_count DESC, skill_name LIMIT 15"
    )
    cities_sql = (
        "SELECT posted_date, city_name, job_count "
        "FROM ${catalog}.${prefix}_gold.mart_daily_city_jobs ORDER BY posted_date, city_name"
    )
    datasets = [
        {"name": "skills", "displayName": "Top 15 skills", "queryLines": [skills_sql]},
        {"name": "cities", "displayName": "Observed posting dates", "queryLines": [cities_sql]},
    ]
    layout = [
        {
            "widget": {
                "name": "description",
                "multilineTextboxSpec": {
                    "lines": [
                        "## Vietnam IT Job Market\n\n",
                        "Source: public ITviec postings. Demand counts postings present in the "
                        "latest complete snapshot. ",
                        "Salary is the mean advertised monthly midpoint; "
                        "NULL indicates insufficient salary data. ",
                        "The publication-date chart includes only observed postings; "
                        "a posting may belong to multiple cities.\n\n",
                        "[Rates By Exchange Rate API](https://www.exchangerate-api.com)",
                    ]
                },
            },
            "position": {"x": 0, "y": 0, "width": 6, "height": 3},
        }
    ]
    charts = [
        (
            "demand",
            "skills",
            "bar",
            "skill_name",
            "categorical",
            "job_count",
            None,
            "Top 15 skills by posting count",
            0,
            3,
        ),
        (
            "trend",
            "cities",
            "line",
            "posted_date",
            "temporal",
            "job_count",
            "city_name",
            "Observed postings by publication date and city",
            3,
            3,
        ),
        (
            "salary",
            "skills",
            "bar",
            "skill_name",
            "categorical",
            "avg_salary_usd",
            None,
            "Mean advertised salary (USD/month, both bounds required)",
            0,
            9,
        ),
        (
            "coverage",
            "skills",
            "bar",
            "skill_name",
            "categorical",
            "salary_coverage",
            None,
            "Salary midpoint coverage (0–1)",
            3,
            9,
        ),
    ]
    for name, dataset, kind, x, scale, y, color, title, left, top in charts:
        fields = [x, y] + ([color] if color else [])
        encodings = {
            "x": {"fieldName": x, "scale": {"type": scale}},
            "y": {"fieldName": y, "scale": {"type": "quantitative"}},
        }
        if color:
            encodings["color"] = {"fieldName": color, "scale": {"type": "categorical"}}
        layout.append(
            {
                "widget": {
                    "name": name,
                    "queries": [
                        {
                            "name": "main_query",
                            "query": {
                                "datasetName": dataset,
                                "fields": [
                                    {"name": field, "expression": f"`{field}`"} for field in fields
                                ],
                                "disaggregated": True,
                            },
                        }
                    ],
                    "spec": {
                        "version": 3,
                        "widgetType": kind,
                        "encodings": encodings,
                        "frame": {"showTitle": True, "title": title},
                    },
                },
                "position": {"x": left, "y": top, "width": 3, "height": 6},
            }
        )
    return {
        "datasets": datasets,
        "pages": [{"name": "market", "displayName": "Vietnam IT jobs", "layout": layout}],
    }


if __name__ == "__main__":
    output = ROOT / "dashboards/market.lvdash.json.tftpl"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(build(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
