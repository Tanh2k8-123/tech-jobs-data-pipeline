# Tổng quan dự án: Vietnam IT Job Market Lakehouse

## Mục tiêu và phạm vi

Xây dựng pipeline thật, chạy batch mỗi ngày, phục vụ phân tích kỹ năng tuyển dụng và ngày đăng tin tại Việt Nam. Phiên bản này dùng ITviec công khai đã được kiểm chứng; không phụ thuộc API giả định của TopDev, không có chế độ demo hoặc fallback sinh dữ liệu.

## Bộ công cụ

Python + requests/BeautifulSoup lấy nguồn; PyArrow ghi Parquet; Databricks SDK upload và chờ Job; Unity Catalog Volume lưu raw; PySpark + Delta giữ Bronze; dbt-databricks xây Silver/Gold và tests; AI/BI Dashboard hiển thị; Terraform quản lý tài nguyên trong workspace; GitHub Actions sở hữu lịch chạy.

Databricks Free Edition là môi trường học có quota, không phải cam kết vận hành miễn phí không giới hạn hoặc nền tảng có SLA. Ingestion chạy bên ngoài Databricks để không phụ thuộc egress serverless. Chi phí GitHub phụ thuộc loại repository/runner và hạn mức thực tế.

## Các cải thiện chính so với bản thiết kế ban đầu

1. Nguồn dữ liệu có implementation và hợp đồng cụ thể: pagination, ID nguồn, ngày đăng JSON-LD, salary visibility và kiểm tra độ đầy đủ.
2. Lưu raw bất biến có checksum/manifest; Bronze giữ từng quan sát thay vì MERGE ghi đè toàn bộ lịch sử theo job_id.
3. Phân biệt posted_date, first_seen_at, snapshot_date; không suy ra đóng/mở từ một lần không thấy tin.
4. Tách dimension kỹ năng khỏi bridge job–skill; bổ sung bridge thành phố để xử lý multi-city đúng grain.
5. Parser lương có kiểm thử; không suy cận thiếu, không mặc định lương năm thành tháng, không tự gán tỷ giá cố định.
6. Lương quảng cáo có số mẫu và độ phủ; mức lương ẩn được giữ NULL, không đại diện cho toàn thị trường.
7. Một chủ lịch, chờ kết quả Job, retry có kiểm soát, replay raw và refresh dashboard sau dbt build thành công.
8. Có cấu trúc package, khóa dependency, Terraform lock, CI, data dictionary và runbook.

## Độ khó

Khoảng 7/10 với người đã biết Python/SQL. Thu thập nguồn thay đổi, kiểm chứng ngữ nghĩa dữ liệu và tích hợp quyền/môi trường cloud là phần khó nhất. Quy mô MVP chưa yêu cầu streaming hoặc nhiều service. Dùng Spark nhằm thực hành lakehouse, không tự tuyên bố đang xử lý big data.

## Đối chiếu rubric

Rubric chính thức hiện có 7 tiêu chí × 4 = 28 điểm kỹ thuật. Bản trước ghi 22/22 và tổng các dòng 26 là không chính xác. Mục tiêu là có bằng chứng cho từng tiêu chí, không tự chấm tối đa bằng cách liệt kê công cụ.

| Tiêu chí | Bằng chứng cần có |
|---|---|
| Problem | Câu hỏi rõ ràng, giới hạn nguồn và cách tính chỉ số |
| Cloud + IaC | Terraform plan/apply, tài nguyên workspace và state được giữ an toàn |
| Orchestration | Một run thật từ ingestion đến dashboard, trạng thái lỗi truyền về caller |
| Warehouse | Delta model đúng grain, giải thích clustering và query profile |
| Transformation | Model dbt, parser, kết quả kiểm thử trên cloud |
| Dashboard | Biểu đồ kỹ năng, ngày đăng, lương và độ phủ; ảnh hoặc link phù hợp quyền truy cập |
| Reproducibility | Clone sạch, locked dependencies, cấu hình mẫu, hướng dẫn triển khai và replay |

Xem [README](../README.md) để triển khai và [architecture.md](architecture.md) cho các giới hạn còn lại, bao gồm việc dbt không giao dịch nguyên tử trên toàn bộ nhiều bảng Gold.
