"""Build the role and skill analysis dashboard from versioned SQL queries."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ALL_ROLES = "All roles"


def parameter():
    return {
        "keyword": "role_family",
        "displayName": "Role family",
        "dataType": "STRING",
        "defaultSelection": {"values": {"dataType": "STRING", "values": [{"value": ALL_ROLES}]}},
    }


def dataset(name, filtered=True):
    text = (ROOT / "dashboards/queries" / f"{name}.sql").read_text(encoding="utf-8")
    value = {
        "name": name,
        "displayName": name.replace("_", " ").title(),
        "queryLines": text.splitlines(keepends=True),
    }
    if filtered:
        value["parameters"] = [parameter()]
    return value


def query(dataset_name, fields):
    return [
        {
            "name": "main_query",
            "query": {
                "datasetName": dataset_name,
                "fields": [{"name": field, "expression": f"`{field}`"} for field in fields],
                "disaggregated": True,
            },
        }
    ]


def position(widget, x, y, width, height):
    return {"widget": widget, "position": {"x": x, "y": y, "width": width, "height": height}}


def chart(name, dataset_name, kind, x, y, title, left, top, color=None, extra=()):
    fields = [x, y] + ([color] if color else []) + list(extra)
    encodings = {
        "x": {"fieldName": x, "scale": {"type": "temporal" if kind == "line" else "quantitative"}},
        "y": {
            "fieldName": y,
            "scale": {"type": "quantitative" if kind == "line" else "categorical"},
        },
    }
    labels = {
        "posting_count": "Observed postings",
        "role_family": "Role family",
        "snapshot_date": "Collected day",
        "skill_share_pct": "Posts mentioning skill (%)",
        "skill_name": "Skill",
    }
    encodings["x"]["displayName"] = labels[x]
    encodings["y"]["displayName"] = labels[y]
    if kind == "bar":
        encodings["y"]["scale"]["sort"] = {"by": "value"}
    if color:
        encodings["color"] = {"fieldName": color, "scale": {"type": "categorical"}}
        encodings["color"]["displayName"] = labels[color]
    if extra:
        encodings["extra"] = [
            {"fieldName": field, "displayName": field.replace("_", " ").title()} for field in extra
        ]
    return position(
        {
            "name": name,
            "queries": query(dataset_name, fields),
            "spec": {
                "version": 3,
                "widgetType": kind,
                "encodings": encodings,
                "frame": {"showTitle": True, "title": title},
            },
        },
        left,
        top,
        3,
        7,
    )


def counter(name, field, title, left):
    return position(
        {
            "name": name,
            "queries": query("role_summary", [field]),
            "spec": {
                "version": 2,
                "widgetType": "counter",
                "encodings": {"value": {"fieldName": field, "displayName": title}},
                "frame": {"showTitle": True, "title": title},
            },
        },
        left,
        5,
        2,
        2,
    )


def table(name, dataset_name, columns, top, height):
    return position(
        {
            "name": name,
            "queries": query(dataset_name, list(columns)),
            "spec": {
                "version": 2,
                "widgetType": "table",
                "encodings": {
                    "columns": [
                        {"fieldName": field, "displayName": label}
                        for field, label in columns.items()
                    ]
                },
                "frame": {
                    "showTitle": True,
                    "title": "Snapshot details"
                    if name == "snapshot_info"
                    else "Skills mentioned in postings by role",
                },
            },
        },
        0,
        top,
        6,
        height,
    )


def build():
    filtered = ["role_summary", "role_trend", "role_skills", "skill_trend", "role_skill_details"]
    datasets = [dataset(name) for name in filtered] + [dataset("role_ranking", filtered=False)]
    datasets.append(
        {
            "name": "role_options",
            "displayName": "Observed roles",
            "queryLines": [
                "SELECT 'All roles' AS role_family UNION ",
                "SELECT DISTINCT role_family FROM ",
                "${catalog}.${prefix}_gold.mart_daily_role_demand ",
                "WHERE posting_count > 0 ORDER BY role_family",
            ],
        }
    )
    layout = [
        position(
            {
                "name": "description",
                "multilineTextboxSpec": {
                    "lines": [
                        "## Vietnam IT Job Market: roles and skills\n\n",
                        "Select a role for trends and skills; ranking shows all roles. ",
                        "Each collected day uses its last complete batch.\n\n",
                        "Skills are public tags, not full requirements. ",
                        "Exact role-name tags are excluded. Labels use title rules; ",
                        "Other and multi-role titles need review. ",
                        "Short history is not a long-term trend. Source: ITviec. ",
                        "[Rates By Exchange Rate API](https://www.exchangerate-api.com)",
                    ]
                },
            },
            0,
            0,
            6,
            3,
        )
    ]
    filter_queries = [
        {
            "name": "role_choices",
            "query": {
                "datasetName": "role_options",
                "fields": [{"name": "role_family", "expression": "`role_family`"}],
                "disaggregated": False,
            },
        }
    ]
    bindings = [{"fieldName": "role_family", "displayName": "Role", "queryName": "role_choices"}]
    for name in filtered:
        filter_queries.append(
            {
                "name": "filter_" + name,
                "query": {
                    "datasetName": name,
                    "parameters": [{"name": "role_family", "keyword": "role_family"}],
                    "disaggregated": False,
                },
            }
        )
        bindings.append({"parameterName": "role_family", "queryName": "filter_" + name})
    layout.append(
        position(
            {
                "name": "role_filter",
                "queries": filter_queries,
                "spec": {
                    "version": 2,
                    "widgetType": "filter-single-select",
                    "encodings": {"fields": bindings},
                    "selection": {
                        "defaultSelection": {
                            "values": {"dataType": "STRING", "values": [{"value": ALL_ROLES}]}
                        }
                    },
                    "frame": {"showTitle": True, "title": "Role for trend and skill analysis"},
                },
            },
            0,
            3,
            6,
            2,
        )
    )
    layout.extend(
        [
            counter("posting_count", "posting_count", "Observed postings - latest snapshot", 0),
            counter("company_count", "company_count", "Companies - selected role", 2),
            counter("skill_count", "skill_count", "Skill tags - selected role", 4),
            table(
                "snapshot_info",
                "role_summary",
                {
                    "selected_role": "Selected role",
                    "snapshot_date": "Latest snapshot",
                    "data_collected_at": "Source collected at (UTC)",
                    "collected_days": "Collected days",
                    "unclassified_posts": "Unclassified posts",
                    "multiple_role_titles": "Multi-role titles",
                },
                7,
                3,
            ),
            chart(
                "role_ranking",
                "role_ranking",
                "bar",
                "posting_count",
                "role_family",
                "Top role families - all roles, latest snapshot",
                0,
                10,
            ),
            chart(
                "role_trend",
                "role_trend",
                "line",
                "snapshot_date",
                "posting_count",
                "Observed role demand - top 6 or selected role",
                3,
                10,
                "role_family",
            ),
            chart(
                "role_skills",
                "role_skills",
                "bar",
                "skill_share_pct",
                "skill_name",
                "Top 15 mentioned skills (% of selected role postings)",
                0,
                17,
                extra=("posting_count", "role_posting_count"),
            ),
            chart(
                "skill_trend",
                "skill_trend",
                "line",
                "snapshot_date",
                "skill_share_pct",
                "Skill mention share over collected days (%)",
                3,
                17,
                "skill_name",
                extra=("posting_count", "role_posting_count"),
            ),
            table(
                "role_skill_details",
                "role_skill_details",
                {
                    "role_family": "Role family",
                    "skill_name": "Skill",
                    "posting_count": "Postings with skill",
                    "role_posting_count": "Role postings",
                    "skill_share_pct": "Share (%)",
                },
                24,
                8,
            ),
        ]
    )
    return {
        "datasets": datasets,
        "pages": [
            {
                "name": "market",
                "displayName": "Roles and skills",
                "pageType": "PAGE_TYPE_CANVAS",
                "layout": layout,
            }
        ],
    }


if __name__ == "__main__":
    output = ROOT / "dashboards/market.lvdash.json.tftpl"
    output.write_text(json.dumps(build(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
