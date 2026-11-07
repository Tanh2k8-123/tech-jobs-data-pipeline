# Vận hành

## Kiểm tra kết nối

Chạy `uv run it-jobs check` tại thư mục dự án. CLI đọc `.env`, kiểm tra current user, warehouse, catalog và chạy SELECT 1. Không in token. Nếu dùng OAuth trong WSL, bảo đảm profile còn đăng nhập và Databricks CLI có tại `/usr/local/bin/databricks`. Với nhiều warehouse, đặt HTTP path rõ ràng; với một warehouse, CLI có thể tự chọn và lưu HTTP path không bí mật vào `.env` hiện có.

## Triển khai

Chạy `uv run python scripts/deploy.py` để xem plan, rồi `uv run python scripts/deploy.py --apply`. Giữ nguyên state đã tạo trong `infra/terraform/terraform.tfstate`; state/plan không được đưa lên Git. Bản OAuth dùng cho Terraform chỉ đi qua môi trường tiến trình, không ghi token xuống file. Dashboard được tạo trong workspace, không chia sẻ công khai và không nhúng thông tin xác thực.

Ghi `job_id` từ Terraform output. `uv run it-jobs run --job-id ID` kích hoạt toàn bộ DAG thu thập nguồn thật trên Databricks và chờ hoàn tất Job. Tham số input_path rỗng có nghĩa lấy snapshot mới ở task extraction; notebook Bronze luôn nhận đường dẫn cụ thể qua task value. Replay nhận input_path đã lưu và bỏ qua extraction mới.

## Khôi phục và chạy bù

- Ingestion lỗi trước manifest: batch chưa hoàn tất, không upload. Kiểm tra trạng thái nguồn, robots, pagination, JSON-LD và log; chạy lại extraction.
- Upload gián đoạn: dùng `replay` với đúng đường dẫn raw. File đã tồn tại phải có cùng checksum, không bị ghi đè.
- Spark lỗi: retry cùng batch. MERGE observation và ledger đều idempotent.
- dbt lỗi: xem model/test cụ thể trong Databricks Job; sửa code, triển khai lại rồi replay batch. Không refresh dashboard khi build thất bại.
- Nếu task extraction đã thành công, có thể dùng `it-jobs repair --job-id ID --run-id RUN_ID` hoặc input `repair_run_id` của workflow để chạy lại task lỗi và downstream. Các tham số tính từ task value phải có tên riêng, tránh bị Job parameters tự động ghi đè.
- Nguồn ẩn lương: kết quả NULL và warning là đúng. Không sửa thành 0 hay tạo mẫu giả để tắt cảnh báo.
- Backfill: replay raw theo run đã lưu. Nếu dựng lại workspace chỉ từ dữ liệu cũ, kiểm tra freshness sẽ báo stale theo thiết kế; cần tải một snapshot hiện tại trước khi công bố dashboard.

## Theo dõi

Kiểm tra số tin, số trang, thời điểm cập nhật, tỷ lệ lương, parse failures và missing posted date. Snapshot gần nhất không tự chứng minh tin đang mở hoặc đã đóng. Không diễn giải đường thời gian thành toàn bộ lịch sử tuyển dụng trước thời điểm pipeline bắt đầu quan sát.

GitHub workflow có timeout 150 phút, concurrency và lưu log thất bại 7 ngày. Để bảo mật và tuân thủ nguồn FX, không upload raw Parquet/FX thành artifact công khai. Kiểm tra quota Databricks trước khi tăng tần suất chạy. Theo dõi dung lượng raw; chưa có tác vụ xóa tự động.
