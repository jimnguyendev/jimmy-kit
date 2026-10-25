# Tổng Hợp Toàn Văn Bản Chép Lời (Transcripts)
## Khóa 02: Tài Chính, Nguồn Vốn Và Setup Hệ Thống Quản Trị
- **Đơn vị phát hành:** [Giamdoc.net](https://giamdoc.net)
- **Giảng viên:** Thầy Vũ Long
- **Nguồn tài liệu:** [Google Drive Folder](https://drive.google.com/drive/folders/1d-uSMUi4rrREA112OecPYXR_s5spyg2c)
- **Phương thức trích xuất:** Tự động hóa qua Chrome DevTools Protocol (CDP), lấy trực tiếp từ bản chép lời (subtitles/cues) tích hợp của Google Drive.
- **Tổng số phân đoạn lời thoại:** 3.321 mốc thoại (~6 giờ nội dung bài giảng).

---

## Cấu Trúc Thư Mục

```text
transcripts/khoa-02-tai-chinh-nguon-von/
├── README.md                                             # Mục lục & hướng dẫn tra cứu
├── markdown/                                             # Bản định dạng Markdown (gom cụm ~45s/đoạn, dễ đọc)
│   ├── 01-bao-cao-tai-chinh-bang-can-doi-ke-toan.md
│   ├── 02-ket-qua-kinh-doanh-va-luu-chuyen-tien-te.md
│   ├── 03-huong-dan-lap-can-doi-ke-toan-thu-cong.md
│   ├── 04-huong-dan-lap-can-doi-ke-toan-dung-cong-thuc.md
│   ├── 05-huong-dan-lap-bao-cao-ket-qua-kinh-doanh.md
│   ├── 06-phuong-phap-phan-tich-bctc.md
│   ├── 07-phan-tich-bctc-va-chi-so-tai-chinh.md
│   └── 08-huong-dan-ung-dung-mau-phan-tich-bctc.md
└── raw/                                                  # Bản text thô theo từng dòng mốc thời gian gốc
    ├── 01-bao-cao-tai-chinh-bang-can-doi-ke-toan.txt
    ├── 02-ket-qua-kinh-doanh-va-luu-chuyen-tien-te.txt
    ├── 03-huong-dan-lap-can-doi-ke-toan-thu-cong.txt
    ├── 04-huong-dan-lap-can-doi-ke-toan-dung-cong-thuc.txt
    ├── 05-huong-dan-lap-bao-cao-ket-qua-kinh-doanh.txt
    ├── 06-phuong-phap-phan-tich-bctc.txt
    ├── 07-phan-tich-bctc-va-chi-so-tai-chinh.txt
    └── 08-huong-dan-ung-dung-mau-phan-tich-bctc.txt
```

---

## Danh Mục Chi Tiết Từng Bài Giảng

| STT | Tên bài giảng | Thời lượng | Cues | Bản Markdown (Đọc & LLM) | Bản Text Thô (Dòng gốc) |
| :---: | :--- | :---: | :---: | :--- | :--- |
| **01** | **Báo Cáo Tài Chính - Bảng Cân Đối Kế Toán**<br>*Bản chất tài sản, nguồn vốn, nguyên lý cân bằng kế toán trong doanh nghiệp.* | 58:16 | 703 | [`markdown/01-...md`](./markdown/01-bao-cao-tai-chinh-bang-can-doi-ke-toan.md) | [`raw/01-...txt`](./raw/01-bao-cao-tai-chinh-bang-can-doi-ke-toan.txt) |
| **02** | **Kết Quả Kinh Doanh Và Lưu Chuyển Tiền Tệ**<br>*Phân biệt doanh thu - dòng tiền, lợi nhuận kế toán và dòng tiền thuần từ hoạt động KD.* | 59:49 | 709 | [`markdown/02-...md`](./markdown/02-ket-qua-kinh-doanh-va-luu-chuyen-tien-te.md) | [`raw/02-...txt`](./raw/02-ket-qua-kinh-doanh-va-luu-chuyen-tien-te.txt) |
| **03** | **Hướng Dẫn Lập Cân Đối Kế Toán Thủ Công**<br>*Thực hành lên bảng cân đối kế toán từ các nghiệp vụ kinh tế phát sinh ban đầu.* | 30:05 | 285 | [`markdown/03-...md`](./markdown/03-huong-dan-lap-can-doi-ke-toan-thu-cong.md) | [`raw/03-...txt`](./raw/03-huong-dan-lap-can-doi-ke-toan-thu-cong.txt) |
| **04** | **Hướng Dẫn Lập Cân Đối Kế Toán Dùng Công Thức**<br>*Tự động hóa lập báo cáo cân đối kế toán trên bảng tính thông qua hàm và công thức.* | 23:25 | 211 | [`markdown/04-...md`](./markdown/04-huong-dan-lap-can-doi-ke-toan-dung-cong-thuc.md) | [`raw/04-...txt`](./raw/04-huong-dan-lap-can-doi-ke-toan-dung-cong-thuc.txt) |
| **05** | **Hướng Dẫn Lập Báo Cáo Kết Quả Kinh Doanh**<br>*Kỹ thuật hạch toán doanh thu, giá vốn, chi phí bán hàng, chi phí quản lý doanh nghiệp.* | 19:42 | 165 | [`markdown/05-...md`](./markdown/05-huong-dan-lap-bao-cao-ket-qua-kinh-doanh.md) | [`raw/05-...txt`](./raw/05-huong-dan-lap-bao-cao-ket-qua-kinh-doanh.txt) |
| **06** | **Phương Pháp Phân Tích BCTC**<br>*Các phương pháp phân tích ngang, phân tích dọc và cấu trúc tỷ trọng báo cáo tài chính.* | 25:31 | 229 | [`markdown/06-...md`](./markdown/06-phuong-phap-phan-tich-bctc.md) | [`raw/06-...txt`](./raw/06-phuong-phap-phan-tich-bctc.txt) |
| **07** | **Phân Tích BCTC Và Các Chỉ Số Tài Chính**<br>*Chỉ số thanh khoản, đòn bẩy tài chính, hiệu quả hoạt động và khả năng sinh lời (ROA, ROE).* | 59:02 | 685 | [`markdown/07-...md`](./markdown/07-phan-tich-bctc-va-chi-so-tai-chinh.md) | [`raw/07-...txt`](./raw/07-phan-tich-bctc-va-chi-so-tai-chinh.txt) |
| **08** | **Hướng Dẫn Ứng Dụng Mẫu Phân Tích BCTC**<br>*Thực hành trực tiếp trên file mẫu phân tích BCTC doanh nghiệp niêm yết (case study).* | 31:47 | 334 | [`markdown/08-...md`](./markdown/08-huong-dan-ung-dung-mau-phan-tich-bctc.md) | [`raw/08-...txt`](./raw/08-huong-dan-ung-dung-mau-phan-tich-bctc.txt) |

---

## Hướng Dẫn Sử Dụng
1. **Dành cho người đọc:** Mở trực tiếp các tệp trong thư mục `markdown/`. Các đoạn hội thoại đã được ngắt theo ngữ cảnh (~45s) kèm timestamp `**[mm:ss]**` giúp dễ dàng tra cứu lại vị trí video tương ứng trên Google Drive.
2. **Dành cho AI / RAG / Prompting:** Sử dụng các file Markdown hoặc file Raw TXT để cung cấp context cho LLM khi cần tóm tắt bài giảng, trích xuất công thức, lập bảng phân tích tài chính hoặc tạo câu hỏi đánh giá.
