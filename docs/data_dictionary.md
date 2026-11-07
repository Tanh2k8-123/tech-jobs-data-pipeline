# Từ điển dữ liệu

| Quan hệ | Grain / ý nghĩa |
|---|---|
| Bronze `raw_it_job_observations` | Một quan sát của source + source_job_id + run_id; chứa raw payload và kết quả parser |
| Bronze `ingestion_runs` | Một run đã hoàn tất nạp Bronze |
| Silver `stg_job_history` | Lịch sử hợp lệ, chỉ từ run có ledger; cast kiểu, quy đổi FX và parse array |
| Silver `int_jobs_current` | Quan sát gần nhất mỗi tin, cùng first_seen_at/last_seen_at |
| Gold `fct_job_postings` | Một tin nguồn đã quan sát; giữ cờ xuất hiện trong snapshot mới nhất |
| Gold `dim_companies` | Một công ty theo ID tại nguồn; không tự gộp liên nguồn |
| Gold `dim_skills` | Một tên kỹ năng chuẩn hóa |
| Gold `bridge_job_skills` | Một cặp tin–kỹ năng duy nhất |
| Gold `bridge_job_cities` | Một cặp tin–thành phố duy nhất |
| Gold `mart_skill_demand` | Một kỹ năng, tính trên snapshot gần nhất của mỗi nguồn |
| Gold `mart_daily_city_jobs` | Một ngày đăng–thành phố, tính trên các tin đã từng quan sát |
| Gold `audit_data_quality` | Một nguồn, các chỉ số thiếu dữ liệu và cập nhật |

## Các trường quan trọng

- `job_sk`: SHA-256 từ source và ID, có length prefix để tránh xung đột khi nối chuỗi.
- `posted_date`: ngày đăng do nguồn cung cấp. NULL bị loại khỏi biểu đồ ngày đăng và được đếm trong audit.
- `snapshot_date`: ngày Việt Nam khi thu thập. `ingested_at`, `first_seen_at`, `last_seen_at`, `fx_rate_at` là thời điểm UTC.
- `observed_in_latest_snapshot`: xuất hiện trong run đầy đủ gần nhất của nguồn; không đặt tên `is_open` vì thiếu bằng chứng trạng thái.
- `min_salary_usd`, `max_salary_usd`: cận USD/tháng biết được; một trong hai có thể NULL.
- `avg_salary_usd`: midpoint khi có đủ hai cận; giữ NULL với một cận hoặc lương chưa công bố.
- `salary_sample_count`: số tin có midpoint hợp lệ trong nhóm kỹ năng.
- `salary_coverage`: số mẫu có midpoint / số tin trong nhóm. Không được dùng làm tỷ lệ tổng thị trường công bố lương.
- `salary_basis`: nguồn chưa xác nhận gross/net thì giữ `unknown`.
- `city_name`: Ha Noi / Ho Chi Minh / Da Nang / Other. Một tin có thể có nhiều giá trị qua bridge.

Kỹ năng chưa có trong alias seed được giữ dưới dạng chữ thường, tránh tự suy diễn taxonomy. Bổ sung alias bằng dữ liệu có căn cứ, kèm kiểm tra không trùng alias.
