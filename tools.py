from __future__ import annotations

import unicodedata

from langchain_core.tools import tool


def format_vnd(amount: int) -> str:
    return f"{amount:,}".replace(",", ".") + "đ"


def parse_money(raw: str) -> int:
    cleaned = raw.strip().replace("_", "").replace(".", "").replace(" ", "")
    if cleaned.endswith("d") or cleaned.endswith("đ"):
        cleaned = cleaned[:-1]
    return int(cleaned)


def strip_accents(value: str) -> str:
    return "".join(
        ch for ch in unicodedata.normalize("NFD", value) if unicodedata.category(ch) != "Mn"
    )


FLIGHTS_DB = {
    ("Hà Nội", "Đà Nẵng"): [
        {"airline": "Vietnam Airlines", "departure": "06:00", "arrival": "07:20", "price": 1_450_000, "class": "economy"},
        {"airline": "Vietnam Airlines", "departure": "14:00", "arrival": "15:20", "price": 2_800_000, "class": "business"},
        {"airline": "VietJet Air", "departure": "08:30", "arrival": "09:50", "price": 890_000, "class": "economy"},
        {"airline": "Bamboo Airways", "departure": "11:00", "arrival": "12:20", "price": 1_200_000, "class": "economy"},
    ],
    ("Hà Nội", "Phú Quốc"): [
        {"airline": "Vietnam Airlines", "departure": "07:00", "arrival": "09:15", "price": 2_100_000, "class": "economy"},
        {"airline": "VietJet Air", "departure": "10:00", "arrival": "12:15", "price": 1_350_000, "class": "economy"},
        {"airline": "VietJet Air", "departure": "16:00", "arrival": "18:15", "price": 1_100_000, "class": "economy"},
    ],
    ("Hà Nội", "Hồ Chí Minh"): [
        {"airline": "Vietnam Airlines", "departure": "06:00", "arrival": "08:10", "price": 1_600_000, "class": "economy"},
        {"airline": "VietJet Air", "departure": "07:30", "arrival": "09:40", "price": 950_000, "class": "economy"},
        {"airline": "Bamboo Airways", "departure": "12:00", "arrival": "14:10", "price": 1_300_000, "class": "economy"},
        {"airline": "Vietnam Airlines", "departure": "18:00", "arrival": "20:10", "price": 3_200_000, "class": "business"},
    ],
    ("Hồ Chí Minh", "Đà Nẵng"): [
        {"airline": "Vietnam Airlines", "departure": "09:00", "arrival": "10:20", "price": 1_300_000, "class": "economy"},
        {"airline": "VietJet Air", "departure": "13:00", "arrival": "14:20", "price": 780_000, "class": "economy"},
    ],
    ("Hồ Chí Minh", "Phú Quốc"): [
        {"airline": "Vietnam Airlines", "departure": "08:00", "arrival": "09:00", "price": 1_100_000, "class": "economy"},
        {"airline": "VietJet Air", "departure": "15:00", "arrival": "16:00", "price": 650_000, "class": "economy"},
    ],
}

HOTELS_DB = {
    "Đà Nẵng": [
        {"name": "Muong Thanh Luxury", "stars": 5, "price_per_night": 1_800_000, "area": "Mỹ Khê", "rating": 4.5},
        {"name": "Sala Danang Beach", "stars": 4, "price_per_night": 1_200_000, "area": "Mỹ Khê", "rating": 4.3},
        {"name": "Fivitel Danang", "stars": 3, "price_per_night": 650_000, "area": "Sơn Trà", "rating": 4.1},
        {"name": "Memory Hostel", "stars": 2, "price_per_night": 250_000, "area": "Hải Châu", "rating": 4.6},
        {"name": "Christina's Homestay", "stars": 2, "price_per_night": 350_000, "area": "An Thượng", "rating": 4.7},
    ],
    "Phú Quốc": [
        {"name": "Vinpearl Resort", "stars": 5, "price_per_night": 3_500_000, "area": "Bãi Dài", "rating": 4.4},
        {"name": "Sol by Melia", "stars": 4, "price_per_night": 1_500_000, "area": "Bãi Trường", "rating": 4.2},
        {"name": "Lahana Resort", "stars": 3, "price_per_night": 800_000, "area": "Dương Đông", "rating": 4.0},
        {"name": "9Station Hostel", "stars": 2, "price_per_night": 200_000, "area": "Dương Đông", "rating": 4.5},
    ],
    "Hồ Chí Minh": [
        {"name": "Rex Hotel", "stars": 5, "price_per_night": 2_800_000, "area": "Quận 1", "rating": 4.3},
        {"name": "Liberty Central", "stars": 4, "price_per_night": 1_400_000, "area": "Quận 1", "rating": 4.1},
        {"name": "Cochin Zen Hotel", "stars": 3, "price_per_night": 550_000, "area": "Quận 3", "rating": 4.4},
        {"name": "The Common Room", "stars": 2, "price_per_night": 180_000, "area": "Quận 1", "rating": 4.6},
    ],
}


