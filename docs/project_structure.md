# Cấu trúc thư mục

```text
sea-it-jobs-pipeline/
├── src/sea_it_jobs/       # CLI, HTTP, nguồn thật, parser, ingestion và SDK
│   └── sources/          # Adapter ITviec đã kiểm chứng
├── notebooks/            # Điểm chạy PySpark Bronze trên Databricks
├── dbt/
│   ├── models/staging/   # Hợp đồng Bronze, kiểu dữ liệu, FX và lịch sử
│   ├── models/intermediate/ # Bản hiện tại, chuẩn hóa skills/cities
│   ├── models/marts/     # Dimensions, facts, bridges và reports
│   ├── macros/           # Schema naming, surrogate key
│   ├── seeds/            # Alias có kiểm soát
│   └── tests/            # Kiểm thử SQL nghiệp vụ trên cloud
├── infra/terraform/      # Workspace objects và provider lock
├── dashboards/           # Template AI/BI dashboard thực sự triển khai
├── scripts/              # Tạo dashboard và triển khai Terraform
├── tests/                # Unit, toàn vẹn raw và kiểm tra ngữ nghĩa SQL
├── docs/                 # Thiết kế, hợp đồng, từ điển, vận hành
├── .github/workflows/    # CI và lịch kích hoạt/chờ toàn bộ Databricks Job
├── artifacts/            # Raw thật, log, plan, công cụ; bị loại khỏi Git
├── .env                  # Cấu hình cá nhân; bị loại khỏi Git
├── pyproject.toml
├── uv.lock
└── Makefile
```

Không gộp code lấy nguồn, upload và biến đổi thành một script lớn. Notebook không chứa business logic lương hoặc dashboard. Các phép tổng hợp nằm trong marts; API nguồn nằm trong adapter. Test fixtures phục vụ kiểm thử, không có đường chạy đưa dữ liệu kiểm thử vào pipeline.
