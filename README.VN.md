# 🇻🇳 **Trustless Wakatime Logger**

**Trustless WakaTime Logger** là một hệ thống tự động ghi log dữ liệu từ WakaTime mỗi ngày, với mục tiêu cốt lõi là:
📌 **Không ai, kể cả chính người sử dụng, có thể giả mạo hay chỉnh sửa dữ liệu log**.

Hệ thống đảm bảo tính xác thực bằng cách:

* Lưu trữ dữ liệu theo cách không thể chỉnh sửa sau khi ghi (immutable).
* Có cơ chế xác minh từ bên thứ ba (external proof/verification).
* Hướng đến sự minh bạch tuyệt đối cho việc theo dõi thói quen lập trình cá nhân hoặc công khai.

> Ý tưởng: Tạo ra một **WakaTime logger không cần niềm tin (trustless)** – nơi người dùng **không thể gian lận chính mình**, nhằm duy trì sự kỷ luật và minh bạch.

## Tính năng

* **Xác minh không thể giả mạo**: Nhiều timestamp bên ngoài (NTP, GitHub API, WorldTimeAPI) để ngăn chặn việc tạo dữ liệu giả
* **Tổ chức có cấu trúc**: Dữ liệu được sắp xếp theo năm/tháng/tuần với tạo thư mục tự động
* **Tóm tắt hàng tuần**: Tự động tạo tóm tắt hàng tuần với thống kê chi tiết và biểu đồ
* **Tóm tắt hàng tháng**: Tổng hợp dữ liệu hàng tháng với biểu đồ
* **Trực quan hóa dữ liệu**: Biểu đồ tương tác nhúng vào file tóm tắt và công cụ trực quan hóa độc lập
* **Đặc biệt Chủ nhật**: Vào Chủ nhật, lấy 7 ngày dữ liệu và tạo tóm tắt tuần
* **GitHub Actions**: Tự động lấy dữ liệu hàng ngày và workflow import dữ liệu thủ công

## Cấu trúc thư mục

```tree
wakatime_logs/
├── 2025/
│   ├── 01_January/
│   │   ├── week_1/
│   │   │   ├── 2025-01-01.json
│   │   │   ├── 2025-01-02.json
│   │   │   ├── ...
│   │   │   ├── week_1.json          # Dữ liệu tóm tắt tuần
│   │   │   └── week_1_summary.md    # Báo cáo tóm tắt tuần với biểu đồ
│   │   ├── week_2/
│   │   ├── ...
│   │   ├── 01_January.json          # Dữ liệu tóm tắt tháng
│   │   └── 01_January_summary.md    # Báo cáo tóm tắt tháng với biểu đồ
│   └── 02_February/
└── 2024/
```

## Cài đặt

1. Clone repository:

    ```bash
    git clone https://github.com/haru2503/wakatime-log.git
    cd wakatime-log
    ```

2. Cài đặt dependencies:

    ```bash
    pip install -r requirements.txt
    ```

## Sử dụng

### Sử dụng cơ bản

Chạy script để lấy dữ liệu ngày hôm qua:

```bash
python wakatime_fetcher.py
```

### Sử dụng nâng cao

Script tự động:

* Tạo thư mục dựa trên cấu trúc ngày tháng
* Tạo tóm tắt tuần vào Chủ nhật với biểu đồ nhúng
* Tạo tóm tắt tháng vào Chủ nhật cuối tháng với trực quan hóa
* Lấy 7 ngày dữ liệu khi chạy vào Chủ nhật

### GitHub Actions Workflows

Repository này bao gồm hai GitHub Actions workflows:

#### 1. Workflow Lấy Dữ Liệu Hàng Ngày (`log-wakatime.yml`)

**Mục đích**: Tự động lấy dữ liệu WakaTime hàng ngày và commit vào repository

**Thiết lập**:

1. Vào Settings → Secrets and variables → Actions của repository
2. Thêm secret `WAKATIME_API_KEY` với WakaTime API key của bạn
3. Workflow chạy hàng ngày lúc 1:00 AM UTC

**Tính năng**:

* Tự động lấy dữ liệu ngày hôm qua
* Vào Chủ nhật, lấy 7 ngày và tạo tóm tắt tuần
* Vào Chủ nhật cuối tháng, tạo tóm tắt tháng
* Commit thay đổi vào repository với xác minh không thể giả mạo

#### 2. Workflow Import Thủ Công (`wakatime-import.yml`)

**Mục đích**: Import dữ liệu WakaTime lịch sử (N ngày gần nhất)

**Thiết lập**:

1. Thiết lập API key giống như trên
2. Vào tab Actions → "Import WakaTime Data" → "Run workflow"
3. Chọn số ngày muốn import (mặc định: 20)

**Tính năng**:

* Import tối đa 400 ngày dữ liệu lịch sử
* Tạo cấu trúc thư mục hoàn chỉnh
* Tạo tất cả tóm tắt và trực quan hóa
* Hoàn hảo cho thiết lập ban đầu hoặc khôi phục dữ liệu

### Trực quan hóa dữ liệu

#### Biểu đồ nhúng trong tóm tắt

File tóm tắt tuần và tháng (`.md`) giờ bao gồm:

