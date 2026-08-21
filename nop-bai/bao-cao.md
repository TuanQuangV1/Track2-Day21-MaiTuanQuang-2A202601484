# Báo Cáo Lab Day 21 - CI/CD cho AI Systems

| | |
|---|---|
| Họ và tên | Mai Tuấn Quang |
| MSSV | 2A202601484 |
| Lớp / Khóa | K4 |
| Repo GitHub | https://github.com/TuanQuangV1/Track2-Day21-MaiTuanQuang-2A202601484 |
| Ngày nộp | 21/08/2026 |

---

## 1. Bộ Siêu Tham Số Đã Chọn và Lý Do

| Lần chạy | n_estimators | learning_rate | max_depth | f1_score | accuracy |
|---|---|---|---|---|---|
| 1 | 100 | 0.1 | 3 | 0.7109 | 0.8780 |
| 2 | 50 | 0.05 | 2 | 0.6051 | 0.8460 |
| 3 | 200 | 0.1 | 5 | 0.7149 | 0.8740 |

**Bộ siêu tham số đã chọn:** `n_estimators=200`, `learning_rate=0.1`, `max_depth=5`.

**Lý do:** Lần chạy 3 đạt điểm F1 cao nhất trên lớp dương (0.7149), vượt qua ngưỡng chất lượng tối thiểu 0.65 của hệ thống. Đáng chú ý, lần chạy 1 có Accuracy cao hơn lần chạy 3 (0.8780 so với 0.8740) nhưng lại có F1 thấp hơn (0.7109 so với 0.7149), cho thấy Accuracy không phản ánh đúng khả năng phân loại chính xác nhóm thu nhập cao. Khi tăng `n_estimators` và `max_depth`, mô hình GradientBoosting học sâu hơn các mối quan hệ phi tuyến giữa các đặc trưng, giúp cải thiện đáng kể độ nhạy với lớp thiểu số.

---

## 2. Vì Sao Ngưỡng Chất Lượng Đặt Trên F1 Chứ Không Phải Accuracy

Tập dữ liệu Adult có phân bố lớp mất cân bằng nghiêm trọng khi chỉ có khoảng 24.8% số mẫu thuộc lớp thu nhập cao (>50K) và 75.2% thuộc lớp thu nhập thấp. Nếu một mô hình đơn giản luôn đoán nhãn "thu nhập thấp" cho tất cả dữ liệu, Accuracy vẫn đạt tới 75.2% dù mô hình hoàn toàn vô dụng và không phát hiện được bất kỳ người có thu nhập cao nào ($F_1 = 0.0$). 

Chỉ số F1 trên lớp dương kết hợp hài hòa giữa Precision (độ chính xác khi dự đoán thu nhập cao) và Recall (tỷ lệ bắt trúng người thu nhập cao thực tế). Việc không sử dụng `average="macro"` hay `average="weighted"` là bắt buộc, vì các phương pháp này bị lớp đa số (75.2%) chi phối làm sai lệch và che giấu sự yếu kém của mô hình đối với lớp thiểu số.

---

## 3. Khó Khăn Gặp Phải và Cách Giải Quyết

| Khó khăn | Nguyên nhân | Cách giải quyết |
|---|---|---|
| Không có thẻ ngân hàng để tạo Cloud Bucket và VM | Các nền tảng GCP/AWS yêu cầu thẻ quốc tế để xác thực tài khoản | Tích hợp DagsHub cung cấp sẵn Remote DVC S3 và MLflow Tracking Server miễn phí 100% |
| Xung đột phiên bản gói khi cài đặt trên môi trường mới | Các thư viện MLflow, DVC và Scikit-learn có phụ thuộc chéo phức tạp | Tạo môi trường ảo độc lập `.venv` và đồng bộ chính xác phiên bản trong workflow |
| Nguy cơ lộ thông tin xác thực lên kho mã nguồn | DVC và MLflow cần Access Token để kết nối và đẩy dữ liệu | Sử dụng cờ `--local` cho cấu hình DVC và lưu toàn bộ khóa vào GitHub Secrets |

---

## 4. So Sánh Bước 2 và Bước 3

| | f1_score | accuracy |
|---|---|---|
| Bước 2 (chỉ `train_batch1`) | 0.7149 | 0.8740 |
| Bước 3 (thêm `train_batch2`) | 0.7162 | 0.8760 |

**Nhận xét:** Khi bổ sung thêm 22.361 mẫu dữ liệu ở Bước 3, F1-score và Accuracy chỉ tăng nhẹ do hai nửa dữ liệu được trích xuất ngẫu nhiên từ cùng một phân phối nguồn. Điểm mấu chốt được chứng minh ở Bước 3 là tính tự động hóa toàn diện của hệ thống MLOps: chỉ với một commit thay đổi con trỏ dữ liệu DVC, toàn bộ pipeline CI/CD đã tự động kích hoạt, huấn luyện lại và cập nhật mô hình mới lên hệ thống phục vụ.

---

## 5. Phần Bonus Đã Thực Hiện

- [x] Bonus 1 - Tracking MLflow từ xa với DagsHub: Kết nối thành công pipeline GitHub Actions trực tiếp với server MLflow trên DagsHub mà không cần server riêng.
