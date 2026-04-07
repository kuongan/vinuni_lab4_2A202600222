# Test Results - Lab 4 TravelBuddy

Ngày: 2026-04-07

## Tool smoke tests

### search_flights(Hà Nội -> Đà Nẵng)
```
Tìm thấy 4 chuyến bay từ Hà Nội đến Đà Nẵng:
1. VietJet Air | 08:30-09:50 | economy | 890.000đ
2. Bamboo Airways | 11:00-12:20 | economy | 1.200.000đ
3. Vietnam Airlines | 06:00-07:20 | economy | 1.450.000đ
4. Vietnam Airlines | 14:00-15:20 | business | 2.800.000đ
```

### search_hotels(Phú Quốc, 900000)
```
Tìm thấy 2 khách sạn phù hợp tại Phú Quốc:
1. 9Station Hostel | 2* | Dương Đông | rating 4.5 | 200.000đ/đêm
2. Lahana Resort | 3* | Dương Đông | rating 4.0 | 800.000đ/đêm
```

### calculate_budget(5000000, ve_may_bay + khach_san)
```
Bảng chi phí:
- ve_may_bay: 1.100.000đ
- khach_san: 1.600.000đ
---
Tổng chi: 2.700.000đ
Ngân sách: 5.000.000đ
Còn lại: 2.300.000đ
```

## Agent test cases (5 scenarios)

### Test 1 - Direct Answer (Không cần tool)
```
USER: Xin chào! Tôi đang muốn đi du lịch nhưng chưa biết đi đâu.
ASSISTANT: Xin chào bạn! Rất vui được trò chuyện với bạn về kế hoạch đi du lịch. Bạn có thích một điểm đến nào đó trong nước hay quốc tế? Hoặc bạn có thể cho biết những sở thích, hoạt động bạn muốn trải nghiệm trong chuyến đi này không?
LOGS:
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO:agent:MODEL trả lời trực tiếp (không gọi tool)
```

### Test 2 - Single Tool Call
```
USER: Tìm giúp tôi chuyến bay từ Hà Nội đi Đà Nẵng
ASSISTANT: Dưới đây là thông tin về các chuyến bay từ Hà Nội đi Đà Nẵng:

1. **VietJet Air** 
   - Giờ bay: 08:30 - 09:50
   - Hạng ghế: Economy
   - Giá: 890.000đ

2. **Bamboo Airways**
   - Giờ bay: 11:00 - 12:20
   - Hạng ghế: Economy
   - Giá: 1.200.000đ

3. **Vietnam Airlines**
   - Giờ bay: 06:00 - 07:20
   - Hạng ghế: Economy
   - Giá: 1.450.000đ

4. **Vietnam Airlines**
   - Giờ bay: 14:00 - 15:20
   - Hạng ghế: Business
   - Giá: 2.800.000đ

Nếu bạn cần hỗ trợ thêm gì khác như đặt vé hay thông tin về khách sạn, hãy cho mình biết nhé!
LOGS:
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO:agent:TOOL CALL search_flights({'origin': 'Hà Nội', 'destination': 'Đà Nẵng'})
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO:agent:MODEL trả lời trực tiếp (không gọi tool)
```

### Test 3 - Multi-Step Tool Chaining
```
USER: Tôi ở Hà Nội, muốn đi Phú Quốc 2 đêm, budget 5 triệu. Tư vấn giúp!
ASSISTANT: Dưới đây là kế hoạch cho chuyến đi của bạn từ Hà Nội tới Phú Quốc trong 2 đêm:

**Chuyến bay:**
- VietJet Air | 16:00-18:15 | Giá: 1.100.000đ

**Khách sạn:**
- Sol by Melia | 4* | Bãi Trường | Rating 4.2 | Giá: 1.500.000đ/đêm
- Tổng giá cho 2 đêm: 3.000.000đ

**Tổng chi phí ước tính:**
- Vé máy bay: 1.100.000đ
- Khách sạn: 3.000.000đ
- **Tổng cộng:** 4.100.000đ
- **Còn lại:** 900.000đ

**Gợi ý thêm:**
- Với số tiền còn lại 900.000đ, bạn có thể thưởng thức món ăn ngon, tham quan các địa điểm nổi tiếng hoặc mua sắm tại Phú Quốc. Hãy nhớ kiểm tra thời tiết và chuẩn bị đồ mang theo nhé!

Nếu bạn cần thêm thông tin hoặc hỗ trợ khác, cứ cho tôi biết nhé!
LOGS:
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO:agent:TOOL CALL search_flights({'origin': 'Hà Nội', 'destination': 'Phú Quốc'})
INFO:agent:TOOL CALL calculate_budget({'total_budget': 5000000, 'expenses': 've_may_bay:0,khach_san:0'})
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO:agent:TOOL CALL search_hotels({'city': 'Phú Quốc', 'max_price_per_night': 1900000})
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO:agent:TOOL CALL calculate_budget({'total_budget': 5000000, 'expenses': 've_may_bay:1100000,khach_san:3000000'})
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO:agent:MODEL trả lời trực tiếp (không gọi tool)
```

### Test 4 - Missing Info / Clarification
```
USER: Tôi muốn đặt khách sạn
ASSISTANT: Chào bạn! Để mình có thể giúp bạn đặt khách sạn tốt nhất, bạn vui lòng cho mình biết một số thông tin như:

1. Điểm đến là thành phố nào?
2. Ngân sách tối đa cho mỗi đêm là bao nhiêu?
3. Bạn có muốn ở trong bao nhiêu đêm không?

Khi có những thông tin này, mình sẽ tìm giúp bạn khách sạn phù hợp!
LOGS:
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO:agent:MODEL trả lời trực tiếp (không gọi tool)
```

### Test 5 - Guardrail / Refusal
```
USER: Giải giúp tôi bài tập lập trình Python về linked list
ASSISTANT: Xin lỗi, nhưng mình không thể giúp bạn với bài tập lập trình. Nếu bạn cần hỗ trợ về du lịch hoặc đặt phòng, hãy cho mình biết!
LOGS:
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO:agent:MODEL trả lời trực tiếp (không gọi tool)
```
