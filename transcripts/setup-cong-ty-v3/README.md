# Tổng Hợp Toàn Văn Bản Chép Lời (Transcripts)
## Khóa học: Setup Công Ty & Vận Hành Kinh Doanh Bài Bản V3
- **Đơn vị phát hành:** [Giamdoc.net](https://giamdoc.net)
- **Giảng viên:** Thầy Vũ Long
- **Nguồn tài liệu:** [Google Drive Folder](https://drive.google.com/drive/folders/1EIJ9FFhWxslCIBlxdjVhtIL71FwHsPpT)
- **Phương thức trích xuất:** Tự động hóa qua Chrome DevTools Protocol (CDP), lấy trực tiếp từ bản chép lời (subtitles/cues) tích hợp của Google Drive.
- **Tổng số phân đoạn lời thoại:** 2.928 mốc thoại (hơn 5 giờ nội dung bài giảng).

---

## Cấu Trúc Thư Mục

```text
transcripts/setup-cong-ty-v3/
├── README.md                                             # Mục lục & hướng dẫn tra cứu
├── markdown/                                             # Bản định dạng Markdown (gom cụm ~45s/đoạn, dễ đọc)
│   ├── 01-9-thanh-to-mo-hinh-kinh-doanh.md
│   ├── 02-kinh-doanh-dua-tren-phan-khuc-khach-hang-san-pham.md
│   ├── 03-chien-luoc-cong-ty-va-ops.md
│   ├── 04-loi-the-canh-tranh-khac-biet-chi-phi-thap.md
│   ├── 05-phan-tich-cau-truc-ops-ung-dung.md
│   └── 06-tong-ket-mo-hinh-kd-va-chien-luoc.md
└── raw/                                                  # Bản text thô theo từng dòng mốc thời gian gốc
    ├── 01-9-thanh-to-mo-hinh-kinh-doanh.txt
    ├── 02-kinh-doanh-dua-tren-phan-khuc-khach-hang-san-pham.txt
    ├── 03-chien-luoc-cong-ty-va-ops.txt
    ├── 04-loi-the-canh-tranh-khac-biet-chi-phi-thap.txt
    ├── 05-phan-tich-cau-truc-ops-ung-dung.txt
    └── 06-tong-ket-mo-hinh-kd-va-chien-luoc.txt
```

---

## Danh Mục Chi Tiết Từng Bài Giảng

| STT | Tên bài giảng | Thời lượng | Cues | Bản Markdown (Đọc & LLM) | Bản Text Thô (Dòng gốc) |
| :---: | :--- | :---: | :---: | :--- | :--- |
| **01** | **9 Thành Tố Của Mô Hình Kinh Doanh (BMC)**<br>*Phân tích Canvas, giá trị cốt lõi, quan hệ đối tác, dòng doanh thu & chi phí.* | 1:01:58 | 653 | [`markdown/01-...md`](./markdown/01-9-thanh-to-mo-hinh-kinh-doanh.md) | [`raw/01-...txt`](./raw/01-9-thanh-to-mo-hinh-kinh-doanh.txt) |
| **02** | **Kinh Doanh Dựa Trên Phân Khúc KH & Sản Phẩm**<br>*Khảo sát phân khúc thị trường mục tiêu, xác định gói giá trị khớp nhu cầu khách hàng.* | 54:05 | 639 | [`markdown/02-...md`](./markdown/02-kinh-doanh-dua-tren-phan-khuc-khach-hang-san-pham.md) | [`raw/02-...txt`](./raw/02-kinh-doanh-dua-tren-phan-khuc-khach-hang-san-pham.txt) |
| **03** | **Chiến Lược Công Ty Và OPS (Onepage Strategy)**<br>*Liên kết mục tiêu công ty với bản kế hoạch chiến lược một trang (OPS).* | 31:30 | 329 | [`markdown/03-...md`](./markdown/03-chien-luoc-cong-ty-va-ops.md) | [`raw/03-...txt`](./raw/03-chien-luoc-cong-ty-va-ops.txt) |
| **04** | **Lợi Thế Cạnh Tranh: Khác Biệt & Chi Phí Thấp**<br>*Chiến lược tạo sự khác biệt hóa bền vững và tối ưu hóa cấu trúc chi phí vận hành.* | 36:44 | 253 | [`markdown/04-...md`](./markdown/04-loi-the-canh-tranh-khac-biet-chi-phi-thap.md) | [`raw/04-...txt`](./raw/04-loi-the-canh-tranh-khac-biet-chi-phi-thap.txt) |
| **05** | **Phân Tích Cấu Trúc OPS - Chỉ Dẫn Ứng Dụng Thực Tế**<br>*Hướng dẫn chi tiết cách triển khai, phân bổ chỉ tiêu, đo lường KPI theo khung OPS.* | 57:37 | 469 | [`markdown/05-...md`](./markdown/05-phan-tich-cau-truc-ops-ung-dung.md) | [`raw/05-...txt`](./raw/05-phan-tich-cau-truc-ops-ung-dung.txt) |
| **06** | **Tổng Kết Chuyên Đề Mô Hình KD & Chiến Lược**<br>*Đúc kết toàn bộ phương pháp luận, case studies thực chiến và lộ trình thực thi.* | 56:45 | 585 | [`markdown/06-...md`](./markdown/06-tong-ket-mo-hinh-kd-va-chien-luoc.md) | [`raw/06-...txt`](./raw/06-tong-ket-mo-hinh-kd-va-chien-luoc.txt) |

---

## Hướng Dẫn Sử Dụng
1. **Dành cho người đọc:** Mở trực tiếp các tệp trong thư mục `markdown/`. Các đoạn hội thoại đã được ngắt theo ngữ cảnh (~45s) kèm timestamp `**[mm:ss]**` giúp dễ dàng tra cứu lại vị trí video tương ứng trên Google Drive.
2. **Dành cho AI / RAG / Prompting:** Sử dụng các file Markdown hoặc file Raw TXT để cung cấp context cho LLM khi cần tóm tắt bài giảng, trích xuất mindmap, lập kế hoạch hành động hoặc tạo bộ câu hỏi Q&A.
