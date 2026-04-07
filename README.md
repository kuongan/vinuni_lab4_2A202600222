# Lab 4 - TravelBuddy Agent với LangGraph

Dự án này xây dựng một AI Agent tư vấn du lịch bằng LangGraph, có khả năng gọi tool để:
- tìm chuyến bay
- tìm khách sạn theo ngân sách
- tính toán chi phí và ngân sách còn lại

Agent sử dụng system prompt riêng, mock data du lịch, và vòng lặp tool-calling theo graph.

## 1. Cấu trúc thư mục

- agent.py: khởi tạo LLM, tools, LangGraph và chat loop
- tools.py: định nghĩa 3 custom tools + mock data flights/hotels
- system_prompt.txt: persona, rules, constraints, response format
- test_api.py: sanity check OpenAI API
- run_lab_tests.py: chạy bộ test và ghi kết quả
- test_results.md: kết quả test đã chạy
- requirements.txt: danh sách thư viện cần cài

## 2. Yêu cầu môi trường

- Python 3.10+
- OpenAI API key

## 3. Cài đặt

### Windows (PowerShell)

```powershell
python -m venv .venv
\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Mac/Linux

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 4. Cấu hình API key

Tạo file .env trong thư mục gốc với nội dung:

```env
OPENAI_API_KEY=your_openai_api_key_here
```

## 5. Kiểm tra kết nối API

```bash
python test_api.py
```

Nếu in ra được câu trả lời từ model, môi trường đã sẵn sàng.

## 6. Chạy agent

```bash
python agent.py
```

Nhập câu hỏi trong terminal. Để thoát, nhập một trong các lệnh:
- quit
- exit
- q

## 7. Mô tả nhanh về graph

Graph trong agent.py được thiết kế như sau:
- START -> agent
- agent -> tools (nếu model yêu cầu gọi tool)
- tools -> agent (trả kết quả về model để tổng hợp)
- agent -> END (nếu model không gọi tool)

Cách thiết kế này cho phép agent tự quyết định gọi tool bao nhiêu lần trước khi trả lời cuối.

## 8. Mô tả 3 tools

### search_flights(origin, destination)
- tìm chuyến bay theo tuyến
- sắp xếp theo giá tăng dần
- nếu không có chiều đi, thử tìm chiều ngược

### search_hotels(city, max_price_per_night)
- tìm khách sạn theo thành phố
- lọc theo giá tối đa mỗi đêm
- sắp xếp ưu tiên rating giảm dần, sau đó giá tăng dần

### calculate_budget(total_budget, expenses)
- parse chuỗi chi phí dạng ten_khoan:so_tien
- tính tổng chi và ngân sách còn lại
- cảnh báo nếu vượt ngân sách
- xử lý lỗi format đầu vào

## 9. Chạy test và tạo báo cáo

```bash
python run_lab_tests.py
```

Lệnh này sẽ ghi kết quả vào file test_results.md.

## 10. Lưu ý

- Dữ liệu trong tools.py là mock data phục vụ bài lab.
- Agent được hướng dẫn bởi system_prompt.txt, hành vi có thể thay đổi theo model.
- Nếu model trả lời không đúng kỳ vọng test, có thể tiếp tục tinh chỉnh system prompt để ép hành vi tool-calling.