* **Biểu đồ cột thời gian coding hàng ngày**: Hiển thị tổng thời gian coding mỗi ngày với phân tích theo project
* **Biểu đồ tròn ngôn ngữ lập trình**: Phân bố các ngôn ngữ lập trình
* **Biểu đồ tròn danh mục**: Phân bố các danh mục coding
* **Biểu đồ tròn editor**: Phân bố các code editor được sử dụng
* **Biểu đồ tròn hệ điều hành**: Phân bố sử dụng OS
* **Biểu đồ tròn máy tính**: Phân bố các máy tính được sử dụng
* **Biểu đồ tròn project**: Phân bố các project đã làm việc

#### Công cụ trực quan hóa độc lập

Sử dụng visualizer để phân tích tùy chỉnh:

```bash
# Biểu đồ thời gian coding hàng ngày
python wakatime_visualizer.py --plot-type daily --start-date 2025-01-01 --end-date 2025-01-07

# Phân bố ngôn ngữ lập trình cho ngày cụ thể
python wakatime_visualizer.py --plot-type languages --date 2025-01-01

# Sử dụng editor cho ngày cụ thể
python wakatime_visualizer.py --plot-type editors --date 2025-01-01

# Biểu đồ tóm tắt tuần
python wakatime_visualizer.py --plot-type weekly --week-folder wakatime_logs/2025/01_January/week_1

# Thống kê tóm tắt cho khoảng thời gian
python wakatime_visualizer.py --plot-type summary --start-date 2025-01-01 --end-date 2025-01-31
```

## Xác minh không thể giả mạo

Hệ thống sử dụng nhiều nguồn bên ngoài để xác minh tính xác thực của dữ liệu:

1. **NTP Timestamps**: Thời gian từ đồng hồ nguyên tử từ pool.ntp.org
2. **GitHub API**: Thời gian server từ GitHub
3. **WorldTimeAPI**: Xác minh thời gian bên ngoài
4. **Content Hashing**: Hash SHA-256 của tất cả dữ liệu
5. **Network Evidence**: Metadata request/response

Điều này khiến bất cứ ai cũng không thể tạo dữ liệu giả mà không kiểm soát tất cả các nguồn xác minh bên ngoài.

## Tóm tắt hàng tuần

Khi script chạy vào Chủ nhật, nó sẽ:

1. Lấy dữ liệu cho tất cả 7 ngày trong tuần
2. Tạo `week_N.json` với dữ liệu tổng hợp
3. Tạo `week_N_summary.md` với phân tích chi tiết và biểu đồ

### Nội dung tóm tắt tuần

* Tổng thời gian coding trong tuần
* Thời gian coding trung bình hàng ngày
* Tổng thời gian theo danh mục, ngôn ngữ, project, editor, máy tính, OS
* Phân tích hàng ngày cho mỗi ngày trong tuần
* **Biểu đồ nhúng**: Biểu đồ cột cho thời gian coding hàng ngày, biểu đồ tròn cho phân bố

## Tóm tắt hàng tháng

Vào Chủ nhật cuối tháng, script cũng sẽ:

1. Tổng hợp tất cả tóm tắt tuần trong tháng
2. Tạo `MM_Month.json` với dữ liệu tháng
3. Tạo `MM_Month_summary.md` với phân tích tháng và trực quan hóa

### Nội dung tóm tắt tháng

* Tổng thời gian coding trong tháng
* Trung bình hàng tuần và hàng ngày
* Tổng thời gian theo danh mục, ngôn ngữ, project, editor, máy tính, OS
* Phân tích hàng tuần cho mỗi tuần trong tháng
* **Biểu đồ nhúng**: Biểu đồ cột cho thời gian coding hàng tuần, biểu đồ tròn cho phân bố

## Quy tắc tạo thư mục

* **Thư mục tháng**: Tạo vào ngày đầu tiên của mỗi tháng
* **Thư mục tuần**: Tạo vào thứ Hai đầu tiên của mỗi tháng
* **Tuần trải dài 2 tháng**: Nếu một tuần nằm ở 2 tháng, dữ liệu sẽ lưu vào thư mục tuần của tháng bắt đầu

## Cấu trúc dữ liệu

Mỗi file JSON hàng ngày chứa:

```json
{
  "wakatime_data": {
    "data": [{
      "languages": [...],
      "editors": [...],
      "categories": [...],
      "grand_total": {...}
    }]
  },
  "authenticity_proof": {
    "content_hash": "...",
    "external_timestamps": {...},
    "network_evidence": {...}
  },
  "request_proof": {...},
  "metadata": {...}
}
```

## Xác minh

Để xác minh tính xác thực của bất kỳ file nào:

```bash
python wakatime_fetcher.py
# Script sẽ tự động xác minh dữ liệu đã lấy
```

## Testing

Chạy script test để xem cấu trúc thư mục hoạt động:

```bash
python test_structure.py
```

Script này sẽ tạo dữ liệu mẫu trong `test_wakatime_logs/` để minh họa cấu trúc.

## Tự động hóa

### GitHub Actions (Khuyến nghị)

Repository bao gồm GitHub Actions workflows được cấu hình sẵn:

1. **Lấy dữ liệu hàng ngày**: Tự động chạy mỗi ngày lúc 1:00 AM UTC (8 giờ sáng VN)
2. **Import thủ công**: Chạy theo yêu cầu để import dữ liệu lịch sử

### Cron Job thủ công

Thiết lập cron job để chạy hàng ngày:

```bash
# Hàng ngày lúc 1 AM
0 1 * * * cd /path/to/wakatime-log && python wakatime_fetcher.py
```

## Đóng góp

Hãy tự do gửi issues và pull request!! 🤗

## Giấy phép

Dự án này là mã nguồn mở được cấp quyền dưới MIT License.