def normalize_city(city: str) -> str:
    text = city.strip().lower()
    normalized = strip_accents(text)
    normalized_compact = normalized.replace(" ", "").replace(".", "")

    canonical = ["Hà Nội", "Đà Nẵng", "Phú Quốc", "Hồ Chí Minh"]
    for name in canonical:
        base = strip_accents(name).lower()
        if normalized == base or normalized_compact == base.replace(" ", ""):
            return name

    if normalized_compact in ("hcm", "tphcm"):
        return "Hồ Chí Minh"

    return city.strip()


@tool
def search_flights(origin: str, destination: str) -> str:
    """Tìm kiếm các chuyến bay giữa hai thành phố."""
    try:
        o = normalize_city(origin)
        d = normalize_city(destination)

        direct_key = (o, d)
        reverse_key = (d, o)

        flights = FLIGHTS_DB.get(direct_key)
        if flights:
            sorted_flights = sorted(flights, key=lambda x: x["price"])
            lines = [f"Tìm thấy {len(sorted_flights)} chuyến bay từ {o} đến {d}:"]
            for idx, flight in enumerate(sorted_flights, start=1):
                lines.append(
                    f"{idx}. {flight['airline']} | {flight['departure']}-{flight['arrival']} | "
                    f"{flight['class']} | {format_vnd(flight['price'])}"
                )
            return "\n".join(lines)

        reverse_flights = FLIGHTS_DB.get(reverse_key)
        if reverse_flights:
            sorted_flights = sorted(reverse_flights, key=lambda x: x["price"])
            lines = [
                f"Không tìm thấy chuyến bay trực tiếp từ {o} đến {d}.",
                f"Nhưng có {len(sorted_flights)} chuyến bay chiều ngược từ {d} đến {o}:"
            ]
            for idx, flight in enumerate(sorted_flights, start=1):
                lines.append(
                    f"{idx}. {flight['airline']} | {flight['departure']}-{flight['arrival']} | "
                    f"{flight['class']} | {format_vnd(flight['price'])}"
                )
            return "\n".join(lines)

        return f"Không tìm thấy chuyến bay từ {o} đến {d}."
    except Exception as exc:  # pragma: no cover
        return f"Lỗi không xác định khi tìm chuyến bay: {exc}"


@tool
def search_hotels(city: str, max_price_per_night: int = 9_999_999) -> str:
    """Tìm khách sạn tại một thành phố, có lọc theo giá tối đa mỗi đêm."""
    try:
        c = normalize_city(city)
        hotels = HOTELS_DB.get(c)
        if not hotels:
            return f"Không tìm thấy dữ liệu khách sạn tại {c}."

        filtered = [h for h in hotels if h["price_per_night"] <= max_price_per_night]
        if not filtered:
            return (
                f"Không tìm thấy khách sạn tại {c} với giá dưới {format_vnd(max_price_per_night)}/đêm. "
                "Hãy thử tăng ngân sách."
            )

        ranked = sorted(filtered, key=lambda x: (-x["rating"], x["price_per_night"]))
        lines = [f"Tìm thấy {len(ranked)} khách sạn phù hợp tại {c}:"]
        for idx, hotel in enumerate(ranked, start=1):
            lines.append(
                f"{idx}. {hotel['name']} | {hotel['stars']}* | {hotel['area']} | "
                f"rating {hotel['rating']} | {format_vnd(hotel['price_per_night'])}/đêm"
            )
        return "\n".join(lines)
    except Exception as exc:  # pragma: no cover
        return f"Lỗi không xác định khi tìm khách sạn: {exc}"


@tool
def calculate_budget(total_budget: int, expenses: str) -> str:
    """Tính ngân sách còn lại sau khi trừ các khoản chi phí."""
    try:
        if not expenses.strip():
            return "Lỗi: expenses không được để trống. Định dạng đúng: ten_khoan:so_tien,ten_khoan:so_tien"

        details: dict[str, int] = {}
        for chunk in expenses.split(","):
            item = chunk.strip()
            if not item:
                continue
            if ":" not in item:
                return f"Lỗi định dạng: '{item}'. Vui lòng dùng mẫu ten_khoan:so_tien"

            name, amount_str = item.split(":", 1)
            name = name.strip()
            if not name:
                return "Lỗi định dạng: tên khoản chi không được để trống."
            amount = parse_money(amount_str)
            if amount < 0:
                return f"Lỗi: số tiền cho '{name}' phải >= 0."
            details[name] = details.get(name, 0) + amount

        total_expense = sum(details.values())
        remaining = total_budget - total_expense

        lines = ["Bảng chi phí:"]
        for name, amount in details.items():
            lines.append(f"- {name}: {format_vnd(amount)}")
        lines.append("---")
        lines.append(f"Tổng chi: {format_vnd(total_expense)}")
        lines.append(f"Ngân sách: {format_vnd(total_budget)}")
        lines.append(f"Còn lại: {format_vnd(remaining)}")

        if remaining < 0:
            lines.append(f"Cảnh báo: Vượt ngân sách {format_vnd(abs(remaining))}! Cần điều chỉnh.")

        return "\n".join(lines)
    except ValueError as exc:
        return f"Lỗi parse chi phí: {exc}. Vui lòng dùng số nguyên, VD: ve_may_bay:890000"
    except Exception as exc:  # pragma: no cover
        return f"Lỗi không xác định khi tính ngân sách: {exc}"
