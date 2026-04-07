from __future__ import annotations

from contextlib import redirect_stderr, redirect_stdout
from datetime import date
import io
import logging

from agent import graph
from tools import calculate_budget, search_flights, search_hotels


def main() -> None:
    lines: list[str] = []
    lines.append("# Test Results - Lab 4 TravelBuddy")
    lines.append("")
    lines.append(f"Ngày: {date.today().isoformat()}")
    lines.append("")

    lines.append("## Tool smoke tests")
    lines.append("")
    lines.append("### search_flights(Hà Nội -> Đà Nẵng)")
    lines.append("```")
    lines.append(search_flights.invoke({"origin": "Hà Nội", "destination": "Đà Nẵng"}))
    lines.append("```")
    lines.append("")

    lines.append("### search_hotels(Phú Quốc, 900000)")
    lines.append("```")
    lines.append(search_hotels.invoke({"city": "Phú Quốc", "max_price_per_night": 900_000}))
    lines.append("```")
    lines.append("")

    lines.append("### calculate_budget(5000000, ve_may_bay + khach_san)")
    lines.append("```")
    lines.append(
        calculate_budget.invoke(
            {
                "total_budget": 5_000_000,
                "expenses": "ve_may_bay:1100000,khach_san:1600000",
            }
        )
    )
    lines.append("```")
    lines.append("")

    tests = [
        ("Test 1 - Direct Answer (Không cần tool)", "Xin chào! Tôi đang muốn đi du lịch nhưng chưa biết đi đâu."),
        ("Test 2 - Single Tool Call", "Tìm giúp tôi chuyến bay từ Hà Nội đi Đà Nẵng"),
        ("Test 3 - Multi-Step Tool Chaining", "Tôi ở Hà Nội, muốn đi Phú Quốc 2 đêm, budget 5 triệu. Tư vấn giúp!"),
        ("Test 4 - Missing Info / Clarification", "Tôi muốn đặt khách sạn"),
        ("Test 5 - Guardrail / Refusal", "Giải giúp tôi bài tập lập trình Python về linked list"),
    ]

    lines.append("## Agent test cases (5 scenarios)")
    lines.append("")

    def run_with_logs(prompt: str) -> tuple[str, str]:
        stdout_buffer = io.StringIO()
        stderr_buffer = io.StringIO()
        log_buffer = io.StringIO()

        handler = logging.StreamHandler(log_buffer)
        handler.setLevel(logging.INFO)
        handler.setFormatter(logging.Formatter("%(levelname)s:%(name)s:%(message)s"))
        root_logger = logging.getLogger()
        root_logger.addHandler(handler)

        try:
            with redirect_stdout(stdout_buffer), redirect_stderr(stderr_buffer):
                result = graph.invoke(
                    {"messages": [("human", prompt)]},
                    config={"recursion_limit": 8},
                )
        finally:
            root_logger.removeHandler(handler)

        final = result["messages"][-1]
        log_text = "".join(
            part for part in [log_buffer.getvalue(), stdout_buffer.getvalue(), stderr_buffer.getvalue()] if part
        ).strip()
        return final.content, log_text

    for title, prompt in tests:
        lines.append(f"### {title}")
        lines.append("```")
        lines.append(f"USER: {prompt}")
        try:
            answer, logs = run_with_logs(prompt)
            lines.append(f"ASSISTANT: {answer}")
            if logs:
                lines.append("LOGS:")
                lines.append(logs)
        except Exception as exc:  # pragma: no cover
            lines.append(f"ERROR: {exc}")
        lines.append("```")
        lines.append("")

    with open("test_results.md", "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print("Wrote test_results.md")


if __name__ == "__main__":
    main()
