# Bằng chứng kiểm chứng

Ngày kiểm tra: 07/11/2026, giờ Việt Nam.

## Dữ liệu thật

- Nguồn ITviec: đọc đủ 32 trang, 632 tin, 632 trang chi tiết JobPosting.
- Batch: `20261107T131542_59cafb1db68e`.
- Truy vấn Gold trên Databricks: 632 tin, 632 tin thuộc snapshot mới nhất, 0 tin thiếu ngày đăng.
- 0 mẫu lương đủ điều kiện tính trung bình vì nguồn ẩn lương. Không bổ sung dữ liệu thay thế.
- Tỷ giá lấy từ endpoint thực, gắn timestamp của nhà cung cấp và lưu riêng với raw.

## Kiểm tra local và cloud

- 27 kiểm thử Python/SQL nghiệp vụ: pass.
- Ruff: pass; dbt parse: pass; Terraform fmt/validate: pass.
- Job `198306811950277`, run `559940590723474`: Bronze, dbt build, dashboard refresh đều SUCCESS.
- dbt trên Databricks: 2 seeds, 8 table models, 5 view models và 38 data tests. 37 tests pass, 1 warning về độ phủ lương, 0 errors. Tổng 53 thao tác: PASS=52, WARN=1.
- Nạp lại chính batch đó bằng task Bronze, run `218432312513077`: vẫn 632 quan sát và 1 batch, kiểm chứng idempotency trên Delta thật.

## Tự động hóa hoàn chỉnh trên cloud

- CI trên Ubuntu đã pass: [Validate pipeline](https://github.com/Tanh2k8-123/tech-jobs-data-pipeline/actions/runs/42380766623).
- Source ingestion chạy ngay trên Databricks, không phụ thuộc máy cá nhân hoặc khả năng truy cập ITviec từ runner GitHub.
- Databricks run `791920414056791` đã thu thập raw thật, sau đó repair thành công Bronze → dbt → dashboard khi lỗi trùng tên tham số đã được sửa. Task Bronze dùng `raw_path` riêng để Job parameter `input_path` không ghi đè task value.
- [Workflow GitHub thành công](https://github.com/Tanh2k8-123/tech-jobs-data-pipeline/actions/runs/42380817065) đã kiểm chứng cơ chế repair và chờ trạng thái Job đến SUCCESS.
- Sau hai batch thật: Bronze 1.264 quan sát / 2 batch, Gold 632 tin / 315 công ty / 320 tag kỹ năng. Snapshot gần nhất có 632 tin, không thiếu ngày đăng, không có midpoint lương được công khai.
- Lịch `01:00 UTC` = `08:00` giờ Việt Nam đã bật bằng `ENABLE_DAILY_PIPELINE=true`. Các lượt theo lịch không có `repair_run_id`, nên luôn thu thập snapshot mới.

Liên kết yêu cầu quyền truy cập workspace:

- [Databricks Job](https://dbc-63d22f94-de5b.cloud.databricks.com/#job/198306811950277)
- [AI/BI Dashboard](https://dbc-63d22f94-de5b.cloud.databricks.com/dashboardsv3/01f1daaffcd713898cd8c43b363dce39/published)

Repo triển khai: [Tanh2k8-123/tech-jobs-data-pipeline](https://github.com/Tanh2k8-123/tech-jobs-data-pipeline).

PAT dành cho GitHub Actions được tạo với hạn dùng đến 05/02/2027; cần luân chuyển trước ngày này. Giá trị token chỉ nằm trong GitHub Secret, không nằm trong mã nguồn hoặc tài liệu.
