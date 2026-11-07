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

Liên kết yêu cầu quyền truy cập workspace:

- [Databricks Job](https://dbc-63d22f94-de5b.cloud.databricks.com/#job/198306811950277)
- [AI/BI Dashboard](https://dbc-63d22f94-de5b.cloud.databricks.com/dashboardsv3/01f1daaffcd713898cd8c43b363dce39/published)

Repo triển khai: [Tanh2k8-123/tech-jobs-data-pipeline](https://github.com/Tanh2k8-123/tech-jobs-data-pipeline).

PAT dành cho GitHub Actions được tạo với hạn dùng đến 05/02/2027; cần luân chuyển trước ngày này. Giá trị token chỉ nằm trong GitHub Secret, không nằm trong mã nguồn hoặc tài liệu.
