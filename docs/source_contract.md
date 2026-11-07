# Hợp đồng nguồn ITviec

Được kiểm chứng với trang công khai ngày 07/11/2026. TopDev chưa được tích hợp: endpoint thử nghiệm không trả đủ trường công khai để sử dụng đáng tin cậy. Không ghi tên một connector vào cấu hình khi chưa có implementation được kiểm chứng.

## Danh sách

- URL gốc: `https://itviec.com/it-jobs`, phân trang bằng `?page=N`.
- Card: `.job-card[data-job-key]`; UUID trong `data-job-key` là ID nguồn. Không dùng bốn chữ số cuối slug làm khóa.
- Tiêu đề: `h3 a`; công ty: link `/companies/`; kỹ năng: phần tử `data-responsive-tag-list-target=tag`.
- Lương chỉ đọc phần công khai. Có `.sign-in-view-salary` thì giữ NULL và không dùng dữ liệu đăng nhập.
- Đọc trang cuối từ pagination. Giới hạn an toàn mặc định 100 trang; chạm giới hạn là lỗi, không xuất snapshot cắt ngắn. Trang lặp, trang rỗng hoặc số tin dưới 90% số nguồn quảng cáo đều bị từ chối. Ngưỡng 90% cho phép thay đổi danh sách trong lúc crawl, không chứng minh bao phủ tuyệt đối.

## Chi tiết

- Mỗi URL chi tiết phải có `JobPosting` trong JSON-LD, kể cả `@graph`.
- Ngày đăng từ `datePosted`, không suy từ nhãn tương đối trên card.
- Tên công ty từ `hiringOrganization.name`, danh sách địa điểm từ `jobLocation[].address.addressRegion`.
- Kỹ năng giữ danh sách nguồn; alias mapping và khử trùng ở Silver.
- Không đọc hồ sơ ứng viên, gửi đơn ứng tuyển, đăng nhập hoặc vượt trang bị chặn. 403/HTML thay đổi làm run thất bại.

HTTP có timeout 10s kết nối/45s đọc, retry tối đa 3 lần cho 429/5xx, tôn trọng Retry-After và giãn request tối thiểu 0.5s, mặc định 1s. Crawl một snapshot đầy đủ có thể mất hơn 10 phút; không giả định đủ dữ liệu từ trang đầu.

## Raw batch

`jobs.parquet` có source identity, payload nguồn, ngày đăng, kỹ năng/địa điểm JSON, trường parser lương, FX và metadata quan sát. `manifest.json` có schema_version, complete, run_id, snapshot_date, row_count, checksum, thời gian bắt đầu/kết thúc và số trang nguồn.

Chỉ batch có manifest hoàn tất và checksum đúng mới được upload/nạp Bronze. Mỗi run có đường dẫn riêng. Không đổi ngày snapshot khi replay, không dùng dữ liệu sinh tự động khi nguồn lỗi.
