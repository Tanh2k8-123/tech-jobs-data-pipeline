import json

from sql_harness import ROOT


def test_dashboard_charts_reference_declared_datasets():
    dashboard = json.loads(
        (ROOT / "dashboards/market.lvdash.json.tftpl").read_text(encoding="utf-8")
    )
    datasets = {dataset["name"]: dataset for dataset in dashboard["datasets"]}
    for dataset in datasets.values():
        for parameter in dataset.get("parameters", []):
            assert parameter.get("displayName")
    widgets = [
        item["widget"] for item in dashboard["pages"][0]["layout"] if "spec" in item["widget"]
    ]
    assert {widget["spec"]["widgetType"] for widget in widgets} >= {
        "bar",
        "line",
        "filter-single-select",
    }

    def bindings(value):
        if isinstance(value, dict):
            if "fieldName" in value or "parameterName" in value:
                yield value
            for child in value.values():
                yield from bindings(child)
        elif isinstance(value, list):
            for child in value:
                yield from bindings(child)

    for widget in widgets:
        queries = {item["name"]: item["query"] for item in widget["queries"]}
        fields = {field["name"] for item in queries.values() for field in item.get("fields", [])}
        for item in queries.values():
            assert item["datasetName"] in datasets
            if not widget["spec"]["widgetType"].startswith("filter-"):
                assert "parameters" not in item
        for binding in bindings(widget["spec"]["encodings"]):
            if "fieldName" in binding:
                assert binding["fieldName"] in fields
            else:
                query = queries[binding["queryName"]]
                assert binding["parameterName"] in {p["name"] for p in query.get("parameters", [])}
                assert binding["parameterName"] in {
                    p["keyword"] for p in datasets[query["datasetName"]]["parameters"]
                }
