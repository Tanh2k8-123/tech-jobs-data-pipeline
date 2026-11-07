import json

from sql_harness import ROOT


def test_dashboard_charts_reference_declared_datasets():
    dashboard = json.loads(
        (ROOT / "dashboards/market.lvdash.json.tftpl").read_text(encoding="utf-8")
    )
    names = {dataset["name"] for dataset in dashboard["datasets"]}
    charts = [
        item["widget"] for item in dashboard["pages"][0]["layout"] if "spec" in item["widget"]
    ]
    assert {chart["spec"]["widgetType"] for chart in charts} >= {"bar", "line"}
    for chart in charts:
        assert chart["queries"][0]["query"]["datasetName"] in names
        fields = {field["name"] for field in chart["queries"][0]["query"]["fields"]}
        assert all(
            encoding["fieldName"] in fields for encoding in chart["spec"]["encodings"].values()
        )
